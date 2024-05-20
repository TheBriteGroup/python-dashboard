import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Load the data
file_path = './pum.xlsx'
data_df = pd.read_excel(file_path, sheet_name='data')

# Initialize the Dash app
app = dash.Dash(__name__)

# Shipments by Mode of Transportation
mode_counts = data_df['MODE'].value_counts().reset_index()
mode_counts.columns = ['Mode', 'Count']
fig1 = px.bar(mode_counts, x='Mode', y='Count', title='Shipments by Mode of Transportation')

# Shipment Value vs. Shipment Weight
fig4 = px.scatter(data_df, x='SHIPMT_WGHT', y='SHIPMT_VALUE', title='Shipment Value vs. Shipment Weight', opacity=0.6)

# Shipment Trends by Quarter
quarterly_trends = data_df.groupby('QUARTER')['SHIPMT_VALUE'].sum().reset_index()
fig5 = px.line(quarterly_trends, x='QUARTER', y='SHIPMT_VALUE', title='Shipment Trends by Quarter')

# Proportion of Shipments by Temperature Control
temp_control_counts = data_df['TEMP_CNTL_YN'].value_counts().reset_index()
temp_control_counts.columns = ['Temperature Control', 'Count']
fig6 = px.pie(temp_control_counts, values='Count', names='Temperature Control', title='Proportion of Shipments by Temperature Control')

# Box Plot: Shipment Value Distribution by Mode
fig8 = px.box(data_df, x='MODE', y='SHIPMT_VALUE', title='Shipment Value Distribution by Mode')

# Layout of the app
app.layout = html.Div(children=[
    html.Div(className='navbar', children=[
        html.A(href='#overview', children='Overview'),
        html.A(href='#mode-transportation', children='Mode of Transportation'),
        html.A(href='#shipment-value', children='Shipment Value vs Weight'),
        html.A(href='#trends', children='Quarterly Trends'),
        html.A(href='#temperature-control', children='Temperature Control'),
        html.A(href='#value-distribution', children='Value Distribution by Mode'),
    ]),
    
    html.Div(className='content', children=[
        html.H1(children='Shipment Data Visualizations'),
        
        html.Div(id='overview', className='section-title', children='Overview'),
        html.P(children='''
            Analyzing shipment data with different visualizations using Dash and Plotly.
        '''),
        
        html.Div(id='mode-transportation', className='section-title', children='Shipments by Mode of Transportation'),
        html.Div(className='graph-grid', children=[
            html.Div(className='graph-item', children=[
                dcc.Graph(
                    id='bar-mode',
                    figure=fig1,
                )
            ]),
        ]),
        
        html.Div(id='shipment-value', className='section-title', children='Shipment Value vs. Shipment Weight'),
        html.Div(className='graph-grid', children=[
            html.Div(className='graph-item', children=[
                dcc.Graph(
                    id='scatter-value-weight',
                    figure=fig4,
                )
            ]),
        ]),
        
        html.Div(id='trends', className='section-title', children='Shipment Trends by Quarter'),
        html.Div(className='graph-grid', children=[
            html.Div(className='graph-item', children=[
                dcc.Graph(
                    id='line-quarterly-trends',
                    figure=fig5,
                )
            ]),
        ]),
        
        html.Div(id='temperature-control', className='section-title', children='Proportion of Shipments by Temperature Control'),
        html.Div(className='graph-grid', children=[
            html.Div(className='graph-item', children=[
                dcc.Graph(
                    id='pie-temp-control',
                    figure=fig6,
                )
            ]),
        ]),
        
        html.Div(id='value-distribution', className='section-title', children='Shipment Value Distribution by Mode'),
        html.Div(className='graph-grid', children=[
            html.Div(className='graph-item', children=[
                dcc.Graph(
                    id='box-mode-value',
                    figure=fig8,
                )
            ]),
        ]),
    ]),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
