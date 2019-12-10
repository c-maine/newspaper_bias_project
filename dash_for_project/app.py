#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

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

db = sql.create_engine(
    'mysql+pymysql://admin:datawarehousing@database-1.cl6uila8iago.eu-central-1.rds.amazonaws.com:3306/news_db')
metadata = MetaData()
articles = Table('articles_tab_news', metadata, autoload=True, autoload_with=db)
countries = Table('countries_tab', metadata, autoload=True, autoload_with=db)
counts = Table('count_tab_news', metadata, autoload=True, autoload_with=db)


Session = sessionmaker(bind=db)
session = Session()
df_big = pd.read_sql(session.query(counts.c.count,countries.c.country_name, countries.c.country_iso, countries.c.region,
                                   counts.c.source, counts.c.count).join(countries,countries.c.country_iso==counts.c.country_iso).statement, session.bind)
# deal with a non-defined region
df_big[df_big.region!='']
available_indicators = df_big['source'].unique()

app = dash.Dash('dash-tutorial')

app.layout = html.Div(className='layout', children=[
    html.H1(className='title', children='How newspapers report about countries'),
    html.H4('Select a newspaper and discover!', className='subtitle', style={'font-size': '2em'}),

    html.Div(id='dropdown_div', children=[
        html.H2('Heatmap - countrywise', className='subtitle', style={'color': 'white', 'font-size': '2em'}),
        dcc.Dropdown(
            id='dropdown_map',
            options=[{'label': i, 'value': i} for i in available_indicators],
            value='the-new-york-times'
        ),
        dcc.Graph(id='updatable_graph')
    ],
             className='plots'
             ),

    html.Div(id='bar_div', children=[
        html.H2('Barplot - countrywise', className='subtitle', style={'color': 'white', 'font-size': '2em'}),
        dcc.Dropdown(
            id='dropdown_bar',
            options=[{'label': i, 'value': i} for i in available_indicators],
            value='the-new-york-times'
        ),
        dcc.Graph(id='updatable_bar', ),
    ],
             className='plots'
             ),

    html.Div([html.Div([
        html.Div([html.H2('Compare two Newspapers', className='subtitle', style={'color': 'white', 'font-size': '2em'})]),
        html.Div([
            dcc.Dropdown(id='newspaper-selected1',
                         options=[{'label': i, 'value': i} for i in available_indicators],
                         value='the-new-york-times')],
            className="dropdowner",
            style={"width": "40%", "float": "right"}
        ),
        html.Div([dcc.Dropdown(id='newspaper-selected2',
                               options=[{'label': i, 'value': i} for i in available_indicators],
                               value='aljazeera.com')],
                 className="dropdowner_2",
                 style={"width": "40%", "float": "left"})],
        className="row",
        style={"padding": 50, "width": "60%", "margin-left": "auto", "margin-right": "auto"}),

        dcc.Graph(id='compare-graph')],
        className='plots'),

    html.Div(id='pie_chart', children=[
        html.H2('Continent-wise', className='subtitle', style={'color': 'white', 'font-size': '2em'}),

        dcc.Dropdown(
            id='pie_dropdown',
            options=[{'label': i, 'value': i} for i in available_indicators],
            value='the-new-york-times'
        ),
        dcc.Graph(id='pie_graph')
    ],
             className='plots'),

])


@app.callback(
    Output('updatable_graph', 'figure'),
    [Input('dropdown_map', 'value')])
def update_figure(newspaper_id):
    df = df_big[df_big.source == newspaper_id].copy()
    return {
        'data': [go.Choropleth(
            locations=df['country_iso'],
            z=df['count'],
            text=df['country_name'],
            colorscale='Blues',
            autocolorscale=True,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title='Total counts',
        )],
        'layout': {
            'title': 'Country Appearences Heatmap for {}'.format(newspaper_id),
        }
    }


@app.callback(
    Output('updatable_bar', 'figure'),
    [Input('dropdown_bar', 'value')])
def update_bar(newspaper_id):
    df_bar = df_big[df_big.source == newspaper_id].sort_values(by=['count'], ascending=False).copy()
    return {
        'data': [go.Bar(x=df_bar['country_name'].iloc[0:10], y=df_bar['count'].iloc[0:10])],
        'layout': {
            'title': 'Country Appearences for {}'.format(newspaper_id)
        }
    }


@app.callback(
    Output('pie_graph', 'figure'),
    [Input('pie_dropdown', 'value')])
def update_pie(newspaper_id):
    # df_pie = df_big[df_big.source == newspaper_id].groupby('region').sum().reset_index().copy()
    df_pie=df_big[df_big.source == newspaper_id].groupby('region').agg('sum').reset_index()
    return {
        'data': [go.Pie(labels=df_pie.region, values=df_pie['count'], hole=.3, textinfo='label')],
        'layout': {
            'title': 'Country Appearences for {}'.format(newspaper_id)
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
    trace1 = go.Bar(x=df_1['country_name'], y=df_1['norm_count'], name=selected_newspaper1.title(), )
    trace2 = go.Bar(x=df_2['country_name'], y=df_2['norm_count'], name=selected_newspaper2.title(), )

    return {
        'data': [trace1, trace2],
        'layout': go.Layout(
            title=f'Relative number of country mentions by : {selected_newspaper1.title()}, {selected_newspaper2.title()}',
            colorway=["#EF963B", "#7f7f7f"], hovermode="closest",
            xaxis={'title': "Country mentioned", 'titlefont': {'color': 'black', 'size': 14},
                   'tickfont': {'size': 9, 'color': 'black'}},
            yaxis={'title': "Number of mentions", 'titlefont': {'color': 'black', 'size': 14, },
                   'tickfont': {'color': 'black'}})}


app.run_server(debug=True)

