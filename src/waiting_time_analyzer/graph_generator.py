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


def generate_scatter(node, node_metrics, color_scale_global):
    if node is None or node_metrics is None:
        return {'layout': go.Layout(title=f'Hover over Link for information')}

    y_axis = node_metrics[config.WAITING]
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
            title='Scattergram of waiting times',
            yaxis=dict(
                title='Duration',
                tickvals=y_ticks,
                ticktext=[seconds_to_dhms_string(s) for s in y_ticks]
            )
        ),
    }


def generate_reasons_bar_chart(transition, performance):
    performance = performance[
        (performance['source_activity'] == transition[0]) & (performance['destination_activity'] == transition[1])]

    wt_total = performance['wt_total'].sum()
    wt_contention = performance['wt_contention'].sum()
    wt_batching = performance['wt_batching'].sum()
    wt_prio = performance['wt_prioritization'].sum()
    wt_unavailability = performance['wt_unavailability'].sum()
    wt_extraneous = performance['wt_extraneous'].sum()

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
        hovertemplate=seconds_to_dhms_string(wt_contention),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_prio],
        name='Prioritization',
        hovertemplate=seconds_to_dhms_string(wt_contention),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_unavailability],
        name='Unavailability',
        hovertemplate=seconds_to_dhms_string(wt_contention),
    ))

    fig.add_trace(go.Bar(
        x=categories,
        y=[wt_extraneous],
        name='Extraneous',
        hovertemplate=seconds_to_dhms_string(wt_contention),
    ))

    # Define custom tick values and labels

    tickvals = list(range(0, int(wt_total) + 1, int(wt_total // 10)))
    ticktext = [seconds_to_dhms_string(s) for s in tickvals]

    # Update layout to stack bars and customize y-axis
    fig.update_layout(
        barmode='stack',
        title='Reasons for Waiting',
        xaxis_title='Category',
        yaxis_title='Total Waiting Time',
        yaxis=dict(
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext
        )
    )

    return fig

def generate_histogram(node, transitions, color_scale_global):
    data = transitions[node][config.WAITING]
    data = [int(v) for v in data]

    unique_values, value_counts = np.unique(data, return_counts=True)
    x_ticks = select_custom_tickvals(data, math.floor(len(unique_values) / 10))

    trace = go.Histogram(
        x=data,
        nbinsx=len(unique_values),
        opacity=0.7,
        marker=dict(color=get_colors(unique_values, color_scale_global)),
    )

    layout = go.Layout(
        title='Histogram of waiting times',
        xaxis=dict(
            title='Waiting Time',
            tickvals=x_ticks,
            ticktext=[seconds_to_dhms_string(s) for s in x_ticks]
        ),
        yaxis=dict(title='Frequency'),
        bargap=0.05
    )
    return go.Figure(data=[trace], layout=layout)


def generate_sankey(metric_name, metrics, transitions, color_scale_global=False):
    source, target = zip(*transitions.keys())
    node_labels = list(set(source + target))
    source_nodes = [node_labels.index(transition[0]) for transition in transitions.keys()]
    target_nodes = [node_labels.index(transition[1]) for transition in transitions.keys()]

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
            value=metrics[metric_name],
            color=get_colors(metrics[metric_name], color_scale_global),
            customdata=[seconds_to_dhms_string(v) for v in metrics[metric_name]],
            hovertemplate=metric_name + ": %{customdata}"
        )))


def get_sorce_target_from_hover_data(transitions, hover_data):
    source, target = zip(*transitions.keys())
    if hover_data is None:
        return
    if 'group' in hover_data['points'][0]: return
    idx = hover_data['points'][0]['index']
    return source[idx], target[idx]
