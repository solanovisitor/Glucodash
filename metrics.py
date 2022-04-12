import pandas as pd
import datetime as datetime
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
from scipy.stats import iqr

"""
    Requirements:
    pandas, datetime, numpy, matplotlib, statsmodels

    Functions:
    available_data(): Number of data points (glucose measurements)
    interdaycv(): Computes and returns the interday coefficient of variation of glucose
    interdaysd(): Computes and returns the interday standard deviation of glucose
    intradaycv(): Computes and returns the intraday coefficient of variation of glucose 
    intradaysd(): Computes and returns the intraday standard deviation of glucose 
    MAGE(): Computes and returns the mean amplitude of glucose excursions
    J_index(): Computes and returns the J-index
    LBGI(): Computes and returns the low blood glucose index
    HBGI(): Computes and returns the high blood glucose index
    ADRR(): Computes and returns the average daily risk range, an assessment of total daily glucose variations within risk space
    MODD(): Computes and returns the mean of daily differences. Examines mean of value + value 24 hours before
    CONGA24(): Computes and returns the continuous overall net glycemic action over 24 hours
    GMI(): Computes and returns the glucose management index
    eA1c(): Computes and returns the American Diabetes Association estimated HbA1c
    summary(): Computes and returns glucose summary metrics, including interday mean y, interday median y, interday minimum y, interday maximum y, interday first quartile y, and interday third quartile glucose
    plotysd(): Plots glucose with specified standard deviation lines
    plotybounds(): Plots glucose with user-defined boundaries
    plotysmooth(): Plots smoothed glucose plot (with LOWESS smoothing)
            
"""

def available_data(df: pd.DataFrame):
    available_measurements = len(df)
    return int(available_measurements)

def average_glucose(df: pd.DataFrame):
    avg = df['y'].mean()
    return round(avg)

def time_in_range(df: pd.DataFrame, available_measurements: int):
    in_range = (df['y'] >= 70) & (df['y'] <= 180)
    in_range = df.loc[in_range]
    n_in_range = len(in_range)
    tir = (n_in_range / available_measurements) * 100
    return round(tir, 2)

def hypo_time(df: pd.DataFrame, available_measurements: int):
    in_hypo = (df['y'] < 70)
    in_hypo = df.loc[in_hypo]
    n_in_hypo = len(in_hypo)
    tihypo = (n_in_hypo / available_measurements) * 100
    return round(tihypo, 2)

def hyper_time(df: pd.DataFrame, available_measurements: int):
    in_hyper = (df['y'] > 180)
    in_hyper = df.loc[in_hyper]
    n_in_hyper = len(in_hyper)
    tihyper = (n_in_hyper / available_measurements) * 100
    return round(tihyper, 2)

def sd(df: pd.DataFrame):
    sd = df['y'].std()
    return round(sd, 2)

def inter_qr(df: pd.DataFrame):
    inter_qr = iqr(df['y'])
    return inter_qr

def interdaycv(df: pd.DataFrame):
    """
        Computes and returns the interday coefficient of variation of y
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            cvx (float): interday coefficient of variation averaged over all days
            
    """
    cvx = (np.std(df['y']) / (np.mean(df['y'])))*100
    return cvx

def interdaysd(df):
    """
        Computes and returns the interday standard deviation of y
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            interdaysd (float): interday standard deviation averaged over all days
            
    """
    interdaysd = np.std(df['y'])
    return interdaysd

def intradaycv(df):
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
    for i in pd.unique(df['Day']):
        intradaycv.append(interdaycv(df[df['Day']==i]))
    
    intradaycv_mean = np.mean(intradaycv)
    intradaycv_median = np.median(intradaycv)
    intradaycv_sd = np.std(intradaycv)
    
    return intradaycv_mean, intradaycv_median, intradaycv_sd


def intradaysd(df):
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

    for i in pd.unique(df['day_of_week']):
        intradaysd.append(np.std(df['y'][df['day_of_week']==i]))
    
    intradaysd_mean = np.mean(intradaysd)
    intradaysd_median = np.median(intradaysd)
    intradaysd_sd = np.std(intradaysd)
    return intradaysd_mean, intradaysd_median, intradaysd_sd

