# import dash
# from dash import dcc, html
# import dash.dependencies as dd
# import plotly.express as px
# import pandas as pd

# # Load the dataset
# file_path = './pum.xlsx'
# data_df = pd.read_excel(file_path, sheet_name='data')

# # Initialize the Dash app
# app = dash.Dash(__name__)

# # Define layout
# app.layout = html.Div([
#     html.H1("Shipment Data Dashboard"),
    
#     # Dropdown for selecting the column to plot
#     dcc.Dropdown(
#         id='column-dropdown',
#         options=[{'label': col, 'value': col} for col in data_df.columns],
#         value=data_df.columns[0],  # Default value to the first column
#         clearable=False
#     ),
    
#     # Graphs to display the plots
#     html.Div(id='graphs-container')
# ])

# # Callback to update the graphs based on selected column
# @app.callback(
#     dd.Output('graphs-container', 'children'),
#     [dd.Input('column-dropdown', 'value')]
# )
# def update_graphs(selected_column):
#     graphs = []

#     if data_df[selected_column].dtype in ['int64', 'float64']:
#         # Numerical column graphs
#         hist_fig = px.histogram(data_df, x=selected_column, title=f'Histogram of {selected_column}')
#         box_fig = px.box(data_df, y=selected_column, title=f'Box Plot of {selected_column}')
#         violin_fig = px.violin(data_df, y=selected_column, title=f'Violin Plot of {selected_column}')
#         density_fig = px.density_contour(data_df, x=selected_column, title=f'Density Plot of {selected_column}')
        
#         graphs.extend([
#             dcc.Graph(figure=hist_fig),
#             dcc.Graph(figure=box_fig),
#             dcc.Graph(figure=violin_fig),
#             dcc.Graph(figure=density_fig)
#         ])
        
#     else:
#         # Categorical column graphs
#         bar_fig = px.bar(data_df[selected_column].value_counts().reset_index(),
#                          x='index', y=selected_column,
#                          title=f'Bar Chart of {selected_column}',
#                          labels={'index': selected_column, selected_column: 'Count'})
#         pie_fig = px.pie(data_df, names=selected_column, title=f'Pie Chart of {selected_column}')
#         heatmap_fig = px.density_heatmap(data_df, y=selected_column, title=f'Heatmap of {selected_column}')
        
#         graphs.extend([
#             dcc.Graph(figure=bar_fig),
#             dcc.Graph(figure=pie_fig),
#             dcc.Graph(figure=heatmap_fig)
#         ])
    
#     return graphs

# # Run the app
# if __name__ == '__main__':
#     app.run_server(debug=True)

import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.express as px
import pandas as pd

# Load the dataset
file_path = './pum.xlsx'
data_df = pd.read_excel(file_path, sheet_name='data')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.H1("Shipment Data Dashboard"),
    
    # Dropdown for selecting the column to plot
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in data_df.columns],
        value=data_df.columns[0],  # Default value to the first column
        clearable=False
    ),
    
    # Container for the data summary
    html.Div(id='data-summary', style={'margin-top': '20px', 'margin-bottom': '20px'}),
    
    # Graphs to display the plots
    html.Div(id='graphs-container')
])

# Callback to update the data summary and graphs based on selected column
@app.callback(
    [dd.Output('data-summary', 'children'),
     dd.Output('graphs-container', 'children')],
    [dd.Input('column-dropdown', 'value')]
)
def update_graphs(selected_column):
    total_data_points = len(data_df[selected_column])
    null_ratio = data_df[selected_column].isnull().mean()
    
    summary = html.Div([
        html.P(f"Total Data Points: {total_data_points}"),
        html.P(f"Ratio of Null Values: {null_ratio:.2%}")
    ])
    
    graphs = []

    if data_df[selected_column].dtype in ['int64', 'float64']:
        # Numerical column graphs
        hist_fig = px.histogram(data_df, x=selected_column, title=f'Histogram of {selected_column}')
        box_fig = px.box(data_df, y=selected_column, title=f'Box Plot of {selected_column}')
        violin_fig = px.violin(data_df, y=selected_column, title=f'Violin Plot of {selected_column}')
        density_fig = px.density_contour(data_df, x=selected_column, title=f'Density Plot of {selected_column}')
        
        graphs.extend([
            dcc.Graph(figure=hist_fig),
            dcc.Graph(figure=box_fig),
            dcc.Graph(figure=violin_fig),
            dcc.Graph(figure=density_fig)
        ])
        
    else:
        # Categorical column graphs
        bar_fig = px.bar(data_df[selected_column].value_counts().reset_index(),
                        x='index', y=selected_column,
                        title=f'Bar Chart of {selected_column}',
                        labels={'index': selected_column, selected_column: 'Count'})
        pie_fig = px.pie(data_df, names=selected_column, title=f'Pie Chart of {selected_column}')
        heatmap_fig = px.density_heatmap(data_df, y=selected_column, title=f'Heatmap of {selected_column}')
        
        graphs.extend([
            dcc.Graph(figure=bar_fig),
            dcc.Graph(figure=pie_fig),
            dcc.Graph(figure=heatmap_fig)
        ])
    
    return summary, graphs

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
