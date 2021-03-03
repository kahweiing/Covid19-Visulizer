import numpy as np
from flask import render_template
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pop
import plotly.express as px
import pycountry


# Get the three-letter country codes for each country
def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

#Plot the Covid-19 World Map
def plotWorldMap():
    df_confirm = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df_confirm = df_confirm.drop(columns=['Province/State', 'Lat', 'Long'])
    df_confirm = df_confirm.groupby('Country/Region').agg('sum')

    date_list = list(df_confirm.columns)
    df_confirm['country'] = df_confirm.index
    df_confirm['code'] = df_confirm['country'].apply(get_country_code)

    # Transform the dataset in a long format
    df_long = pd.melt(df_confirm, id_vars=['country', 'code'], value_vars=date_list, var_name='Date')
    fig = px.choropleth(df_long,  # Input Dataframe
                       locations="code",  # identify country code column
                        color="value",  # identify representing column
                        hover_name="country",  # identify hover name
                        animation_frame="Date",  # identify date column
                        projection="natural earth",  # select projection
                        color_continuous_scale='Peach',  # select prefer color scale
                       range_color=[0, 50000]  # select range of dataset
                        )
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    content = pop.to_html(fig)

    #Get Top 5 Covid Country
    covid_df = pd.read_csv("./csv/covid-19-dataset-2.csv")
    covid_country = covid_df.groupby('Country_Region').sum()[['Confirmed']]
    coviddf = (covid_country.nlargest(5, 'Confirmed'))
    pairs = [(country, confirmed) for country,confirmed in zip(coviddf.index, coviddf['Confirmed'])]

    return render_template("Worldmap.html", content=content, table=coviddf, pairs=pairs)

# PLot bar Chart
def plotBarChart(statementlist,mainBranches,df,titlelist,x_axistitle):
    counter = 0
    data = []
    for datapoint in statementlist:
        data.append(go.Bar(
            x=mainBranches,
            y=getattr(df, datapoint),
            name=titlelist[counter]
        ))
        counter += 1
    layout = go.Layout(
        barmode='group',
        autosize=True,
        width=1200,
        height=800,
        hovermode="x unified",
        xaxis=dict(
        title=x_axistitle
        )
    )
    config = {
        'scrollZoom': True
    }
    fig = go.Figure(data=data, layout=layout)
    bar = pop.to_html(fig, config=config)
    return bar


# PLot line Chart
def plotLineChart(statementlist,mainBranches,df,titlelist,x_axistitle):
    lineCounter = 0
    dataLine = []
    for datapoint in statementlist:
        dataLine.append(go.Scatter(
            x=mainBranches,
            y=getattr(df, datapoint),
            name=titlelist[lineCounter],
            mode='lines'
        ))
        lineCounter += 1
    layoutLine = go.Layout(
        autosize=True,
        width=1200,
        height=800,
        hovermode="x unified",
        xaxis=dict(
        title=x_axistitle
        )
    )
    configLine = {
        'scrollZoom': True
    }
    figLine = go.Figure(data=dataLine, layout=layoutLine)
    line = pop.to_html(figLine, config=configLine)
    return line

# PLot Stack Chart
def plotStackChart(statementlist,mainBranches,df,titlelist,x_axistitle):
    stackCounter = 0
    dataStack = []
    for datapoint in statementlist:
        dataStack.append(go.Bar(
            x=mainBranches,
            y=getattr(df, datapoint),
            name=titlelist[stackCounter]
        ))
        stackCounter += 1
    layoutStack = go.Layout(
        barmode='relative',
        autosize=True,
        width=1200,
        height=800,
        hovermode="x unified",
        xaxis=dict(
        title=x_axistitle
        )
    )
    configStack = {
        'scrollZoom': True
    }
    figStack = go.Figure(data=dataStack, layout=layoutStack)
    stack = pop.to_html(figStack, config=configStack)
    return stack