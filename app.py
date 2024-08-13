import dash
from dash import dcc, html, dash_table
import dash.dependencies as dd
import plotly.express as px
import pandas as pd
import boto3
from io import BytesIO

s3 = boto3.client(
    's3',
    aws_access_key_id='KEY',
    aws_secret_access_key='SECRET-KEY',
    region_name='us-east-2'
)
bucket_name = 'bibhus-bucket'

# Function to list files in S3 bucket
def list_files_in_bucket(bucket_name):
    objects = s3.list_objects_v2(Bucket=bucket_name)
    files = [obj['Key'] for obj in objects.get('Contents', []) if obj['Key'].endswith(('.xlsx', '.csv'))]
    return files

# Populate the dropdown with file names from S3
available_files = list_files_in_bucket(bucket_name)

# Function to load a file from S3
def load_file_from_s3(bucket_name, file_name):
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    if file_name.endswith('.xlsx'):
        return pd.read_excel(BytesIO(obj['Body'].read()), sheet_name='data')
    elif file_name.endswith('.csv'):
        return pd.read_csv(BytesIO(obj['Body'].read()))

# Preprocess the dataset
def preprocess_data(df):
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

# Function to calculate summary statistics
def calculate_statistics(df, column):
    if df[column].dtype in ['int64', 'float64']:
        stats = df[column].describe().to_frame().reset_index()
        stats.columns = ['Statistical Feature', 'Value']
    else:
        stats = df[column].value_counts().to_frame().reset_index()
        stats.columns = ['Value', 'Count']
        stats['Percentage'] = (stats['Count'] / stats['Count'].sum()) * 100
    return stats

# Function to generate all possible graphs for numerical columns
def generate_numerical_graphs(data_df, column):
    graphs = []
    unique_values = data_df[column].nunique()
    skewness = data_df[column].skew()

    if unique_values < 10:
        graphs.append(('Bar Chart', px.bar(data_df[column].value_counts().reset_index(),
                                        x='index', y=column,
                                        title=f'Bar Chart of {column}',
                                        labels={'index': column, column: 'Count'})))
    if skewness > 1 or skewness < -1:
        graphs.append(('Box Plot', px.box(data_df, y=column, title=f'Box Plot of {column}')))
    if unique_values < 100:
        graphs.append(('Histogram', px.histogram(data_df, x=column, title=f'Histogram of {column}')))
    if unique_values < 1000:
        graphs.append(('Violin Plot', px.violin(data_df, y=column, title=f'Violin Plot of {column}')))
    if data_df.index.is_monotonic_increasing:
        graphs.append(('Line Plot', px.line(data_df, y=column, title=f'Line Plot of {column}')))
    
    graphs.append(('ECDF Plot', px.ecdf(data_df, x=column, title=f'ECDF Plot of {column}')))

    return graphs

# Function to generate all possible graphs for categorical columns
def generate_categorical_graphs(data_df, column):
    graphs = []
    unique_values = data_df[column].nunique()
    
    if unique_values < 10:
        graphs.append(('Pie Chart', px.pie(data_df, names=column, title=f'Pie Chart of {column}')))
    if unique_values < 50:
        graphs.append(('Bar Chart', px.bar(data_df[column].value_counts().reset_index(),
                                        x='index', y=column,
                                        title=f'Bar Chart of {column}',
                                        labels={'index': column, column: 'Count'})))
    if unique_values < 100:
        graphs.append(('Treemap', px.treemap(data_df, path=[column], title=f'Treemap of {column}')))
    if unique_values < 200:
        graphs.append(('Sunburst Chart', px.sunburst(data_df, path=[column], title=f'Sunburst Chart of {column}')))
    
    graphs.append(('Count Plot', px.histogram(data_df, x=column, title=f'Count Plot of {column}')))

    return graphs

# Function to select the best possible graph
def select_best_graph(data_df, column):
    if data_df[column].dtype in ['int64', 'float64']:
        # For numerical columns
        unique_values = data_df[column].nunique()
        skewness = data_df[column].skew()
        
        if unique_values < 10:
            return 'Bar Chart'
        elif skewness > 1 or skewness < -1:
            return 'Box Plot'
        elif unique_values < 100:
            return 'Histogram'
        elif unique_values < 1000:
            return 'Violin Plot'
        elif data_df.index.is_monotonic_increasing:
            return 'Line Plot'
        else:
            return 'ECDF Plot'
    else:
        # For categorical columns
        unique_values = data_df[column].nunique()
        
        if unique_values < 10:
            return 'Pie Chart'
        elif unique_values < 50:
            return 'Bar Chart'
        elif unique_values < 100:
            return 'Treemap'
        elif unique_values < 200:
            return 'Sunburst Chart'
        else:
            return 'Count Plot'

# Initialize the Dash app
app = dash.Dash(__name__)

