import dash
from dash import Dash, html, dcc, dash_table, callback, Output, Input, State
import news_data as nd

# Load data
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

def get_data(option):
    if option == 'option1':
        return nd.brazilJournal_main(headers)
    elif option == 'option2':
        return nd.brazilJournal_economy(headers)
    elif option == 'option3':
        return nd.brazilJournal_business(headers)
    elif option == 'option4':
        return nd.valorPublic_main(headers)
    elif option == 'option5':
        return nd.valorPaid_main(headers)
    elif option == 'option6':
        return nd.valorFinances_main(headers)
    elif option == 'option7':
        return nd.valorEmpresas_main(headers)

# Initialize the app
app = dash.Dash(__name__, assets_folder='assets')

# App layout
app.layout = html.Div([
    html.Div(className='app-header', children=[
        html.Div(className='app-header--title', children="News Scraping")
    ]),
    
    html.Div([
        html.Hr(className='hr'),
        html.Button('Brazil Journal Main Page', id='button1', n_clicks=0),
        html.Button('Brazil Journal Economy', id='button2', n_clicks=0),
        html.Button('Brazil Journal Business', id='button3', n_clicks=0),
        html.Button('Valor Main Page Public', id='button4', n_clicks=0),
        html.Button('Valor Main Page Paid', id='button5', n_clicks=0),
        html.Button('Valor Finances', id='button6', n_clicks=0),
        html.Button('Valor Business', id='button7', n_clicks=0),
        html.Div(id='table-content', className='table-content'),
        html.Div(id='article-details', className='article-details')
    ]),
    dcc.Input(id='clicked-row-index', type='hidden', value='')
])

# Update the table content based on button clicks
@app.callback(
    Output('table-content', 'children'),
    [Input('button1', 'n_clicks'),
     Input('button2', 'n_clicks'),
     Input('button3', 'n_clicks'),
     Input('button4', 'n_clicks'),
     Input('button5', 'n_clicks'),
     Input('button6', 'n_clicks'),
     Input('button7', 'n_clicks')]
)
def update_table_content(*button_clicks):
    button_id = button_clicks.index(max(button_clicks)) + 1
    table = get_data(f"option{button_id}")

    if table:
        table_data = [{"headline": headline, "link": f"[Link]({link})", "ler": "Ler"} for headline, link in table.items()]
        table_data_with_line_breaks = [{k: v.replace('\n', '<br>') for k, v in item.items()} for item in table_data]
        data_table = dash_table.DataTable(
            id='table',
            columns=[
                {"name": "Headline", "id": "headline"},
                {"name": "Link", "id": "link", "presentation": "markdown"},
                {"name": "Ler", "id": "ler"}
            ],
            page_size=20,
            data=table_data_with_line_breaks,
            markdown_options={"html": True},
            style_cell={'textAlign': 'left'}
        )

        return data_table
    else:
        return html.Div("No data available for this option")

# Handle table row click event
@app.callback(
    [Output('article-details', 'children'),
     Output('clicked-row-index', 'value')],
    [Input('table', 'active_cell')],
    [State('table', 'derived_virtual_data'),
     State('clicked-row-index', 'value')]
)
def handle_table_click(active_cell, rows, clicked_row_index):
    if active_cell:
        row_index = active_cell['row']
        link = rows[row_index]['link']
        
        # Extract the href from the markdown link
        href_start = link.index('(') + 1
        href_end = link.index(')')
        href = link[href_start:href_end]
        
        # Call your function based on the href
        hrefAux = href
        hrefAux = hrefAux.replace("https://", "")

        # If the link is from Brazil Journal
        if hrefAux.startswith("braziljournal.com"):
            headline, datetime, author, article = nd.brazilJournal_news(href, headers)
        else:
            headline, datetime, author, article = nd.valor_news(href, headers)
        
        bulletpoints = nd.openai_bulletpoints(article, headers)
        headline = headline.replace('.', '<br>')
        # Create article details component
        article_details = html.Div([
            html.H3(headline),
            html.H4(bulletpoints),  
            html.P(f"Date and Time: {datetime}"),
            html.P(f"Author: {author}"),
            html.Hr(),
            html.P(article),
            html.P(className='author', children=f"Author: {author}")
        ])
        
        return article_details, row_index
    
    return None, clicked_row_index

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
