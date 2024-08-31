import dash
from dash import dcc, html
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

data = pd.read_csv('data.csv')


def classes_fromto(year1=1888, year2=2023):
    return px.bar(data[(data['DateAcquired'] >= year1) & (data['DateAcquired'] <= year2)]['Classification'].value_counts(), labels=dict(value='count', index='classes')).update_layout(showlegend=False, title=f'Classes distribution from {year1} to {year2}')


def countries_distribution(year=2023, group_smallest=True, group_method='mean'):
    temp = data[data['DateAcquired'] <= year]['Country'].value_counts()
    if group_smallest:
        other = temp[temp <= (np.mean(temp) if group_method ==
                              'mean' else np.median(temp))]
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
    temp['CountLog'] = temp[temp['Count'] != 0]['Count'].astype(float).apply(np.log)
    temp['Count'] = temp[temp['Count'] != 0]['Count'].astype(int)
    temp = temp.replace(np.nan, 0)
    fig = px.bar(
        temp,
        x='Classification',
        y='CountLog',
        animation_frame='Year',
        labels={'CountLog': 'Number of Artworks (log)', 'Count': 'Number of artworks'},
        color_discrete_sequence=['#3DCCC0'],
        range_y=[0.1, max(temp['CountLog'])],
        hover_data={'Year': False, 'Classification': False, 'Count': True, 'CountLog': False}
    )
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
    fig.update_layout(
        title=dict(text='Classification of Acquired Artworks',
                   x=0.05, y=0.95
                   ),
        template='ggplot2'
    )
    return fig


def acquired_plot(total=True):

    if total:
        temp = data.groupby('DateAcquired').count().cumsum().reset_index()
    else:
        temp = data.groupby('DateAcquired').count().reset_index()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=temp['DateAcquired'],
            y=temp['Artist']
        )
    )

    fig.update_layout(
        title='Total number of art acquired' if total else 'Arts acquired',
        xaxis_title='Year',
        yaxis_title='Arts',
    )

    return fig

def sunburst(countries=None):
    if countries:
        temp = data[data['Country'].isin(countries)]
    else:
        temp = data.copy()
    fig = px.sunburst(temp, path=['Department', 'Classification'], color_discrete_sequence=['#4a4bc7'])
    fig.update_traces(
        go.Sunburst(hovertemplate='Number of artworks=%{value}'
    ))
    fig.update_layout(
        title=dict(text='Artworks Classification Arranged by Department', font=dict(color='black'))
    )
    return fig

def genders_chart():
    df = pd.pivot_table(data, index='DateAcquired', columns='Gender', values='Artist', aggfunc='count')
    df = df.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['DateAcquired'], y=df['Female'],
        fillcolor='rgb(111, 231, 219)',
        mode='lines',
        line=dict(width=0.5, color='rgb(111, 231, 219)'),
        stackgroup='one',
        name='Female',
        groupnorm='percent',  # sets the normalization for the sum of the stackgroup
        hovertemplate='Year=%{x}' + '<br>Percentage=%{y:.2f}' + '%'

    ))

    fig.add_trace(go.Scatter(
        x=df['DateAcquired'], y=df['Male'],
        fillcolor='rgb(74, 75, 199)',
        mode='lines',
        line=dict(width=0.5, color='rgb(74, 75, 199)'),
        stackgroup='one',
        name='Male',
        hovertemplate='Year: %{x}' + '<br>Percentage: %{y:.2f}' + '%'
    ))

    fig.update_layout(
        title=dict(text='Gender of Artists Over Time',
                   x=0.05, y=0.95
                   ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=0.02,
            font=dict(family="Arial", size=12),
            bordercolor="white",
            borderwidth=1,
            itemsizing='trace'
        ),
        xaxis_type='linear',
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'))

    fig.update_yaxes(title='Percentage of Artworks Acquired')
    fig.update_xaxes(title='Year Acquired')
    fig.update_layout(template="simple_white")

    return fig

def line_chart_nationalities():
    temp = data.groupby(['DateAcquired', 'Country'])['Title'].count().reset_index().rename({'Title': 'Count'}, axis=1)
    # Number of different countries per year
    temp2 = temp.groupby('DateAcquired')['Country'].count().reset_index()

    # Number of new countries by the years
    new_country = []
    new = []
    temp2['New'] = np.nan
    for year in temp['DateAcquired'].unique():
        country_year = temp[temp['DateAcquired'] == year]['Country'].values
        new_year = [country for country in country_year if country not in new_country]
        for n in new_year: new_country.append(n)
        new.append(len(new_country))
    temp2['New'] = new
    temp2.rename({'Country': 'Different nationalities by year', 'New': 'Different nationalities until that year'},
                 axis=1, inplace=True)

    fig = px.line(temp2, x='DateAcquired',
                  y=['Different nationalities by year', 'Different nationalities until that year'],
                  hover_data={'DateAcquired': False, 'variable': False, 'value': True},
                  color_discrete_sequence=['#9acfbf','#3eceaf'],
                  labels={'DateAcquired': 'Year Artworks were Acquired', 'variable': '', 'value': 'Number of Nationalities'},
                  height=350,
                  width=690
                  )

    fig.update_layout(
        title=dict(text='Diversity of Artists\' Origins Over Time',
                   x=0.05, y=0.95
                   ),
        template='ggplot2',
        hovermode="x",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.95,
            xanchor="left",
            x=0.02,
            font=dict(family="Arial", size=12),
            bordercolor="white",
            borderwidth=1,
            itemsizing='trace'
        )
    )
    fig.update_traces(hovertemplate='%{y}<extra></extra>',
                      line=dict(width=3))

    return fig

def map_with_animation():
    # 2 options (comment the one you don't want)
    ### With growth
    temp = data.groupby(['DateAcquired', 'Country'])['Title'].count
