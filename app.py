from logging import Filterer
import streamlit as st
from datetime import time
from util import FinalData, CgmMetric #dexcom_preprocessing, libre_preprocessing, nightscout_preprocessing, filter_data
from plots import histogram, one_day_scatter, scatter
from metrics import (available_data, average_glucose,
                    time_in_range, eA1c, hyper_time,
                    hypo_time, sd, inter_qr, interdaysd,
                    intradaysd, MAGE, J_index, LBGI,
                    HBGI, ADRR, MODD, CONGA24, GMI, best_day)
# from auth_config import firebase_instances

def main():

    # with st.sidebar:

    #     auth, db, storage = firebase_instances()

    #     st.title('EndoMetrics')

    #     auth_menu = ['Login', 'Sign up']
    #     choice = st.selectbox('Login/Signup', auth_menu)

    #     email = st.text_input('Please enter your e-mail address')
    #     password = st.text_input('Please enter your password')

    #     if choice == 'Sign up':
    #         handle = st.text_input('Please enter your username', value='Default')
    #         submit = st.button('Create my account')

    #         if submit:
    #             user = auth.create_user_with_email_and_password(email, password)
    #             st.success('Your account was created successfully')
    #             st.balloons()
    #             #Sign in
    #             user = auth.sign_in_with_email_and_password(email, password)
    #             db.child(user['localId']).child('Handle').set(handle)
    #             db.child(user['localId']).child('ID').set(user['localId'])
    #             st.title('Welcome ' + handle)

    with st.container():
        st.title('Dynamic Ambulatory Glucose Profile (dAGP)')
        st.header('Input your Libre data and select your filters')
        devices = ['Freestyle Libre', 'Dexcom', 'Nightscout']
        device = st.selectbox('Select your device', devices)
        data = st.file_uploader('Upload the glucose data downloaded from the LibreView website', type='csv')
        # if data is not None:
        #     final_data = FinalData(data, device)
        #     preprocessed_df = final_data.preprocessing()
        ranges = ['2 weeks', '1 month', '3 months', '6 months', '1 year', 'All times']
        day_names = ['Every Day', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        boolean = ['No', 'Yes']
        #unit = st.radio('Select the unit of choice', units)
        time_range = st.selectbox('Select the amount of time for your analysis', ranges, index=2)
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
            # final_data = FinalData(data, device, time_range, week_day, start_time, end_time)
            # filtered_df = final_data.filter_data()
            cgm_metrics = CgmMetric(data, device, time_range, week_day, start_time, end_time)
            st.header('Check the resulting metrics below')
            # b_day = cgm_metrics.available_data()
            # st.subheader(f'The lowest GMI was on the {b_day}')
            # st.subheader(CgmMetric.available_data())

            with st.container():

                col1, col2, col3, col4 = st.columns(4)

                n_data = cgm_metrics.available_data()
                avg = round(cgm_metrics.average_glucose(), 2)
                std = round(cgm_metrics.sd(),2)
                ea1c = round(cgm_metrics.eA1c(), 2)
                trange = f'{cgm_metrics.time_in_range()}%'
                thyper = f'{cgm_metrics.hyper_time()}%'
                thypo = f'{cgm_metrics.hypo_time()}%'
                iqr = cgm_metrics.inter_qr()
                intersd = round(cgm_metrics.interdaysd(), 2)
                intrasd = round(cgm_metrics.intradaysd()[0], 2)
                mage = round(cgm_metrics.MAGE(), 2)
                jindex = round(cgm_metrics.J_index(), 2)
                lgbi = round(cgm_metrics.LBGI(), 2)
                hbgi = round(cgm_metrics.HBGI(), 2)
                # adrr = round(cgm_metrics.ADRR(), 2)
                modd = round(cgm_metrics.MODD(), 2)
                conga = round(cgm_metrics.CONGA24(), 2)
                gmi = round(cgm_metrics.GMI(), 2)

                col1.metric(label="Number of measurements", value=n_data)
                col2.metric(label="Average Glucose", value=avg)
                col3.metric(label="Standard Deviation (SD)", value=std)
                col4.metric(label="Estimated A1c", value=ea1c)
                col1.metric(label="Time in range", value=trange)
                col2.metric(label='Time in hyper', value=thyper)
                col3.metric(label='Time in hypo', value=thypo)
                col4.metric(label='Interquartile range', value=iqr)
                col1.metric(label="Interday SD", value=intersd)
                col2.metric(label="Intraday SD", value=intrasd)
                col3.metric(label="MAGE", value=mage)
                col4.metric(label="J-Index", value=jindex)
                col1.metric(label="LBGI", value=lgbi)
                col2.metric(label="HBGI", value=hbgi)
                # col3.metric(label="ADRR", value=adrr)
                # col4.metric(label="MODD", value=modd)
                col3.metric(label="CONGA24", value=conga)
                col4.metric(label="GMI", value=gmi)

            with st.container():
                
                st.header('Visualize glucose data') 
                cgm_metrics.histogram()
                cgm_metrics.scatter()
                cgm_metrics.one_day_scatter()

if __name__ == '__main__':
    main()