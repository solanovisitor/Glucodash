import streamlit as st
import pandas as pd
pd.options.mode.chained_assignment = None
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

    fig.update_traces(opacity=0.75, marker_line_width=.8, marker_line_color="white", marker_opacity=0.75)

    transparent = 'rgba(0,0,0,0)'

    fig.update_layout(yaxis = dict(showgrid=False),
                      #paper_bgcolor=transparent)
                      plot_bgcolor=transparent)

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
            , line=dict(color='royalblue', width=.7)
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
    yaxis_title='Glucose (mg/dL)',
    hovermode='x',
    showlegend=True
    # , title_text=str('Court Data for ' + str(year))
    , paper_bgcolor=transparent
    , plot_bgcolor=transparent
    , title='Glucose along with trends and limits'
    )

    fig.update_layout(
                        xaxis = dict(
                            type = 'category',
                            showgrid=True,
                            ticks="outside",
                            tickson="boundaries",
                            ticklen=1,
                            visible=False
                        ),
                        yaxis = dict(showgrid=False)
                    )

    st.plotly_chart(fig, use_container_width=True)

def one_day_scatter(df: pd.DataFrame):

    df.reset_index(drop=True, inplace=True)
    mean_df = df.groupby('hh_mm').mean()
    mean_df.reset_index(drop=False, inplace=True)
    mean_df['hh_mm'] = pd.to_datetime(mean_df['hh_mm'])
    std_df = df.groupby('hh_mm').std()
    std_df.reset_index(drop=False, inplace=True)
    std_df['hh_mm'] = pd.to_datetime(std_df['hh_mm'])

    # create a blank canvas
    fig = go.Figure()

    fig.add_hline(y=140, line_color='purple')
    fig.add_hline(y=100, line_color='purple')

    help_fig = px.scatter(mean_df, x=mean_df['hh_mm'], y=mean_df['y'], trendline="lowess", trendline_options=dict(frac=0.1))
    help_fig2 = px.scatter(mean_df, x=mean_df['hh_mm'], y=mean_df['y']+std_df['y'], trendline="lowess", trendline_options=dict(frac=0.1))
    help_fig3 = px.scatter(mean_df, x=mean_df['hh_mm'], y=mean_df['y']-std_df['y'], trendline="lowess", trendline_options=dict(frac=0.1))

    # extract points as plain x and y
    x_trend = help_fig["data"][1]['x']
    y_trend = help_fig["data"][1]['y']

    upper_x_trend = help_fig2["data"][1]['x']
    upper_y_trend = help_fig2["data"][1]['y']

    lower_x_trend = help_fig3["data"][1]['x']
    lower_y_trend = help_fig3["data"][1]['y']

        # add the x,y data as a scatter graph object
    fig.add_trace(
        go.Scatter(x=x_trend,
                   y=y_trend,
                   name='Mean Band'))

    fig.add_trace(
        go.Scatter(x=upper_x_trend,
                   y=upper_y_trend,
                   name='Upper Band'))

    fig.add_trace(
        go.Scatter(x=lower_x_trend, 
                   y=lower_y_trend,
                   name='Lower Band',
                   fillcolor='rgba(68, 68, 68, 0.3)',
                   fill='tonexty'))

    transparent = 'rgba(0,0,0,0)'

    fig.update_layout(
        yaxis_title='Glucose (mg/dL)',
        hovermode="x",
        paper_bgcolor=transparent,
        plot_bgcolor=transparent,
        title='One-day aggregated measures - smoothed mean and standard deviation'

    )

    fig.update_layout(xaxis_tickformat = '%H:%M', yaxis = dict(showgrid=False))

    st.plotly_chart(fig, use_container_width=True)