import dash
from dash import html, dcc, callback, Output, Input

from graph_generator import seconds_to_dhms_string, get_transition_from_hover_data, generate_scatter, \
    generate_histogram, generate_sankey, generate_reasons_bar_chart, generate_box_chart

from src.waiting_time_analyzer import config


def generate_and_serve_dashboard(metrics, transitions, reasons):

    app = dash.Dash(__name__)

    sankey_div = html.Div([dcc.Graph(id='sankey-plot')], style={'padding': '20px'})

    # Filter div with 33% width
    filter_div = html.Div(
        children=[
            dcc.Dropdown(
                id='metric-dropdown',
                options=[{'label': key, 'value': key} for key in metrics.keys()],
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
        html.Div([dcc.Graph(id='box-chart', figure={})], style={'flex': 1}),
        html.Div([dcc.Graph(id='scatter-plot', figure={})], style={'flex': 1}),
        html.Div([dcc.Graph(id='hist-plot', figure={})], style={'flex': 1}),
        html.Div([dcc.Graph(id='reasons-plot', figure={})], style={'flex': 1})
    ], style={'display': 'flex', 'flex-wrap': 'wrap'})

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
        Output('scatter-plot', 'figure'),
        Output('hist-plot', 'figure'),
        Output('reasons-plot', 'figure'),
        Input('sankey-plot', 'hoverData'),
        Input('global-color-scale', 'value')
    )
    def update_details(hover_data, color_scale_global):
        transition = get_transition_from_hover_data(transitions, hover_data)

        if transition is None:
            return {}, {}, {}, {}

        if color_scale_global:
            color_scale_global = (min(metrics['min']), max(metrics['max']))

        return (generate_box_chart(transitions[transition]),
                generate_scatter(transition, transitions[transition], color_scale_global),
                generate_histogram(transition, transitions, color_scale_global),
                generate_reasons_bar_chart(transition, reasons)
                )

    # Filter Sankey
    @callback(
        Output('sankey-plot', 'figure'),
        Input('metric-dropdown', 'value'),
        Input('global-color-scale', 'value')
    )
    def update_sankey(metric, color_scale_global):

        if color_scale_global:
            color_scale_global = (min(metrics['min']), max(metrics['max']))

        return generate_sankey(metric, metrics, transitions, color_scale_global)

    app.run_server()
