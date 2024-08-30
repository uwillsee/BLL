import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import gunicorn

import numpy as np
import pandas as pd
from re import search

import plotly.graph_objects as go
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')

# Загрузка данных
data = pd.read_csv('translated_books.csv')

# Функция для распределения по классификации
def classes_fromto(year1=1888, year2=2023):
    filtered_data = data[(data['DateAcquired'] >= year1) & (data['DateAcquired'] <= year2)]
    return px.bar(
        filtered_data['Classification'].value_counts(), 
        labels=dict(value='count', index='classes')
    ).update_layout(showlegend=False, title=f'Classes distribution from {year1} to {year2}')

# Функция для распределения по странам
def countries_distribution(year=2020, group_smallest=True, group_method='mean'):
    temp = data[data['DateAcquired'] <= year]['Country'].value_counts()
    if group_smallest:
        other = temp[temp <= (np.mean(temp) if group_method == 'mean' else np.median(temp))]
        temp = temp[temp > (np.mean(temp) if group_method == 'mean' else np.median(temp))]
        temp['Other'] = other.sum()
    return px.pie(temp, values=temp.values, names=temp.index, title=f'Country distribution up to {year}')

# Функция для отображения количества страниц
def pages_distribution():
    return px.histogram(
        data, 
        x='Pages', 
        nbins=20, 
        title='Pages distribution'
    )

# Функция для отображения произведений по авторам
def books_by_author():
    return px.bar(
        data['Author'].value_counts(), 
        labels=dict(value='count', index='author'),
        title='Books by Author'
    )

# Функция для отображения среднего рейтинга по странам
def average_grade_by_country():
    filtered_data = data.dropna(subset=['Grade'])
    return px.bar(
        filtered_data.groupby('Country')['Grade'].mean().sort_values(), 
        labels=dict(value='Average Grade', index='Country'),
        title='Average Grade by Country'
    )

# Инициализация приложения Dash
app = dash.Dash(__name__)

# Лейаут приложения
app.layout = html.Div([
    html.H1("Books Data Dashboard"),
    dcc.Tabs([
        dcc.Tab(label='Classification Distribution', children=[
            dcc.Graph(figure=classes_fromto())
        ]),
        dcc.Tab(label='Country Distribution', children=[
            dcc.Slider(
                id='year-slider',
                min=data['DateAcquired'].min(),
                max=data['DateAcquired'].max(),
                value=2020,
                marks={str(year): str(year) for year in range(1888, 2025, 10)},
                step=None
            ),
            dcc.Graph(id='country-dist')
        ]),
        dcc.Tab(label='Pages Distribution', children=[
            dcc.Graph(figure=pages_distribution())
        ]),
        dcc.Tab(label='Books by Author', children=[
            dcc.Graph(figure=books_by_author())
        ]),
        dcc.Tab(label='Average Grade by Country', children=[
            dcc.Graph(figure=average_grade_by_country())
        ])
    ])
])

# Callback для обновления распределения по странам в зависимости от выбранного года
@app.callback(
    Output('country-dist', 'figure'),
    Input('year-slider', 'value')
)
def update_country_distribution(year):
    if year is None:
        raise PreventUpdate
    return countries_distribution(year)

# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)