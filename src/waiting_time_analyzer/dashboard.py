import dash
from dash import html, dcc, callback, Output, Input

from graph_generator import get_transition_from_hover_data, \
    generate_histogram, generate_sankey, generate_reasons_bar_chart, generate_box_chart, get_all_waiting_times_as_list, \
    get_performance_data_for, get_waiting_times_for, compute_waiting_times_for
from src.waiting_time_analyzer import config


def generate_and_serve_dashboard(transitions, performance_data):
    app = dash.Dash(__name__)

    sankey_div = html.Div([dcc.Graph(id='sankey-plot')], style={'padding': '20px'})

    # Filter div with 33% width
    filter_div = html.Div(
        children=[
            dcc.Dropdown(
                id='metric-dropdown',
                options=[{'label': metric.name.capitalize(), 'value': metric.value} for metric in config.Metrics],
                value='median',
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
        Input('global-color-scale', 'value')
    )
    def update_details(hover_data, color_scale_global):
        _performance_data = performance_data
        transition = get_transition_from_hover_data(transitions, hover_data)

        if transition is not None:
            _performance_data = get_performance_data_for(transition, _performance_data)
            help_text = f'{transition[0]} --> {transition[1]}'
        else:
            help_text = 'Hover over a node to see info for that node'

        waiting_times = get_all_waiting_times_as_list(_performance_data)

        if color_scale_global:
            color_scale_global = (min(get_all_waiting_times_as_list(performance_data)),
                                  max(get_all_waiting_times_as_list(performance_data)))

        return (generate_box_chart(waiting_times, color_scale_global),
                generate_histogram(waiting_times, color_scale_global),
                generate_reasons_bar_chart(_performance_data),
                help_text
                )

    # Filter Sankey
    @callback(
        Output('sankey-plot', 'figure'),
        Input('metric-dropdown', 'value'),
        Input('global-color-scale', 'value')
    )
    def update_sankey(metric, color_scale_global):
        waiting_times = [get_waiting_times_for(transition, performance_data) for transition in transitions]
        waiting_times = compute_waiting_times_for(waiting_times, metric)

        print(len(waiting_times))

        if color_scale_global:
            color_scale_global = (min(get_all_waiting_times_as_list(performance_data)),
                                  max(get_all_waiting_times_as_list(performance_data)))

        return generate_sankey(transitions, waiting_times, color_scale_global)

    app.run_server()
