import streamlit as st
import pandas as pd
from datetime import time
from util import preprocessing, filter_data

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
        st.dataframe(filtered_df)

if __name__ == '__main__':
    main()