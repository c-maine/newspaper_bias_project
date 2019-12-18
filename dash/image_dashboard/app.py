#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from pathlib import Path
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import records

import sqlalchemy as sql
from sqlalchemy import MetaData, Table
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
import pymysql
import plotly.express as px
from dash.dependencies import Input, Output

# get db address from env file
env_path = Path('/home/assets')/'.env'
load_dotenv(dotenv_path = env_path)
database_address = os.getenv('ADDRESS')

# create engine and table aliases
db = sql.create_engine(database_address)
metadata = MetaData()
articles = Table('articles_tab_news', metadata, autoload=True, autoload_with=db)
countries = Table('countries_tab', metadata, autoload=True, autoload_with=db)
counts = Table('count_tab_news', metadata, autoload=True, autoload_with=db)

# read big table to df
Session = sessionmaker(bind=db)
session = Session()
df_big = pd.read_sql(session.query(counts.c.count,countries.c.country_name, countries.c.country_iso, countries.c.region, countries.c.subregion,
                                   countries.c.population, counts.c.source, counts.c.count).join(countries,countries.c.country_iso==counts.c.country_iso).statement, session.bind)
# deal with a non-defined region
df_big[df_big.region!='']
# sum over all dates
df_big = df_big.groupby(['country_iso','source','region','country_name','subregion','population']).agg({'count': 'sum'}).reset_index()
# create dictionary for nicer display
indicators_dict = {'the-new-york-times': 'The New York Times', 'al-jazeera-english': 'Al Jazeera', 'news24': 'news24', 'the-hindu': 'The Hindu'}

app = dash.Dash('dash-newspapers',assets_folder='home/assets')

app.layout = html.Div(className='layout', children=[
    html.H1(className='title', children='How newspapers report about countries'),
    html.H4('Select a newspaper and discover!', className='subtitle', style={'font-size': '2em'}),

    html.Div(id='aligned_map',children=[
        html.Div([html.H2('Countries', className='subtitle',
                          style={'color': 'white', 'font-size': '2em', 'display': 'inline-block'})]),
        dcc.Dropdown(
                    id='dropdown_map_aligned',
                    options=[{'label': value, 'value': key} for key,value in indicators_dict.items()],
                    value='the-new-york-times'
                ),
        html.Div(id='al_graphs', style={'text-align':'center'}, children=[
            dcc.Graph(id='updatable_map_aligned', style={'width': '59%', 'display': 'inline-block'}),
            dcc.Graph(id='updatable_bar_aligned', style={'width': '41%', 'display': 'inline-block'})
        ],
                 )
    ],
    className='plots'
             ),

    html.Div(id='aligned_pie', children=[
        html.Div([html.H2('Regions and Subregions', className='subtitle',
                          style={'color': 'white', 'font-size': '2em', 'display': 'inline-block'})]),

        dcc.Dropdown(
                        id='dropdown_pie_aligned',
                        options=[{'label': value, 'value': key} for key,value in indicators_dict.items()],
                        value='the-new-york-times'
                    ),
            html.Div(id='al_graphs_pie', style={'text-align':'center'}, children=[
                dcc.Graph(id='updatable_pie_aligned', style={'width': '40%', 'display': 'inline-block'}),
                dcc.Graph(id='updatable_bar_pie_aligned', style={'width': '60%', 'display': 'inline-block'})
            ]
                     )
        ],
        className='plots'
                 ),

    html.Div([html.Div([
        html.Div([html.H2('Compare two Newspapers', className='subtitle', style={'color': 'white', 'font-size': '2em', 'display': 'inline-block'})]),
        html.Div([
            dcc.Dropdown(id='newspaper-selected1',
                         options=[{'label': value, 'value': key} for key, value in indicators_dict.items()],
                         value='the-new-york-times')],
            className="dropdowner",
            style={"width": "45%", "float": "right", 'display': 'inline-block'}
        ),
        html.Div([dcc.Dropdown(id='newspaper-selected2',
                               options=[{'label': value, 'value': key} for key, value in indicators_dict.items()],
                               value='the-hindu')],
                 className="dropdowner_2",
                 style={"width": "45%", "float": "left", 'display': 'inline-block'})],
        className="row",
        style={"padding": 50, "width": "90%", "margin-left": "auto", "margin-right": "auto"}),

        dcc.Graph(id='compare-graph')],
        className='plots'),

    html.Div(id='weighted_map', children=[
        html.H2('Heatmap - countrywise - weighted by country population', className='subtitle',
                style={'color': 'white', 'font-size': '2em'}),
        dcc.Dropdown(
            id='dropdown_map_weighted',
            options=[{'label': value, 'value': key} for key, value in indicators_dict.items()],
            value='the-new-york-times'
        ),
        dcc.Graph(id='updatable_map_weighted')
    ],
             className='plots'
             ),

])


@app.callback(
    Output('updatable_map_aligned', 'figure'),
    [Input('dropdown_map_aligned', 'value')])