def MAGE(df, std=1):
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
    y = df['y'].tolist()
    ix = [1*i for i in range(len(y))]
    stdev = std
    
    # local minima & maxima
    a = np.diff(np.sign(np.diff(y))).nonzero()[0] + 1      
    # local min
    valleys = (np.diff(np.sign(np.diff(y))) > 0).nonzero()[0] + 1 
    # local max
    peaks = (np.diff(np.sign(np.diff(y))) < 0).nonzero()[0] + 1         
    # +1 -- diff reduces original index number

    #store local minima and maxima -> identify + remove turning points
    excursion_points = pd.DataFrame(columns=['Index', 'ds', 'y', 'Type'])
    k=0
    for i in range(len(peaks)):
        excursion_points.loc[k] = [peaks[i]] + [df['ds'][k]] + [df['y'][k]] + ["P"]
        k+=1

    for i in range(len(valleys)):
        excursion_points.loc[k] = [valleys[i]] + [df['ds'][k]] + [df['y'][k]] + ["V"]
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

def J_index(df):
    """
        J index is a measure of quality of glycemic control based on
        the combination of information from the mean and SD calculated as 0.001 x (mean + SD)

        Computes and returns the J-index
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            J (float): J-index of y
            
    """
    J = 0.001*((np.mean(df['y'])+np.std(df['y']))**2)
    return J

def LBGI_HBGI(df):
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
    f = ((np.log(df['y'])**1.084) - 5.381)
    rl = []
    for i in f: 
        if (i <= 0):
            rl.append(22.77*(i**2))
        else:
            rl.append(0)

    LBGI = np.mean(rl)

    rh = []
    for i in f: 
        if (i > 0):
            rh.append(22.77*(i**2))
        else:
            rh.append(0)

    HBGI = np.mean(rh)
    
    return LBGI, HBGI, rh, rl

def LBGI(df):
    """
        Computes and returns the low blood y index
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            LBGI (float): Low blood y index
            
    """
    f = ((np.log(df['y'])**1.084) - 5.381)
    rl = []
    for i in f: 
        if (i <= 0):
            rl.append(22.77*(i**2))
        else:
            rl.append(0)

    LBGI = np.mean(rl)
    return LBGI

def HBGI(df):
    """
        Computes and returns the high blood y index
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            HBGI (float): High blood y index
            
    """
    f = ((np.log(df['y'])**1.084) - 5.381)
    rh = []
    for i in f: 
        if (i > 0):
            rh.append(22.77*(i**2))
        else:
            rh.append(0)

    HBGI = np.mean(rh)
    return HBGI

def ADRR(df):
    """
        Computes and returns the average daily risk range, an assessment of total daily y variations within risk space
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            ADRRx (float): average daily risk range
            
    """
    ADRRl = []
    for i in pd.unique(df['Day']):
        LBGI, HBGI, rh, rl = LBGI_HBGI(df[df['Day']==i])
        LR = np.max(rl)
        HR = np.max(rh)
        ADRRl.append(LR+HR)

    ADRRx = np.mean(ADRRl)
    return ADRRx

def uniquevalfilter(df, value):
    """
        Supporting function for MODD and CONGA24 functions
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            value (datetime): time to match up with previous 24 hours
        Returns:
            MODD_n (float): Best matched with unique value, value
            
    """
    xdf = df[df['Minfrommid'] == value]
    n = len(xdf)
    diff = abs(xdf['y'].diff())
    MODD_n = np.nanmean(diff)
    return MODD_n

def MODD(df):
    """
        Computes and returns the mean of daily differences. Examines mean of value + value 24 hours before
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Requires:
            uniquevalfilter (function)
        Returns:
            MODD (float): Mean of daily differences
            
    """
    df['Timefrommidnight'] =  df['ds'].dt.time
    lists=[]
    for i in range(0, len(df['Timefrommidnight'])):
        lists.append(int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[0:2])*60 + int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[3:5]) + round(int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[6:9])/60))
    df['Minfrommid'] = lists
    df = df.drop(columns=['Timefrommidnight'])
    
    #Calculation of MODD and CONGA:
    MODD_n = []
    uniquetimes = df['Minfrommid'].unique()

    for i in uniquetimes:
        MODD_n.append(uniquevalfilter(df, i))
    
    #Remove zeros from dataframe for calculation (in case there are random unique values that result in a mean of 0)
    MODD_n[MODD_n == 0] = np.nan
    
    MODD = np.nanmean(MODD_n)
    return MODD

