import pandas as pd
import os
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html


print("Python Initiated")

TIMEOUT = 3

data_folder='data'
input_filename = 'ppp.csv'
currency_file_name = 'currency.csv'

ppp = pd.read_csv(os.path.join(data_folder,input_filename))
currency = pd.read_csv(os.path.join(data_folder,currency_file_name))

category_list_base = ["(All)"] + list(ppp['category'].unique())
base_list_base = list(ppp['base'].unique())


def get_product_list(category):
    if category == "(All)":
        product_list = list(ppp['product'].unique())
    else:
        product_list = list(ppp[ppp['category']==category]['product'].unique())
    return ["(All)"] + product_list

product_list_base = get_product_list("(All)")


base_list = [{'label':"Base Currency: "+y,'value':y} for y in base_list_base]
category_list = [{'label':"Category: "+y,'value':y} for y in category_list_base]
product_list = [{'label': "Product: "+y, 'value':y} for y in product_list_base]

colors = dict(background='#f1f6f9', text1='#14274e', text2='#394867', border='#9ba4b4')

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


base_selector = dcc.Dropdown(
        id='base_selection',
        options=base_list,
        value="USD",
        clearable=False
    )

category_selector = dcc.Dropdown(
        id='category_selection',
        options=category_list,
        value='(All)',
        clearable=False
    )

app.layout = html.Div([
    
    html.Div(children=[
            html.Div(base_selector),
            html.Div(category_selector),
            html.Div(dcc.Dropdown(id='product_selection'))]

    ),
    html.Div([dcc.Graph(id='index_plot')])
], style={'background-color':colors['background'],
            'max-width':'800px','borderStyle':'solid', 'borderRadius':'15px',
            'borderWidth':'2px', 'borderColor':colors['border'],'padding':'10px'})

@app.callback(
    dash.dependencies.Output('product_selection', 'options'),
    dash.dependencies.Output('product_selection', 'value'),
    [dash.dependencies.Input('category_selection', 'value')])
def update_product_list(category):
    product_list_dynamic = get_product_list(category)
    return [{'label': "Product: "+y, 'value':y} for y in product_list_dynamic], "(All)"


@app.callback(
    dash.dependencies.Output('index_plot', 'figure'),
    [dash.dependencies.Input('base_selection', 'value'),
     dash.dependencies.Input('category_selection', 'value'),
     dash.dependencies.Input('product_selection', 'value')])
def update_plot(base,category,product):
    return get_figure(base,category,product)
        

def get_figure (base,category,product):
    df = ppp[ppp['base']==base]
    if category!="(All)":
        df = df[(df['category']==category)]
    if product!="(All)":
        df = df[(df['product']==product)]
    df = df[['currency','PPP','eX','valued']].groupby('currency').mean()
    df = df.reset_index()
    df = df.sort_values(by='valued')
    df['color'] = 'red'
    df.loc[df['valued']<0,'color']='blue'
    df.loc[df['valued']==0,'color']='black'
    df = df.merge(currency, on='currency')
    df['blank'] = " "
    df['equal'] = " = "
    df['PPP value'] = (df['multiplier']*df['PPP']).round(2)
    df['base'] = " " + base
    df['PPP text'] = " (PPP) \t"
    df['eX value'] = (df['multiplier']*df['eX']).round(2)
    df['eX text'] = " (eX) "
    df['text'] = df['multiplier'].astype(str) + df['blank'] + df['currency'] + df['equal'] + df['PPP value'].astype(str) + df['base'] + df['PPP text'] + df['eX value'].astype(str) + df['base'] + df['eX text']
    df.drop(columns=['multiplier','blank','equal','PPP value','PPP text','eX value','eX text'], inplace=True)
    
    fig = go.Figure(data=go.Scatter(x=df['currency'],
                                y=df['valued'],
                                mode='markers',
                                marker_color=df['color'],
                                text=df['text'])) # hover text goes here

    fig.update_layout(yaxis=dict(tickformat="%"))
    return fig

server = app.server

if __name__ == '__main__':
    server.run(host="0.0.0.0", debug=True)
    # app.run_server(debug=False)

