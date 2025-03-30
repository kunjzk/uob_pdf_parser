# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, callback, Input, Output, State
from typing import Optional, Tuple, Dict, Any, List
import plotly.express as px
import pandas as pd
import camelot
from datetime import datetime
import os
import base64
from plotly.graph_objects import Figure

app = Dash(__name__)

# Define the path for storing balance data
BALANCE_FILE = 'balance_data.csv'

# Initialize global data structure from disk if it exists, otherwise empty
if os.path.exists(BALANCE_FILE):
    balance_data = pd.read_csv(BALANCE_FILE)
    balance_data['date'] = pd.to_datetime(balance_data['date'])
else:
    balance_data = pd.DataFrame(columns=['date', 'balance'])

# Month and year options for dropdowns
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
years = ['2025', '2024', '2023', '2022', '2021', '2020']

def get_balance(path_to_file: str) -> Optional[float]:
    try:
        tables = camelot.read_pdf(path_to_file, flavor='stream', pages='1')
        balance_df = tables[0].df
        try:
            balance_str = balance_df.iloc[13, -1]
        except:
            try:
                # for september 2024, the balance is in the row with "One Account"
                balance_str = balance_df.loc[balance_df[0]=="One Account"].iloc[0, 5]
            except:
                # before jul 2024, the balance is in the row with "UNIPLUS"
                balance_str = balance_df.loc[balance_df[0]=="UNIPLUS"].iloc[0, 5]
        # Remove commas and convert to float
        balance = float(balance_str.replace(',', ''))
        return balance
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None

def save_balance_data(df: pd.DataFrame) -> None:
    """Save balance data to disk"""
    df.to_csv(BALANCE_FILE, index=False)

app.layout = html.Div([
    html.H1('UOB Bank Balance Tracker'),
    
    # Upload section
    html.Div([
        dcc.Upload(
            id='upload-pdf',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select PDF')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=False
        ),
        
        # Upload confirmation message
        html.Div(id='upload-confirmation', style={'margin': '10px', 'color': 'green'}),
        
        # Month and Year dropdowns
        html.Div([
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in months],
                placeholder='Select Month',
                style={'width': '200px', 'display': 'inline-block', 'margin': '10px'}
            ),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': year, 'value': year} for year in years],
                placeholder='Select Year',
                style={'width': '200px', 'display': 'inline-block', 'margin': '10px'}
            ),
            html.Button('Upload', id='upload-button', n_clicks=0,
                       style={'margin': '10px', 'padding': '5px 15px'})
        ]),
        
        # Error message display
        html.Div(id='error-message', style={'color': 'red', 'margin': '10px'})
    ]),
    
    # Graph
    dcc.Graph(id='balance-graph'),
    
    # Store for uploaded file contents
    dcc.Store(id='stored-contents')
])

@callback(
    [Output('stored-contents', 'data'),
     Output('upload-confirmation', 'children')],
    Input('upload-pdf', 'contents'),
    prevent_initial_call=True
)
def store_contents(contents: Optional[str]) -> Tuple[Optional[str], str]:
    if contents is None:
        return None, ''
    return contents, 'PDF file received! Select month and year, then click Upload.'

@callback(
    [Output('balance-graph', 'figure'),
     Output('error-message', 'children')],
    [Input('upload-button', 'n_clicks')],
    [State('stored-contents', 'data'),
     State('month-dropdown', 'value'),
     State('year-dropdown', 'value')]
)
def update_graph(n_clicks: int, contents: Optional[str], month: Optional[str], year: Optional[str]) -> Tuple[Figure, str]:
    global balance_data
    
    if n_clicks == 0:
        # Initial state - show empty graph
        fig = px.line(balance_data, x='date', y='balance',
                     title='Bank Balance Over Time')
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                ticktext=[],
                tickvals=[]
            )
        )
        return fig, ''
    
    if contents is None:
        return px.line(balance_data, x='date', y='balance',
                      title='Bank Balance Over Time'), 'Please select a PDF file'
    
    if not month or not year:
        return px.line(balance_data, x='date', y='balance',
                      title='Bank Balance Over Time'), 'Please select both month and year'
    
    try:
        # Decode the uploaded file
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Save the file temporarily
        with open('temp.pdf', 'wb') as f:
            f.write(decoded)
        
        # Get balance from PDF
        balance = get_balance('temp.pdf')
        
        if balance is None:
            return px.line(balance_data, x='date', y='balance',
                          title='Bank Balance Over Time'), 'Error processing PDF. Please try again.'
        
        # Convert month and year to datetime
        # Note: We're using the first day of the next month as the date
        month_num = months.index(month) + 1
        # If it's December, increment the year
        if month_num == 12:
            date = datetime(int(year) + 1, 1, 1)
        else:
            date = datetime(int(year), month_num + 1, 1)
        
        # Remove existing entry for this date if it exists
        balance_data = balance_data[balance_data['date'] != date]
        
        # Add new data point
        new_row = pd.DataFrame({'date': [date], 'balance': [balance]})
        balance_data = pd.concat([balance_data, new_row], ignore_index=True)
        
        # Sort the data by date
        balance_data = balance_data.sort_values('date')
        
        # Save to disk
        save_balance_data(balance_data)
        
        # Create the graph
        fig = px.line(balance_data, x='date', y='balance',
                     title='Bank Balance Over Time',
                     labels={'date': 'Date', 'balance': 'Balance (SGD)'})
        
        # Format date axis
        fig.update_xaxes(
            tickformat='%b %Y',
            tickmode='array',
            ticktext=balance_data['date'].dt.strftime('%b %Y'),
            tickvals=balance_data['date']
        )
        
        # Add balance labels above points
        fig.update_traces(text=balance_data['balance'].apply(lambda x: f'${x:,.2f}'),
                         textposition='top center',
                         mode='lines+markers+text')
        
        # Clean up temporary file
        os.remove('temp.pdf')
        
        return fig, ''
        
    except Exception as e:
        return px.line(balance_data, x='date', y='balance',
                      title='Bank Balance Over Time'), f'Error: {str(e)}'

if __name__ == '__main__':
    app.run(debug=True)