def update_figure(newspaper_id):
    df = df_big[df_big.source == newspaper_id].copy()
    return {
        'data': [go.Choropleth(
            locations=df['country_iso'],
            z=(df['count']/sum(df['count'])).round(3),
            text=df['country_name'],
            colorscale='Blues',
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title='relative counts',
        )],
        'layout': {
            'title': 'Country Appearences Heatmap for {}'.format(indicators_dict[newspaper_id]),
        }
    }


@app.callback(
    Output('updatable_bar_aligned', 'figure'),
    [Input('dropdown_map_aligned', 'value')])
def update_bar(newspaper_id):
    df_bar = df_big[df_big.source == newspaper_id].sort_values(by=['count'], ascending=False).copy()
    df_bar['rel_count']=(df_bar['count']/sum(df_bar['count'])).round(3)
    return {
        'data': [go.Bar(y=df_bar['country_name'].iloc[0:10], x=df_bar['rel_count'].iloc[0:10], orientation='h')],
        'layout': {
            'title': 'Relative numbers for popular countries'.format((indicators_dict[newspaper_id])),
            'xaxis': {'automargin': True, 'autorange': True},
            'yaxis': {'automargin': True, 'autorange': True}
        }
    }



@app.callback(
    Output('updatable_map_weighted', 'figure'),
    [Input('dropdown_map_weighted', 'value')])
def update_figure(newspaper_id):
    df = df_big[df_big.source == newspaper_id].copy()
    df = df[df.population > 1000000]
    df['weighted'] = df['count'] / df['population']
    df['weighted']=(df['weighted']/df['weighted'].sum()).round(4)
    return {
        'data': [go.Choropleth(
            locations=df['country_iso'],
            z=df['weighted'],
            text=df['country_name'],
            colorscale='Blues',
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title='relative counts',
        )],
        'layout': {
            'title': 'Country Appearences Heatmap for {}'.format(indicators_dict[newspaper_id]),
        }
    }


@app.callback(
    Output('updatable_bar_pie_aligned', 'figure'),
    [Input('dropdown_pie_aligned', 'value')])
def update_bar(newspaper_id):
    df_bar=df_big[df_big.source == newspaper_id].groupby('subregion').agg('sum').reset_index().sort_values(by=['count'], ascending=False).copy()
    df_bar['rel_count']=(df_bar['count']/sum(df_bar['count'])).round(3)
    return {
        'data': [go.Bar(x=df_bar['subregion'], y=df_bar['rel_count'])],
        'layout': {
            'title': 'Subregion Appearences for {} in relative numbers'.format((indicators_dict[newspaper_id])),
            'xaxis': {'automargin': True, 'autorange': True}
        }
    }


@app.callback(
    Output('updatable_pie_aligned', 'figure'),
    [Input('dropdown_pie_aligned', 'value')])
def update_pie(newspaper_id):
    df_pie=df_big[df_big.source == newspaper_id].groupby('region').agg('sum').reset_index()
    df_pie = df_pie[df_pie['count'] > 0]
    return {
        'data': [go.Pie(labels=df_pie.region, values=df_pie['count'], hole=.3, textinfo='label')],
        'layout': {
            'title': 'Country Appearences for {}'.format((indicators_dict[newspaper_id]))
        }
    }


@app.callback(
    Output('compare-graph', 'figure'),
    [Input('newspaper-selected1', 'value'),
     Input('newspaper-selected2', 'value')])
def update_compare(selected_newspaper1, selected_newspaper2):
    df_1 = df_big[df_big['source'] == selected_newspaper1].copy()
    df_1['norm_count'] = df_1['count'] / sum(df_1['count'])
    df_2 = df_big[df_big['source'] == selected_newspaper2].copy()
    df_2['norm_count'] = df_2['count'] / sum(df_2['count'])
    to_subset = list(df_1.sort_values(by=['norm_count']).iloc[-10:, :]['country_iso'])+list(df_2.sort_values(by=['norm_count']).iloc[-10:, :]['country_iso'])
    df_1 = df_1[df_1['country_iso'].isin(set(to_subset))]
    df_2 = df_2[df_2['country_iso'].isin(set(to_subset))]
    trace1 = go.Bar(x=df_1['country_name'], y=df_1['norm_count'], name=selected_newspaper1.title(), )
    trace2 = go.Bar(x=df_2['country_name'], y=df_2['norm_count'], name=selected_newspaper2.title(), )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            title=f'Relative number of top country mentions by {indicators_dict[selected_newspaper1]} and {indicators_dict[selected_newspaper2]}',
            colorway=["#EF963B", "#7f7f7f"], hovermode="closest",
            xaxis={'tickfont': {'size': 9, 'color': 'black'}},
            yaxis={'title': "Relative number of mentions", 'titlefont': {'color': 'black', 'size': 14, },
                   'tickfont': {'color': 'black'}})}


app.run_server(host='0.0.0.0',debug=True)

