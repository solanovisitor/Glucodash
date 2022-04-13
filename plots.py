from unicodedata import name
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def histogram(df: pd.DataFrame):
    # Add histogram data

    in_range = (df['y'] >= 70) & (df['y'] <= 180)
    in_range = df.loc[in_range]
    in_range['Range'] = 'In range'

    in_hypo = (df['y'] < 70)
    in_hypo = df.loc[in_hypo]
    in_hypo['Range'] = 'Hypoglicemia'

    in_hyper = (df['y'] > 180)
    in_hyper = df.loc[in_hyper]
    in_hyper['Range'] = 'Hyperglicemia'

    data = pd.concat([in_hypo, in_range])
    data = pd.concat([data, in_hyper])

    fig = px.histogram(data, x="day_of_week", color="Range", barnorm='percent', title="Histogram of range frequencies",
                       color_discrete_sequence=['#f54266', '#38cf77', '#4287f5']).update_xaxes(categoryorder='array',
                       categoryarray= ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).update_layout(yaxis_title="Percentage on ranges",
                       xaxis_title='Day of Week', hovermode='x unified')
    # Plot!
    st.plotly_chart(fig, use_container_width=True)

def scatter(df: pd.DataFrame):

    # create a blank canvas
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
              x=df['ds']
            , y=df['y']
            , name='Glucose'
        ))
    
    #px.scatter(df, x=df['ds'], y=df['y'])
    # extract points as plain x and y
    fig.add_hline(y=180, line_color='red')
    fig.add_hline(y=70, line_color='red')

    help_fig = px.scatter(df, x=df['ds'], y=df['y'], trendline="lowess", trendline_options=dict(frac=0.1))
    # extract points as plain x and y
    x_trend = help_fig["data"][1]['x']
    y_trend = help_fig["data"][1]['y']
    
        # add the x,y data as a scatter graph object
    fig.add_trace(
        go.Scatter(x=x_trend, y=y_trend, name='Glucose trend'))

    transparent = 'rgba(0,0,0,0)'

    fig.update_layout(
    hovermode='x',
    showlegend=True
    # , title_text=str('Court Data for ' + str(year))
    , paper_bgcolor=transparent
    , plot_bgcolor=transparent
    , title='Glucose along with limits and trend'
    )


    st.plotly_chart(fig, use_container_width=True)