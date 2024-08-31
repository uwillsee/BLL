import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Загрузка данных
data = pd.read_csv('data.csv')

# Функции для отображения данных
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

def acquired_plot(total=True):
    if total:
        temp = data.groupby('DateAcquired').count().cumsum().reset_index()
    else:
        temp = data.groupby('DateAcquired').count().reset_index()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=temp['DateAcquired'],
            y=temp['Author']
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
    df = pd.pivot_table(data, index='DateAcquired', columns='Gender', values='Author', aggfunc='count')
    df = df.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['DateAcquired'], y=df['Female'],
        fillcolor='rgb(111, 231, 219)',
        mode='lines',
        line=dict(width=0.5, color='rgb(111, 231, 219)'),
        stackgroup='one',
        name='Female',
        groupnorm='percent',
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
        title=dict(text='Gender of Authors Over Time',
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
    temp2 = temp.groupby('DateAcquired')['Country'].count().reset_index()

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
        title=dict(text='Diversity of Authors\' Origins Over Time',
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
    temp = data.groupby(['DateAcquired', 'Country'])['Title'].count().unstack().replace(np.nan, 0).cumsum()
    temp = pd.DataFrame(temp.stack()).reset_index().rename({0: 'Count'}, axis=1)

    temp['Countlog'] = np.log(temp['Count'])

    fig = px.choropleth(temp, locations='Country', locationmode='country names',
                        color='Countlog',
                        color_continuous_scale=['#e8e6ff', '#dcd9ff', '#b2b0ff', '#8889e0', '#6063b6', '#4a4bc7', '#33357f'],
                        animation_frame='DateAcquired',
                        range_color=(0, temp['Countlog'].max()),
                        hover_name='Country',
                        hover_data={'Country':False,'Count':True,'Countlog':False,'DateAcquired':False},
                        labels={'DateAcquired': 'Year', 'Countlog': 'Acquired
