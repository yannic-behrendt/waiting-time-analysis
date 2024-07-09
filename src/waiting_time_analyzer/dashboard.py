import dash
from dash import html, dcc, callback, Output, Input

from graph_generator import generate_histogram, generate_sankey, generate_reasons_bar_chart, generate_box_chart
from src.waiting_time_analyzer.config import Metrics, Notions
from src.waiting_time_analyzer.waiting_times_helper import filter_performance_data_for_transition, compute_waiting_times_metric


def generate_and_serve_dashboard(transitions, performance_data):
    app = dash.Dash(__name__)

    sankey_div = html.Div([dcc.Graph(id='sankey-plot')], style={'padding': '20px'})

    # Filter div with 33% width
    filter_div = html.Div(
        children=[
            dcc.Dropdown(
                id='metric-dropdown',
                options=[{'label': metric.name.capitalize(), 'value': metric.value} for metric in Metrics],
                value=Metrics.MEDIAN.value,
            ),
            dcc.Dropdown(
                id='notion-selector',
                options=[{'label': notion.name.capitalize(), 'value': notion.value} for notion in Notions],
                value=Notions.CONTROL_FLOW.value,
            ),
            dcc.Checklist(
                id='global-color-scale',
                options=[{'label': 'Use global color scale', 'value': True}],
                value=[]
            ),
        ],
        style={'width': '33%', 'padding': '20px'}
    )

    # Details div with children having even spacing horizontally
    details_div = html.Div([
        html.Div([
            html.Div([html.Plaintext(id='hover-transition', children="Hover over a Sankey element to see details:")],
                     style={'font-size': '24pt',
                            'width': '100%',
                            'text-align': 'center',
                            'margin-x': 'auto'})
        ]),

        html.Div([
            html.Div([dcc.Graph(id='box-chart', figure={})], style={'flex': 4}),
        ], style={'display': 'flex', 'width': '100%'}),

        html.Div([
            html.Div([dcc.Graph(id='hist-plot', figure={})], style={'flex': 3}),
            html.Div([dcc.Graph(id='reasons-plot', figure={})], style={'flex': 1}),
        ], style={'display': 'flex', 'width': '100%'})
    ], style={'display': 'flex', 'flex-direction': 'column', 'width': '100%'})

    # Overall layout
    app.layout = html.Div(
        style={'backgroundColor': 'white', 'zoom': '100%'},
        children=[
            filter_div,
            sankey_div,
            details_div,
        ]
    )

    @callback(
        Output('box-chart', 'figure'),
        Output('hist-plot', 'figure'),
        Output('reasons-plot', 'figure'),
        Output('hover-transition', 'children'),
        Input('sankey-plot', 'hoverData'),
        Input('global-color-scale', 'value'),
        Input('notion-selector', 'value')
    )
    def update_details(hover_data, color_scale_global, notion):
        transition = get_transition_from_hover_data(transitions, hover_data)
        filtered_performance_data = filter_performance_data_for_transition(performance_data, transition)
        waiting_times = filtered_performance_data[notion]

        help_text = 'Hover over a node to see info for that node' if transition is None else f'{transition[0]} --> {transition[1]}'
        color_scale_global = (waiting_times.min(), waiting_times.max()) if color_scale_global else color_scale_global

        return (generate_box_chart(waiting_times, color_scale_global),
                generate_histogram(waiting_times, color_scale_global),
                generate_reasons_bar_chart(filtered_performance_data),
                help_text)

    @callback(
        Output('sankey-plot', 'figure'),
        Input('metric-dropdown', 'value'),
        Input('global-color-scale', 'value'),
        Input('notion-selector', 'value')
    )
    def update_sankey(metric: Metrics, color_scale_global, notion):
        waiting_times_metric_by_transition = []

        for transition in transitions:
            filtered_data = filter_performance_data_for_transition(performance_data, transition)
            waiting_times_metric = compute_waiting_times_metric(filtered_data, metric, notion)
            waiting_times_metric_by_transition.append(waiting_times_metric)

        color_scale_global = (performance_data[notion].min(),
                              performance_data[notion].max()) if color_scale_global else color_scale_global

        return generate_sankey(transitions, waiting_times_metric_by_transition, color_scale_global)

    app.run_server()


def get_transition_from_hover_data(transitions, hover_data):
    source, target = zip(*transitions)
    if hover_data is None:
        return
    if 'group' in hover_data['points'][0]: return
    idx = hover_data['points'][0]['index']
    return source[idx], target[idx]