# Define descriptions for each graph type
graph_descriptions = {
    'Bar Chart': 'A bar chart displays categorical data with rectangular bars representing different categories.',
    'Box Plot': 'A box plot shows the distribution of a dataset and highlights the median, quartiles, and outliers.',
    'Histogram': 'A histogram represents the distribution of numerical data by showing the frequency of data points in intervals.',
    'Violin Plot': 'A violin plot combines aspects of a box plot and a KDE plot to show data distribution and density.',
    'Line Plot': 'A line plot displays data points connected by lines, commonly used for time series data.',
    'ECDF Plot': 'An ECDF plot shows the empirical cumulative distribution function of a dataset.',
    'Pie Chart': "A pie chart represents categorical data as slices of a circle, with each slice proportional to the category's frequency.",
    'Treemap': 'A treemap displays hierarchical data as nested rectangles, with the size of each rectangle proportional to the data value.',
    'Sunburst Chart': 'A sunburst chart visualizes hierarchical data with concentric circles, where each level of the hierarchy is represented by a ring.',
    'Count Plot': 'A count plot is similar to a bar chart but shows the frequency of categorical data.'
}

# Define layout
app.layout = html.Div([
    html.H1("Data Profiling Dashboard"),
    
    # Dropdown for selecting the file
    dcc.Dropdown(
        id='file-dropdown',
        options=[{'label': f, 'value': f} for f in available_files],
        value=available_files[0],  # Default to the first file
        clearable=False,
        style={'margin-bottom': '20px'}
    ),
    
    # Container for the data summary
    html.Div(id='data-summary', style={'margin-bottom': '20px'}),
    
    # DataTable for displaying raw data with pagination and sorting
    dash_table.DataTable(
        id='data-table',
        page_size=10,
        sort_action='native',
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    ),

    # Container for the statistical summary
    html.Div(id='statistical-summary', style={'margin-bottom': '20px'}),
    
    # Dropdown for selecting the column to plot (populated dynamically)
    dcc.Dropdown(
        id='column-dropdown',
        clearable=False,
        style={'margin-bottom': '20px'}
    ),

    # Div for graph description
    html.Div(id='graph-description', style={'margin-bottom': '20px', 'padding': '10px', 'border': '1px solid #ddd', 'border-radius': '5px'}),
    
    # Tabs for different plots
    dcc.Tabs(id='graph-tabs', value='best-graph', children=[]),
])

# Callback to update column dropdown based on the selected file
@app.callback(
    dd.Output('column-dropdown', 'options'),
    dd.Output('column-dropdown', 'value'),
    dd.Output('data-table', 'columns'),
    dd.Output('data-table', 'data'),
    dd.Input('file-dropdown', 'value')
)
def update_columns(file_name):
    data_df = load_file_from_s3(bucket_name, file_name)
    data_df = preprocess_data(data_df)
    options = [{'label': col, 'value': col} for col in data_df.columns]
    value = data_df.columns[0]
    columns = [{'name': i, 'id': i} for i in data_df.columns]
    data = data_df.to_dict('records')
    return options, value, columns, data

# Combined callback to update the data summary, statistical summary, graph tabs, and description
@app.callback(
    [dd.Output('data-summary', 'children'),
    dd.Output('statistical-summary', 'children'),
    dd.Output('graph-tabs', 'children'),
    dd.Output('graph-tabs', 'value'),
    dd.Output('graph-description', 'children')],
    [dd.Input('column-dropdown', 'value'),
    dd.Input('graph-tabs', 'value'),
    dd.Input('file-dropdown', 'value')]
)
def update_output(selected_column, selected_tab, file_name):
    data_df = load_file_from_s3(bucket_name, file_name)
    data_df = preprocess_data(data_df)
    
    total_data_points = len(data_df[selected_column])
    null_ratio = data_df[selected_column].isnull().mean()
    
    summary = html.Div([
        html.P(f"Total Data Points: {total_data_points}", id="numerical-data-description"),
        html.P(f"Ratio of Null Values: {null_ratio:.2%}", id="numerical-data-description")
    ])
    
    # Calculate statistical summary
    stats_df = calculate_statistics(data_df, selected_column)
    page_size = 10 if len(stats_df) > 10 else len(stats_df)
    statistical_summary = dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in stats_df.columns],
        data=stats_df.to_dict('records'),
        page_size=page_size,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
    )

    if data_df[selected_column].dtype in ['int64', 'float64']:
        graphs = generate_numerical_graphs(data_df, selected_column)
    else:
        graphs = generate_categorical_graphs(data_df, selected_column)
    
    best_graph = select_best_graph(data_df, selected_column)
    
    tabs = [dcc.Tab(label=title, children=[dcc.Graph(figure=fig, style={'width': '100%'})], value=title)
            for title, fig in graphs]
    
    ctx = dash.callback_context
    if not ctx.triggered:
        triggered_input = 'column-dropdown'
    else:
        triggered_input = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_input == 'column-dropdown':
        selected_tab = best_graph

    description = [html.P(f"{title}: {graph_descriptions.get(title, 'No description available.')}") for title, _ in graphs]
    return summary, statistical_summary, tabs, selected_tab, description

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
