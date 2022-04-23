# from pycaret.anomaly import *
import pandas as pd
import datetime
import streamlit as st

class FinalData:

    def __init__(self, data, device: str):
        self.data = data
        self.device = device

    def preprocessing(self):

        device_dict = {'Freestyle Libre': [4, 2], 'Dexcom': [7, 1], 'Nightscout': [-2, 3]}
        if self.device != 'Nightscout':
            try:
                df = pd.read_csv(self.data, low_memory=False, delimiter=',', skiprows=1, on_bad_lines='skip')
            except:
                st.error('Your data does not match with the specified device. Please check above.')
        else:
            try:
                df = pd.read_csv(self.data, low_memory=False, delimiter=';', skiprows=1, on_bad_lines='skip')
            except:
                st.error('Your data does not match with the specified device. Please check above.')
        try:
            df['y'] = df.iloc[:, device_dict[self.device][0]]
            df['ds'] = df.iloc[:, device_dict[self.device][1]]
        except:
            st.error('Your data does not match with the specified device. Please check above.')
            st.stop()
        rest = df.drop(['y', 'ds'], axis=1)
        df.drop(rest, inplace=True, axis=1)
        df['ds'].drop_duplicates(inplace=True)
        if self.device == 'Freestyle Libre':
            try:
                df['ds'] = pd.to_datetime(df['ds'], format='%m-%d-%Y %I:%M %p')
            except:
                st.error('Your data does not match with the specified device. Please check above.')
                st.stop()
        else:
            try:
                df['ds'] = pd.to_datetime(df['ds'])
            except:
                st.error('Your data does not match with the specified device. Please check above.')
                st.stop()
        df.sort_values(by=['ds'], inplace=True)
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df

    @staticmethod
    def filter_data(df: pd.DataFrame, time_range: str, week_day: str, start_time: str, end_time):

        time = df['ds']
        df['day_of_week'] = time.dt.day_name()
        df['Day'] = time.dt.day
        df['Hour'] = time.dt.strftime('%H')
        df['dd_mm_yy'] = time.dt.strftime('%d/%m/%Y')
        df['hh_mm'] = time.dt.strftime('%H:%M')
        df.index = df['ds']
        last_date = df['ds'][-1]

        ranges = {'2 weeks': 14, '1 month': 30, '3 months': 90, '6 months': 180, '1 year': 365}

        if time_range != 'All times':
            curr_range = ranges[time_range]
            starter = last_date-datetime.timedelta(days=curr_range)
            mask = (df['ds'] > starter) & (df['ds'] <= last_date)
            df = df.loc[mask]
        if week_day != 'Every Day':
            df = df.loc[df['day_of_week'] == week_day]
        if end_time is not None:
            df = df.between_time(start_time, end_time)

        return df
