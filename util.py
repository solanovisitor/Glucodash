# from pycaret.anomaly import *
import pandas as pd
pd.options.mode.chained_assignment = None
import datetime
import streamlit as st
import numpy as np
from scipy.stats import iqr
import plotly.express as px
import plotly.graph_objects as go

class FinalData:

    def __init__(self, data, device: str, time_range: str, week_day: str, start_time: str, end_time):
        self.data = data
        self.device = device
        self.time_range = time_range
        self.week_day = week_day
        self.start_time = start_time
        self.end_time = end_time

    def preprocessing(self):

        device_dict = {'Freestyle Libre': [4, 2], 'Dexcom': [7, 1], 'Nightscout': [-2, 3]}
        if self.device != 'Nightscout':
            try:
                df = pd.read_csv(self.data, delimiter=',', skiprows=1)
                df['y'] = df.iloc[:, device_dict[self.device][0]]
                df['ds'] = df.iloc[:, device_dict[self.device][1]]
            except:
                st.error('Your data does not match with the specified device. Please check above.')
                st.stop()
        else:
            try:
                df = pd.read_csv(self.data, low_memory=False, delimiter=';', skiprows=1)
                df['y'] = df.iloc[:, device_dict[self.device][0]]
                df['ds'] = df.iloc[:, device_dict[self.device][1]]
            except:
                st.error('Your data does not match with the specified device. Please check above.')
                st.stop()
        if df['y'].mean() < 40:
            df['y'] = df['y'].apply(lambda x: x*18)
        rest = df.drop(['y', 'ds'], axis=1)
        df.drop(rest, inplace=True, axis=1)
        df['ds'].drop_duplicates(inplace=True)
        try:
            df['ds'] = pd.to_datetime(df['ds'])
        except:
            st.error('Your data does not match with the specified device. Please check above.')
            st.stop()
        df.sort_values(by=['ds'], inplace=True)
        df.dropna(inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df

    @property
    def filter_data(self):

        df = self.preprocessing()
        try:
            time = df['ds']
            df['day_of_week'] = time.dt.day_name()
            df['Day'] = time.dt.day
            df['Hour'] = time.dt.strftime('%H')
            df['dd_mm_yy'] = time.dt.strftime('%d/%m/%Y')
            df['hh_mm'] = time.dt.strftime('%H:%M')
            df.index = df['ds']
            last_date = df['ds'][-1]
        except:
            st.error('Your data is corruptded. Please check it for errors and be sure to upload the data immediatly after exported from the CGM website. If error continues, please contact us.')
            st.stop()

        ranges = {'2 weeks': 14, '1 month': 30, '3 months': 90, '6 months': 180, '1 year': 365}

        if self.time_range != 'All times':
            curr_range = ranges[self.time_range]
            starter = last_date-datetime.timedelta(days=curr_range)
            mask = (df['ds'] > starter) & (df['ds'] <= last_date)
            starter2 = starter-datetime.timedelta(days=curr_range)
            mask2 = (df['ds'] > starter2) & (df['ds'] <= starter)
            # st.dataframe(df[df.index.duplicated()])
            df1 = df.loc[mask]
            if mask2 is not None:
                df2 = df.loc[mask2]
            else:
                df2 = None
        if self.week_day != 'Every Day':
            df1 = df1.loc[df1['day_of_week'] == self.week_day]
            if df2 is not None:
                df2 = df2.loc[df2['day_of_week'] == self.week_day]
        if self.end_time is not None:
            df1 = df1.between_time(self.start_time, self.end_time)
            df2 = df2.between_time(self.start_time, self.end_time)

        start_date = df1['ds'][0]
        final_date = df1['ds'][-1]

        return df1, df2, start_date.strftime('%d/%m/%Y'), final_date.strftime('%d/%m/%Y')


class CgmMetric:

    def __init__(self, filtered_df):

        self.filtered_df = filtered_df

    def available_data(self):
        self.available_measurements = len(self.filtered_df)
        return int(self.available_measurements)

    def average_glucose(self):
        avg = self.filtered_df['y'].mean()
        return round(avg)

    def time_in_range(self):
        in_range = (self.filtered_df['y'] >= 70) & (self.filtered_df['y'] <= 180)
        in_range = self.filtered_df.loc[in_range]
        n_in_range = len(in_range)
        tir = (n_in_range / self.available_measurements) * 100
        return round(tir, 2)

    def hypo_time(self):
        in_hypo = (self.filtered_df['y'] < 70)
        in_hypo = self.filtered_df.loc[in_hypo]
        n_in_hypo = len(in_hypo)
        tihypo = (n_in_hypo / self.available_measurements) * 100
        return round(tihypo, 2)

    def hyper_time(self):
        in_hyper = (self.filtered_df['y'] > 180)
        in_hyper = self.filtered_df.loc[in_hyper]
        n_in_hyper = len(in_hyper)
        tihyper = (n_in_hyper / self.available_measurements) * 100
        return round(tihyper, 2)

    def sd(self):
        sd = self.filtered_df['y'].std()
        return round(sd, 2)

    def inter_qr(self):
        inter_qr = iqr(self.filtered_df['y'])
        return inter_qr

    def interdaycv(self):
        """
            Computes and returns the interday coefficient of variation of y
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                cvx (float): interday coefficient of variation averaged over all days
                
        """
        cvx = (np.std(self.filtered_df['y']) / (np.mean(self.filtered_df['y'])))*100
        return cvx

    def interdaysd(self):
        """
            Computes and returns the interday standard deviation of y
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                interdaysd (float): interday standard deviation averaged over all days
                
        """
        self.interdaysd = np.std(self.filtered_df['y'])
        return self.interdaysd

    def intradaycv(self):
        """
            Computes and returns the intraday coefficient of variation of y 
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                intradaycv_mean (float): intraday coefficient of variation averaged over all days
                intradaycv_medan (float): intraday coefficient of variation median over all days
                intradaycv_sd (float): intraday coefficient of variation standard deviation over all days
                
        """
        intradaycv = []
        for i in pd.unique(self.filtered_df['Day']):
            intradaycv.append(self.interdaycv(self.filtered_df[self.filtered_df['Day']==i]))
        
        intradaycv_mean = np.mean(intradaycv)
        intradaycv_median = np.median(intradaycv)
        intradaycv_sd = np.std(intradaycv)
        
        return intradaycv_mean, intradaycv_median, intradaycv_sd


    def intradaysd(self):
        """
            Computes and returns the intraday standard deviation of y 
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                intradaysd_mean (float): intraday standard deviation averaged over all days
                intradaysd_medan (float): intraday standard deviation median over all days
                intradaysd_sd (float): intraday standard deviation standard deviation over all days
                
        """
        intradaysd =[]

        for i in pd.unique(self.filtered_df['day_of_week']):
            intradaysd.append(np.std(self.filtered_df['y'][self.filtered_df['day_of_week']==i]))
        
        intradaysd_mean = np.mean(intradaysd)
        intradaysd_median = np.median(intradaysd)
        intradaysd_sd = np.std(intradaysd)
        return intradaysd_mean, intradaysd_median, intradaysd_sd

    def MAGE(self, std=1):
        """
            Mean amplitude of glycemic excursions (MAGE), together with mean and SD,
            is the most popular parameter for assessing glycemic variability and is calculated
            based on the arithmetic mean of differences between consecutive peaks and nadirs of
            differences greater than one SD of mean glycemia.
            It is designed to assess major glucose swings and exclude minor ones.

            Computes and returns the mean amplitude of y excursions
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
                sd (integer): standard deviation for computing range (default=1)
            Returns:
                MAGE (float): the mean amplitude of y excursions 
            Refs:
                Sneh Gajiwala: https://github.com/snehG0205/NCSA_genomics/tree/2bfbb87c9c872b1458ef3597d9fb2e56ac13ad64
                
        """
        
        #extracting y values and incdices
        y = self.filtered_df['y'].tolist()
        # ix = [1*i for i in range(len(y))]
        stdev = std
        
        # local minima & maxima
        # a = np.diff(np.sign(np.diff(y))).nonzero()[0] + 1      
        # local min
        valleys = (np.diff(np.sign(np.diff(y))) > 0).nonzero()[0] + 1 
        # local max
        peaks = (np.diff(np.sign(np.diff(y))) < 0).nonzero()[0] + 1         
        # +1 -- diff reduces original index number

        #store local minima and maxima -> identify + remove turning points
        excursion_points = pd.DataFrame(columns=['Index', 'ds', 'y', 'Type'])
        k=0
        for i in range(len(peaks)):
            excursion_points.loc[k] = [peaks[i]] + [self.filtered_df['ds'][k]] + [self.filtered_df['y'][k]] + ["P"]
            k+=1

        for i in range(len(valleys)):
            excursion_points.loc[k] = [valleys[i]] + [self.filtered_df['ds'][k]] + [self.filtered_df['y'][k]] + ["V"]
            k+=1

        excursion_points = excursion_points.sort_values(by=['Index'])
        excursion_points = excursion_points.reset_index(drop=True)


        # selecting turning points
        turning_points = pd.DataFrame(columns=['Index', 'ds', 'y', 'Type'])
        k=0
        for i in range(stdev,len(excursion_points.Index)-stdev):
            positions = [i-stdev,i,i+stdev]
            for j in range(0,len(positions)-1):
                if(excursion_points.Type[positions[j]] == excursion_points.Type[positions[j+1]]):
                    if(excursion_points.Type[positions[j]]=='P'):
                        if excursion_points.y[positions[j]]>=excursion_points.y[positions[j+1]]:
                            turning_points.loc[k] = excursion_points.loc[positions[j+1]]
                            k+=1
                        else:
                            turning_points.loc[k] = excursion_points.loc[positions[j+1]]
                            k+=1
                    else:
                        if excursion_points.y[positions[j]]<=excursion_points.y[positions[j+1]]:
                            turning_points.loc[k] = excursion_points.loc[positions[j]]
                            k+=1
                        else:
                            turning_points.loc[k] = excursion_points.loc[positions[j+1]]
                            k+=1

        if len(turning_points.index)<10:
            turning_points = excursion_points.copy()
            excursion_count = len(excursion_points.index)
        else:
            excursion_count = len(excursion_points.index)/2


        turning_points = turning_points.drop_duplicates(subset= "Index", keep= "first")
        turning_points=turning_points.reset_index(drop=True)
        excursion_points = excursion_points[excursion_points.Index.isin(turning_points.Index) == False]
        excursion_points = excursion_points.reset_index(drop=True)

        # calculating MAGE
        mage = turning_points.y.sum()/excursion_count
        
        return round(mage,3)

    def J_index(self):
        """
            J index is a measure of quality of glycemic control based on
            the combination of information from the mean and SD calculated as 0.001 x (mean + SD)

            Computes and returns the J-index
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                J (float): J-index of y
                
        """
        J = 0.001*((np.mean(self.filtered_df['y'])+np.std(self.filtered_df['y']))**2)
        return J

    def LBGI_HBGI(self, i):
        """
            Connecter function to calculate rh and rl, used for ADRR function
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                LBGI (float): Low blood y index
                HBGI (float): High blood y index
                rl (float): See calculation of LBGI
                rh (float): See calculation of HBGI
                
        """
        self.filtered_df = self.filtered_df[self.filtered_df['Day']==i]
        f = ((np.log(self.filtered_df['y'])**1.084) - 5.381)
        self.rl = []
        for i in f: 
            if (i <= 0):
                self.rl.append(22.77*(i**2))
            else:
                self.rl.append(0)

        self.LBGI = np.mean(self.rl)

        self.rh = []
        for i in f: 
            if (i > 0):
                self.rh.append(22.77*(i**2))
            else:
                self.rh.append(0)

        self.HBGI = np.mean(self.rh)
        
        return self.LBGI, self.HBGI, self.rh, self.rl

    def LBGI(self):
        """
            Computes and returns the low blood y index
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                LBGI (float): Low blood y index
                
        """
        f = ((np.log(self.filtered_df['y'])**1.084) - 5.381)
        rl = []
        for i in f: 
            if (i <= 0):
                rl.append(22.77*(i**2))
            else:
                rl.append(0)

        LBGI = np.mean(rl)
        return LBGI

    def HBGI(self):
        """
            Computes and returns the high blood y index
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                HBGI (float): High blood y index
                
        """
        f = ((np.log(self.filtered_df['y'])**1.084) - 5.381)
        rh = []
        for i in f: 
            if (i > 0):
                rh.append(22.77*(i**2))
            else:
                rh.append(0)

        HBGI = np.mean(rh)
        return HBGI

    def ADRR(self):
        """
            Computes and returns the average daily risk range, an assessment of total daily y variations within risk space
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                ADRRx (float): average daily risk range
                
        """
        ADRRl = []
        for i in pd.unique(self.filtered_df['Day']):
            self.LBGI, self.HBGI, self.rh, self.rl = self.LBGI_HBGI(i)
            LR = np.max(self.rl)
            HR = np.max(self.rh)
            ADRRl.append(LR+HR)

        ADRRx = np.mean(ADRRl)
        return ADRRx

    def uniquevalfilter(self, value):
        """
            Supporting function for MODD and CONGA24 functions
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
                value (datetime): time to match up with previous 24 hours
            Returns:
                MODD_n (float): Best matched with unique value, value
                
        """
        xdf = self.filtered_df[self.filtered_df['Minfrommid'] == value]
        # n = len(xdf)
        diff = abs(xdf['y'].diff())
        self.MODD_n = np.nanmean(diff)
        return self.MODD_n

    def MODD(self):
        """
            Computes and returns the mean of daily differences. Examines mean of value + value 24 hours before
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Requires:
                uniquevalfilter (function)
            Returns:
                MODD (float): Mean of daily differences
                
        """
        self.filtered_df['Timefrommidnight'] =  self.filtered_df['ds'].dt.time
        lists=[]
        for i in range(0, len(self.filtered_df['Timefrommidnight'])):
            lists.append(int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[0:2])*60 + int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[3:5]) + round(int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[6:9])/60))
        self.filtered_df['Minfrommid'] = lists
        self.filtered_df = self.filtered_df.drop(columns=['Timefrommidnight'])
        
        #Calculation of MODD and CONGA:
        MODD_n = []
        uniquetimes = self.filtered_df['Minfrommid'].unique()

        for i in uniquetimes:
            MODD_n.append(self.uniquevalfilter(i))
        
        #Remove zeros from dataframe for calculation (in case there are random unique values that result in a mean of 0)
        MODD_n[MODD_n == 0] = np.nan
        
        MODD = np.nanmean(MODD_n)
        return MODD

    def CONGA24(self):
        """
            Computes and returns the continuous overall net glycemic action over 24 hours
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Requires:
                uniquevalfilter (function)
            Returns:
                CONGA24 (float): continuous overall net glycemic action over 24 hours
                
        """
        self.filtered_df['Timefrommidnight'] =  self.filtered_df['ds'].dt.time
        lists=[]
        for i in range(0, len(self.filtered_df['Timefrommidnight'])):
            lists.append(int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[0:2])*60 + int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[3:5]) + round(int(self.filtered_df['Timefrommidnight'][i].strftime('%H:%M:%S')[6:9])/60))
        self.filtered_df['Minfrommid'] = lists
        self.filtered_df = self.filtered_df.drop(columns=['Timefrommidnight'])
        
        #Calculation of MODD and CONGA:
        MODD_n = []
        uniquetimes = self.filtered_df['Minfrommid'].unique()

        for i in uniquetimes:
            MODD_n.append(self.uniquevalfilter(i))
        
        #Remove zeros from dataframe for calculation (in case there are random unique values that result in a mean of 0)
        MODD_n[MODD_n == 0] = np.nan
        
        CONGA24 = np.nanstd(MODD_n)
        return CONGA24

    def GMI(self):
        """
            Computes and returns the y management index
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                GMI (float): y management index (an estimate of HbA1c)
                
        """
        GMI = 3.31 + (0.02392*np.mean(self.filtered_df['y']))
        return GMI

    def eA1c(self):
        """
            Computes and returns the American Diabetes Association estimated HbA1c
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                eA1c (float): an estimate of HbA1c from the American Diabetes Association
                
        """
        eA1c = (46.7 + np.mean(self.filtered_df['y']))/ 28.7 
        return eA1c

    def summary(self): 
        """
            Computes and returns y summary metrics
            Args:
                (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            Returns:
                meanG (float): interday mean of y
                medianG (float): interday median of y
                minG (float): interday minimum of y
                maxG (float): interday maximum of y
                Q1G (float): interday first quartile of y
                Q3G (float): interday third quartile of y
                
        """
        meanG = np.nanmean(self.filtered_dfdf['y'])
        medianG = np.nanmedian(self.filtered_df['y'])
        minG = np.nanmin(self.filtered_df['y'])
        maxG = np.nanmax(self.filtered_df['y'])
        Q1G = np.nanpercentile(self.filtered_df['y'], 25)
        Q3G = np.nanpercentile(self.filtered_df['y'], 75)
        
        return meanG, medianG, minG, maxG, Q1G, Q3G

    def best_day(self):
        grouped_by_day = self.filtered_df.groupby('dd_mm_yy').mean()
        grouped_by_day = grouped_by_day.assign(Best_Day = lambda x: (3.31 + (0.02392*(x['y']))))
        best_day = grouped_by_day['y'].idxmin()

        return best_day

    def histogram(self):
        # Add histogram data

        in_range = (self.filtered_df['y'] >= 70) & (self.filtered_df['y'] <= 180)
        in_range = self.filtered_df.loc[in_range]
        in_range['Range'] = 'In range'

        in_hypo = (self.filtered_df['y'] < 70)
        in_hypo = self.filtered_df.loc[in_hypo]
        in_hypo['Range'] = 'Hypoglicemia'

        in_hyper = (self.filtered_df['y'] > 180)
        in_hyper = self.filtered_df.loc[in_hyper]
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

    def scatter(self):

        # create a blank canvas
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=self.filtered_df['ds']
                , y=self.filtered_df['y']
                , name='Glucose'
                , line=dict(color='royalblue', width=.7)
            ))
        
        #px.scatter(df, x=df['ds'], y=df['y'])
        # extract points as plain x and y
        fig.add_hline(y=180, line_color='red')
        fig.add_hline(y=70, line_color='red')

        help_fig = px.scatter(self.filtered_df, x=self.filtered_df['ds'], y=self.filtered_df['y'], trendline="lowess", trendline_options=dict(frac=0.1))
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

    def one_day_scatter(self):

        self.filtered_df.reset_index(drop=True, inplace=True)
        mean_df = self.filtered_df.groupby('hh_mm').mean()
        mean_df.reset_index(drop=False, inplace=True)
        mean_df['hh_mm'] = pd.to_datetime(mean_df['hh_mm'])
        std_df = self.filtered_df.groupby('hh_mm').std()
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