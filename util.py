from tracemalloc import start
from typing import Any
import pandas as pd
import datetime

def preprocessing(df):

    df['y'] = df.iloc[:, 4]
    df['ds'] = df.iloc[:, 2]
    rest = df.drop(['y', 'ds'], axis=1)
    df.drop(rest, inplace=True, axis=1)
    df['ds'].drop_duplicates(inplace=True)
    df['ds'] = pd.to_datetime(df['ds'], format='%m-%d-%Y %I:%M %p')
    df.sort_values(by=['ds'], inplace=True)
    df.dropna(inplace=True)
    df.reset_index(inplace=True, drop=True)

    return df

def filter_data(df: pd.DataFrame, time_range: str, week_day: str, start_time: str, end_time):

    time = df['ds']
    df['day_of_week'] = time.dt.day_name()
    df['Day'] = time.dt.day
    df.index = df['ds']
    last_date = df['ds'][-1]

    if time_range == '2 weeks':
        starter = last_date-datetime.timedelta(days=14)
        mask = (df['ds'] > starter) & (df['ds'] <= last_date)
        df = df.loc[mask]
    if time_range == '1 month':
        starter = last_date-datetime.timedelta(days=30)
        mask = (df['ds'] > starter) & (df['ds'] <= last_date)
        df = df.loc[mask]
    if time_range == '3 months':
        starter = last_date-datetime.timedelta(days=90)
        mask = (df['ds'] > starter) & (df['ds'] <= last_date)
        df = df.loc[mask]
    if time_range == '6 months':
        starter = last_date-datetime.timedelta(days=180)
        mask = (df['ds'] > starter) & (df['ds'] <= last_date)
        df = df.loc[mask]
    if time_range == '1 year':
        starter = last_date-datetime.timedelta(days=365)
        mask = (df['ds'] > starter) & (df['ds'] <= last_date)
        df = df.loc[mask]
    if time_range == 'All times':
        df = df
    if week_day != 'Every Day':
        df = df.loc[df['day_of_week'] == week_day]
    if end_time is not None:
        df = df.between_time(start_time, end_time)

    return df

