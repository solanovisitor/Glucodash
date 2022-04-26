import streamlit as st
from datetime import time
from util import FinalData ,CgmMetric
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
            cgm_data = FinalData(data, device, time_range, week_day, start_time, end_time)
            filtered_df, filtered_df2 = cgm_data.filter_data
            cgm = CgmMetric(filtered_df)
            if filtered_df2.empty:
                cgm2 = None
            else:
                cgm2 = CgmMetric(filtered_df2)
            st.header('Check the resulting metrics below')
            b_day = cgm.best_day()
            st.subheader(f'The lowest GMI was on the {b_day}')

            with st.container():

                col1, col2, col3, col4 = st.columns(4)

                n_data = cgm.available_data()
                avg = round(cgm.average_glucose(), 2)
                std = round(cgm.sd(),2)
                ea1c = round(cgm.eA1c(), 2)
                trange = cgm.time_in_range()
                trange_str = f'{trange}%'
                thyper = cgm.hyper_time()
                thyper_str = f'{thyper}%'
                thypo = cgm.hypo_time()
                thypo_str = f'{thypo}%'
                iqr = cgm.inter_qr()
                intersd = round(cgm.interdaysd(), 2)
                intrasd = round(cgm.intradaysd()[0], 2)
                mage = round(cgm.MAGE(), 2)
                jindex = round(cgm.J_index(), 2)
                lgbi = round(cgm.LBGI(), 2)
                hbgi = round(cgm.HBGI(), 2)
                # adrr = round(cgm_metrics.ADRR(), 2)
                modd = round(cgm.MODD(), 2)
                conga = round(cgm.CONGA24(), 2)
                gmi = round(cgm.GMI(), 2)
                
                if cgm2 is not None:

                    n_data_delta = n_data-cgm2.available_data()
                    avg_delta = round(avg-cgm2.average_glucose(), 2)
                    std_delta = round(std-cgm2.sd(),2)
                    ea1c_delta = round(ea1c-cgm2.eA1c(), 2)
                    trange_delta = f'{round(trange-cgm2.time_in_range(), 2)}%'
                    thyper_delta = f'{round(thyper-cgm2.hyper_time(), 2)}%'
                    thypo_delta = f'{round(thypo-cgm2.hypo_time(), 2)}%'
                    iqr_delta = iqr-cgm2.inter_qr()
                    intersd_delta = round(intersd-cgm2.interdaysd(), 2)
                    intrasd_delta = round(intrasd-cgm2.intradaysd()[0], 2)
                    mage_delta = round(mage-cgm2.MAGE(), 2)
                    jindex_delta = round(jindex-cgm2.J_index(), 2)
                    lgbi_delta = round(lgbi-cgm2.LBGI(), 2)
                    hbgi_delta = round(hbgi-cgm2.HBGI(), 2)
                    modd_delta = round(modd-cgm2.MODD(), 2)
                    conga_delta = round(conga-cgm2.CONGA24(), 2)
                    gmi_delta = round(gmi-cgm2.GMI(), 2)

                    col1.metric(label="Number of measurements", value=n_data, delta=n_data_delta)
                    col2.metric(label="Average Glucose", value=avg, delta=avg_delta, delta_color="inverse")
                    col3.metric(label="Standard Deviation (SD)", value=std, delta=std_delta, delta_color="inverse")
                    col4.metric(label="Estimated A1c", value=ea1c, delta=ea1c_delta, delta_color="inverse")
                    col1.metric(label="Time in range", value=trange_str, delta=trange_delta)
                    col2.metric(label='Time in hyper', value=thyper_str, delta=thyper_delta, delta_color="inverse")
                    col3.metric(label='Time in hypo', value=thypo_str, delta=thypo_delta, delta_color="inverse")
                    col4.metric(label='Interquartile range', value=iqr, delta=iqr_delta, delta_color="inverse")
                    col1.metric(label="Interday SD", value=intersd, delta=intersd_delta, delta_color="inverse")
                    col2.metric(label="Intraday SD", value=intrasd, delta=intrasd_delta, delta_color="inverse")
                    col3.metric(label="MAGE", value=mage, delta=mage_delta, delta_color="inverse")
                    col4.metric(label="J-Index", value=jindex, delta=jindex_delta, delta_color="inverse")
                    col1.metric(label="LBGI", value=lgbi, delta=lgbi_delta, delta_color="inverse")
                    col2.metric(label="HBGI", value=hbgi, delta=hbgi_delta, delta_color="inverse")
                    col3.metric(label="CONGA24", value=conga, delta=conga_delta, delta_color="inverse")
                    col4.metric(label="GMI", value=gmi, delta=gmi_delta, delta_color="inverse")
                
                else:

                    col1.metric(label="Number of measurements", value=n_data)
                    col2.metric(label="Average Glucose", value=avg)
                    col3.metric(label="Standard Deviation (SD)", value=std)
                    col4.metric(label="Estimated A1c", value=ea1c)
                    col2.metric(label='Time in hyper', value=thyper_str)
                    col3.metric(label='Time in hypo', value=thypo_str)
                    col4.metric(label='Interquartile range', value=iqr)
                    col1.metric(label="Interday SD", value=intersd)
                    col2.metric(label="Intraday SD", value=intrasd)
                    col3.metric(label="MAGE", value=mage)
                    col4.metric(label="J-Index", value=jindex)
                    col1.metric(label="LBGI", value=lgbi)
                    col2.metric(label="HBGI", value=hbgi)
                    col3.metric(label="CONGA24", value=conga)
                    col4.metric(label="GMI", value=gmi)

            with st.container():
                
                st.header('Visualize glucose data') 
                cgm.histogram()
                cgm.scatter()
                cgm.one_day_scatter()

if __name__ == '__main__':
    main()