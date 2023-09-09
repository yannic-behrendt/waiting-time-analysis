import pm4py
import pandas
import plotly.graph_objects.layout.Yaxis
import plotly.graph_objects as go
import statistics
from collections import defaultdict
from pm4py.objects.log.util import interval_lifecycle
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils
import plotly.graph_objects as go
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback, Output, Input


# Create a Sankey diagram trace
trace = go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=["A", "B", "C", "D", "E"],
    ),
    link=dict(
        source=[0, 1, 0, 2, 3, 3],
        target=[2, 3, 3, 4, 4, 5],
        value=[8, 4, 2, 8, 4, 2],
    ),
)

fig = make_subplots(rows=1, cols=1)
fig.add_trace(trace)

# Define a callback function to handle hover events
def on_hover(trace, points, state):
    print("HHHHHHHHHHHHHHHH")

    if points.point_inds:
        value = trace.link.value[points.point_inds[0]]
        print(f"Hovered Value: {value}")

# Add the on_hover callback to the Sankey trace
fig.data[0].on_hover(on_hover)

# Show the plot
fig.show()

html.Textarea
html.Plaintext

def generate_scatter(s_t, values):
  if s_t == None or values == None: return {} 

  source = s_t[0]
  target = s_t[1]
  y_axis = values['waiting_times']
  x_axis = [i for i in range(len(y_axis))]

  return {
            'data': [go.Scatter(
               x=x_axis, 
               y=y_axis, 
               mode='markers', 
               name=f'Waiting Times for {source} -> {target}')],
            'layout': go.Layout(
               title=f'Waiting Times {source} -> {target}',
               yaxis=dict(
                  
               )
               
               ),
            
        }