def CONGA24(df):
    """
        Computes and returns the continuous overall net glycemic action over 24 hours
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Requires:
            uniquevalfilter (function)
        Returns:
            CONGA24 (float): continuous overall net glycemic action over 24 hours
            
    """
    df['Timefrommidnight'] =  df['Time'].dt.time
    lists=[]
    for i in range(0, len(df['Timefrommidnight'])):
        lists.append(int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[0:2])*60 + int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[3:5]) + round(int(df['Timefrommidnight'][i].strftime('%H:%M:%S')[6:9])/60))
    df['Minfrommid'] = lists
    df = df.drop(columns=['Timefrommidnight'])
    
    #Calculation of MODD and CONGA:
    MODD_n = []
    uniquetimes = df['Minfrommid'].unique()

    for i in uniquetimes:
        MODD_n.append(uniquevalfilter(df, i))
    
    #Remove zeros from dataframe for calculation (in case there are random unique values that result in a mean of 0)
    MODD_n[MODD_n == 0] = np.nan
    
    CONGA24 = np.nanstd(MODD_n)
    return CONGA24

def GMI(df):
    """
        Computes and returns the y management index
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            GMI (float): y management index (an estimate of HbA1c)
            
    """
    GMI = 3.31 + (0.02392*np.mean(df['y']))
    return GMI

def eA1c(df):
    """
        Computes and returns the American Diabetes Association estimated HbA1c
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
        Returns:
            eA1c (float): an estimate of HbA1c from the American Diabetes Association
            
    """
    eA1c = (46.7 + np.mean(df['y']))/ 28.7 
    return eA1c

def summary(df): 
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
    meanG = np.nanmean(df['y'])
    medianG = np.nanmedian(df['y'])
    minG = np.nanmin(df['y'])
    maxG = np.nanmax(df['y'])
    Q1G = np.nanpercentile(df['y'], 25)
    Q3G = np.nanpercentile(df['y'], 75)
    
    return meanG, medianG, minG, maxG, Q1G, Q3G

def plotysd(df, sd=1, size=15):
    """
        Plots y with specified standard deviation lines
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            sd (integer): standard deviation lines to plot (default=1)
            size (integer): font size for plot (default=15)
        Returns:
            plot of y with standard deviation lines
            
    """
    y_mean = np.mean(df['y'])
    up = np.mean(df['y']) + sd*np.std(df['y'])
    dw = np.mean(df['y']) - sd*np.std(df['y'])

    plt.figure(figsize=(20,5))
    plt.rcParams.update({'font.size': size})
    plt.plot(df['Time'], df['y'], '.', color = '#1f77b4')
    plt.axhline(y=y_mean, color='red', linestyle='-')
    plt.axhline(y=up, color='pink', linestyle='-')
    plt.axhline(y=dw, color='pink', linestyle='-')
    plt.ylabel('y')
    plt.show()

def plotybounds(df, upperbound = 180, lowerbound = 70, size=15):
    """
        Plots y with user-defined boundaries
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            upperbound (integer): user defined upper bound for y line to plot (default=180)
            lowerbound (integer): user defined lower bound for y line to plot (default=70)
            size (integer): font size for plot (default=15)
        Returns:
            plot of y with user defined boundary lines
            
    """
    plt.figure(figsize=(20,5))
    plt.rcParams.update({'font.size': size})
    plt.plot(df['ds'], df['y'], '.', color = '#1f77b4')
    plt.axhline(y=upperbound, color='red', linestyle='-')
    plt.axhline(y=lowerbound, color='orange', linestyle='-')
    plt.ylabel('y')
    plt.show()

def plotysmooth(df, size=15):
    """
        Plots smoothed y plot (with LOWESS smoothing)
        Args:
            (pd.DataFrame): dataframe of data with DateTime, Time and y columns
            size (integer): font size for plot (default=15)
        Returns:
            LOWESS-smoothed plot of y
            
    """
    filteres = lowess(df['y'], df['Time'], is_sorted=True, frac=0.025, it=0)
    filtered = pd.to_datetime(filteres[:,0], format='%Y-%m-%dT%H:%M:%S') 
    
    plt.figure(figsize=(20,5))
    plt.rcParams.update({'font.size': size})
    plt.plot(df['ds'], df['y'], '.')
    plt.plot(filtered, filteres[:,1], 'r')
    plt.ylabel('y')
    plt.show()