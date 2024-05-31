import dash
from dash import dcc, html
import dash.dependencies as dd
import plotly.express as px
import pandas as pd
import numpy as np

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
    
    # Graph to display the plot
    dcc.Graph(id='data-plot')
])

# Function to select the best possible graph
def select_best_graph(data_df, column):
    if data_df[column].dtype in ['int64', 'float64']:
        # For numerical columns
        unique_values = data_df[column].nunique()
        skewness = data_df[column].skew()
        if unique_values < 10:
            return px.bar(data_df[column].value_counts().reset_index(),
                          x='index', y=column,
                          title=f'Bar Chart of {column}',
                          labels={'index': column, column: 'Count'})
        elif skewness > 1 or skewness < -1:
            return px.box(data_df, y=column, title=f'Box Plot of {column}')
        elif unique_values > 10 and unique_values < 100:
            return px.histogram(data_df, x=column, title=f'Histogram of {column}')
        else:
            return px.violin(data_df, y=column, title=f'Violin Plot of {column}')
    else:
        # For categorical columns
        unique_values = data_df[column].nunique()
        if unique_values < 10:
            return px.pie(data_df, names=column, title=f'Pie Chart of {column}')
        else:
            return px.bar(data_df[column].value_counts().reset_index(),
                          x='index', y=column,
                          title=f'Bar Chart of {column}',
                          labels={'index': column, column: 'Count'})

# Callback to update the data summary and graph based on selected column
@app.callback(
    [dd.Output('data-summary', 'children'),
     dd.Output('data-plot', 'figure')],
    [dd.Input('column-dropdown', 'value')]
)
def update_graph(selected_column):
    total_data_points = len(data_df[selected_column])
    null_ratio = data_df[selected_column].isnull().mean()
    
    summary = html.Div([
        html.P(f"Total Data Points: {total_data_points}"),
        html.P(f"Ratio of Null Values: {null_ratio:.2%}")
    ])
    
    fig = select_best_graph(data_df, selected_column)
    
    return summary, fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
