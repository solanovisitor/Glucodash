import streamlit as st
import pandas as pd
from datetime import time
from util import preprocessing, filter_data
from metrics import available_data, average_glucose, time_in_range, eA1c, hyper_time, hypo_time, sd, inter_qr

def main():

    st.title('Dynamic Ambulatory Glucose Profile (dAGP)')
    st.subheader('Input your Libre data and select your filters below')
    data = st.file_uploader('Upload the glucose data downloaded from the LibreView website', type='csv')
    if data is not None:
        df = pd.read_csv(data, low_memory=False, delimiter=',', skiprows=1)
        df = preprocessing(df)
    units = ['mg/dL', 'mmol/L']
    ranges = ['All times', '2 weeks', '1 month', '3 months', '6 months', '1 year']
    day_names = ['Every Day', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    boolean = ['Yes', 'No']
    unit = st.radio('Select the unit of choice', units)
    time_range = st.selectbox('Select the amount of time for your analysis', ranges)
    week_day = st.selectbox('Filter by day of week', day_names)
    whole_day = st.radio('Do you want to select a time range?', boolean)
    if whole_day == 'Yes':
        hours = st.slider(
        "Select the desired time range:",
        value=(time(7, 00), time(9, 00)))
        start_time, end_time = hours
    else:
        start_time = None
        end_time = None

    if data is not None:
        filtered_df = filter_data(df, time_range, week_day, start_time, end_time)

        col1, col2, col3, col4 = st.columns(4)

        n_data = available_data(filtered_df)
        avg = average_glucose(filtered_df)
        std = sd(filtered_df)
        ea1c = round(eA1c(filtered_df), 2)
        trange = f'{time_in_range(filtered_df, n_data)}%'
        thyper = f'{hyper_time(filtered_df, n_data)}%'
        thypo = f'{hypo_time(filtered_df, n_data)}%'
        iqr = inter_qr(filtered_df)

        col1.metric(label="Number of measurements", value=n_data)
        col2.metric(label="Average Glucose", value=avg)
        col3.metric(label="Standard Deviation", value=std)
        col4.metric(label="Estimated A1c", value=ea1c)
        col1.metric(label="Time in range", value=trange)
        col2.metric(label='Time in hyper', value=thyper)
        col3.metric(label='Time in hypo', value=thypo)
        col4.metric(label='Interquartile range', value=iqr)

if __name__ == '__main__':
    main()