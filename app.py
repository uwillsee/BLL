import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
from re import search
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

# Загрузка данных
data = pd.read_csv('data.csv')

# Функции аналитики
def classes_fromto(year1=1929, year2=2020):
    return px.bar(data[(data['DateAcquired'] >= year1) & (data['DateAcquired'] <= year2)]['Classification'].value_counts(), labels=dict(value='count', index='classes')).update_layout(showlegend=False, title=f'Classes distribution from {year1} to {year2}')

def countries_distribution(year=2020, group_smallest=True, group_method='mean'):
    temp = data[data['DateAcquired'] <= year]['Country'].value_counts()
    if group_smallest:
        other = temp[temp <= (np.mean(temp) if group_method == 'mean' else np.median(temp))]
        temp.drop(other.index, inplace=True)
        temp = temp.append(pd.Series({'Other': np.sum(other)}))
    return px.bar(temp, labels=dict(value='count', index='countries')).update_layout(showlegend=False, title=f'Countries distribution in {year}')

def bar_with_animation():
    classes = ['Architecture', 'Design', 'Drawing', 'Illustrated Book', 'Painting', 'Photograph', 'Print', 'Sculpture']
    temp = pd.DataFrame(columns=['Year', 'Classification', 'Count'])
    for year in sorted(data['DateAcquired'].unique()):
        for class_ in classes:
            count = data[(data['DateAcquired'] == year) & (data['Classification'] == class_)].count()['Title']
            temp = temp.append({'Year': year, 'Classification': class_, 'Count': count}, ignore_index=True)
    temp['CountLog'] = temp['Count'].apply(np.log)
    temp = temp.replace(np.nan, 0)
    fig = px.bar(
        temp,
        x='Classification',
        y='CountLog',
        animation_frame='Year',
        labels={'CountLog': 'Number of Artworks (log)', 'Count': 'Number of artworks'},
        color_discrete_sequence=['#3DCCC0'],
        range_y=[0.1, max(temp['CountLog'])]
    )
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', title='Classification of Acquired Artworks')
    return fig

# Создание Dash-приложения
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = dcc.Loading(
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        children=[
                            html.Img(
                                src=app.get_asset_url("moma-logo.png"),
                                style={'width': '140%', 'margin-top': '0px'}
                            ),
                        ],
                        style={'width': '25%'}
                    ),
                    html.Div(
                        children=[
                            html.H5('The Museum of Modern Art (MoMA) acquired its first artworks in 1929.'
                                    ' Today, the Museum’s evolving collection contains almost 200,000 works'
                                    ' from around the world spanning the last 150 years. In this dashboard, '
                                    'you can go on tour with the MoMA museum by getting insights into which '
                                    'artworks it acquired over the years and by which artists. Next, you can '
                                    'see MoMA per country by checking which country the art pieces come from. '
                                    'The art collections include an ever-expanding range of visual expression, '
                                    'including painting, sculpture, photography, architecture, design, and '
                                    'film art. Travel through time and space with MoMA and enjoy the tour...'),
                        ],
                        className='card',
                        style={"height": "25%"},
                    ),
                      ],
                className='body',
                style={'width': '50%'}
            ),
            html.Div(
                children=[
                    dcc.Loading([
                        dcc.Graph(figure=map_with_animation(), id='main-choropleth')
                    ], type='default', color='black', id="map-loading")
                ],
                className='card',
                style={'width': '50%', 'margin-bottom': '7px'}
            ),
        ],
        className='container'
    ),
    type='cube', color='white'
)

@app.callback(
    Output('unique-artists', 'children'),
    Output('unique-artworks', 'children'),
    Output('male-count', 'children'),
    Output('female-count', 'children'),
    Output('sunburst', 'figure'),
    Output('donut', 'figure'),
    Input('countries-dropdown', 'value')
)
def update_stats(value):
    stats = statistics(value)
    return stats[0], stats[1], stats[2], stats[3], sunburst(value), donut_chart(value)


if __name__ == '__main__':
    app.run_server(debug=True)
