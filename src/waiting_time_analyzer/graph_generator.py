import math

from src.waiting_time_analyzer import config
import numpy as np
import plotly.graph_objects as go


def seconds_to_dhms_string(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    _days = "" if round(days) == 0 else f"{int(days)}d"
    _hours = "" if round(hours) == 0 else f"{int(hours)}h"
    _minutes = "" if round(minutes) == 0 else f"{int(minutes)}m"
    _seconds = "" if round(seconds) == 0 and (
            round(minutes) != 0 or round(hours) != 0 or round(days) != 0) else f"{int(seconds)}s"

    return f"{_days} {_hours} {_minutes} {_seconds}"


def select_custom_tickvals(data, num_ticks=5):
    # Calculate the minimum and maximum values in the data
    min_val = min(data)
    max_val = max(data)

    if min_val == max_val: return data

    # Calculate the tick interval to achieve even spacing
    tick_interval = (max_val - min_val) / (num_ticks - 1)

    # Calculate custom tick values with even spacing
    custom_tickvals = np.arange(min_val, max_val + tick_interval, tick_interval)

    return custom_tickvals.tolist()


def get_colors(values, global_scale):
    min_value = min(values)
    max_value = max(values)

    if global_scale:
        min_value = global_scale[0]
        max_value = global_scale[1]

    return [get_color(value, min_value, max_value) for value in values]


def get_color(value, min_value, max_value):
    if max_value == min_value:
        normalized_value = 1
    else:
        normalized_value = (value - min_value) / (max_value - min_value)

    hue = 120 - int(120 * normalized_value)  # Hue from 120 (green) to 0 (red)
    saturation = 50  # Reduced saturation for subdued colors
    lightness = 50  # Medium lightness for a pastel effect
    return f'hsl({hue}, {saturation}%, {lightness}%)'


def generate_scatter(waiting_times, color_scale_global):
    y_axis = waiting_times
    x_axis = [i for i in range(len(y_axis))]

    y_ticks = select_custom_tickvals(y_axis)

    return {
        'data': [go.Scatter(
            x=x_axis,
            y=y_axis,
            mode='markers',
            marker=dict(color=get_colors(y_axis, color_scale_global))
        )],
        'layout': go.Layout(
            yaxis=dict(
                title='Duration',
                tickvals=y_ticks,
                ticktext=[seconds_to_dhms_string(s) for s in y_ticks]
            )
        ),
    }


def generate_box_chart(waiting_times, color_scale_global):
    hover_text = [seconds_to_dhms_string(time) for time in waiting_times]

    unique_values, value_counts = np.unique(waiting_times, return_counts=True)
    x_ticks = select_custom_tickvals(waiting_times, math.floor(len(unique_values) / 33))

    fig = go.Figure()

    fig.add_trace(go.Box(
        name='',
        x=waiting_times,
        boxpoints=False,
        hovertemplate=hover_text,
        showlegend=False
    )
    )
    fig.add_trace(go.Scatter(
        name='',
        x=waiting_times,
        y=[1] * len(waiting_times),
        mode='markers',
        marker=dict(color=get_colors(waiting_times, color_scale_global)),
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        yaxis_title='Distribution',
        xaxis=dict(
            title='Waiting Time',
            tickvals=x_ticks,
            ticktext=[seconds_to_dhms_string(s) for s in x_ticks]
        )
    )
    return fig


def generate_reasons_bar_chart(performance_data):
    wt_total = performance_data[config.TOTAL].sum()
    wt_contention = performance_data[config.CONTENTION].sum()
    wt_batching = performance_data[config.BATCHING].sum()
    wt_prio = performance_data[config.PRIO].sum()
    wt_unavailability = performance_data[config.UNAVAILABILITY].sum()
    wt_extraneous = performance_data[config.EXTRANEOUS].sum()

    categories = ['Wait Time Reasons']

    fig = go.Figure()

    # Add each value as a separate trace
    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_contention],
        name='Resource Contention',
        hovertemplate=seconds_to_dhms_string(wt_contention),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_batching],
        name='Batching',
        hovertemplate=seconds_to_dhms_string(wt_batching),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_prio],
        name='Prioritization',
        hovertemplate=seconds_to_dhms_string(wt_prio),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_unavailability],
        name='Unavailability',
        hovertemplate=seconds_to_dhms_string(wt_unavailability),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_extraneous],
        name='Extraneous',
        hovertemplate=seconds_to_dhms_string(wt_extraneous),
    ))

    # Define custom tick values and labels
    tickvals = [wt_contention,
                wt_contention + wt_batching,
                wt_contention + wt_batching + wt_prio,
                wt_contention + wt_batching + wt_prio + wt_unavailability,
                wt_contention + wt_batching + wt_prio + wt_unavailability + wt_extraneous,
                wt_total]
    ticktext = [seconds_to_dhms_string(s) for s in tickvals]

    fig.update_layout(
        barmode='stack',
        yaxis_title='Total Waiting Time',
        yaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        )
    )

    return fig


def generate_histogram(waiting_times, color_scale_global):
    waiting_times = [int(v) for v in waiting_times]

    unique_values, value_counts = np.unique(waiting_times, return_counts=True)
    x_ticks = select_custom_tickvals(waiting_times, math.floor(len(unique_values) / 33))

    trace = go.Histogram(
        x=waiting_times,
        nbinsx=len(unique_values),
        opacity=0.7,
        marker=dict(color=get_colors(unique_values, color_scale_global)),
    )

    layout = go.Layout(
        xaxis=dict(
            title='Waiting Time',
            tickvals=x_ticks,
            ticktext=[seconds_to_dhms_string(s) for s in x_ticks]
        ),
        yaxis=dict(title='Frequency'),
        bargap=0.05
    )
    return go.Figure(data=[trace], layout=layout)


def generate_sankey(transitions, waiting_times, color_scale_global=False):
    source, target = zip(*transitions)
    node_labels = list(set(source + target))
    source_nodes = [node_labels.index(transition[0]) for transition in transitions]
    target_nodes = [node_labels.index(transition[1]) for transition in transitions]

    return go.Figure(go.Sankey(
        arrangement="snap",
        valuesuffix="s",

        node=dict(
            pad=50,
            thickness=10,
            line=dict(width=0),
            label=node_labels,
        ),
        link=dict(
            source=source_nodes,
            target=target_nodes,
            value=waiting_times,
            color=get_colors(waiting_times, color_scale_global),
            customdata=[seconds_to_dhms_string(v) for v in waiting_times],
            hovertemplate="waiting_time: %{customdata}"
        )))