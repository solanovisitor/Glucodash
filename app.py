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
        st.session_state.device = st.selectbox('Select your device', devices)
        st.session_state.data = st.file_uploader('Upload the glucose data downloaded from the LibreView website', type='csv')
        ranges = ['2 weeks', '1 month', '3 months', '6 months', '1 year', 'All times']
        day_names = ['Every Day', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        boolean = ['No', 'Yes']
        #unit = st.radio('Select the unit of choice', units)
        st.session_state.time_range = st.selectbox('Select the amount of time for your analysis', ranges, index=2)
        st.session_state.week_day = st.selectbox('Filter by day of week', day_names)
        whole_day = st.radio('Do you want to select a time range?', boolean)
        if whole_day == 'Yes':
            hours = st.slider(
            "Select the desired time range:",
            value=(time(7, 00), time(9, 00)))
            st.session_state.start_time, st.session_state.end_time = hours
        else:
            st.session_state.start_time = None
            st.session_state.end_time = None
        if st.session_state.data is not None:
            cgm_data = FinalData(st.session_state.data, st.session_state.device, st.session_state.time_range, st.session_state.week_day, st.session_state.start_time, st.session_state.end_time)
            filtered_df, filtered_df2, st.session_state.start_date, st.session_state.final_date = cgm_data.filter_data
            cgm = CgmMetric(filtered_df)
            if filtered_df2.empty:
                cgm2 = None
            else:
                cgm2 = CgmMetric(filtered_df2)
            st.header('Check the resulting metrics below')
            b_day = cgm.best_day()
            st.subheader(f'Your data goes from {st.session_state.start_date} to {st.session_state.final_date}')
            st.subheader(f'The lowest GMI was on the {b_day}')

            with st.container():

                col1, col2, col3, col4 = st.columns(4)

                st.session_state.n_data = cgm.available_data()
                st.session_state.avg = round(cgm.average_glucose(), 2)
                st.session_state.std = round(cgm.sd(),1)
                st.session_state.ea1c = round(cgm.eA1c(), 2)
                st.session_state.trange = round(cgm.time_in_range(), 1)
                trange_str = f'{st.session_state.trange}%'
                st.session_state.thyper = round(cgm.hyper_time(), 1)
                thyper_str = f'{st.session_state.thyper}%'
                st.session_state.thypo = round(cgm.hypo_time(), 1)
                thypo_str = f'{st.session_state.thypo}%'
                st.session_state.iqr = int(cgm.inter_qr())
                st.session_state.intersd = int(cgm.interdaysd())
                st.session_state.intrasd = int(cgm.intradaysd()[0])
                st.session_state.mage = round(cgm.MAGE(), 1)
                st.session_state.jindex = round(cgm.J_index(), 2)
                st.session_state.lgbi = round(cgm.LBGI(), 2)
                st.session_state.hbgi = round(cgm.HBGI(), 2)
                # adrr = round(cgm_metrics.ADRR(), 2)
                st.session_state.modd = round(cgm.MODD(), 2)
                st.session_state.conga = round(cgm.CONGA24(), 2)
                st.session_state.gmi = round(cgm.GMI(), 2)
                
                if cgm2 is not None:

                    st.info(f'As you selected a {st.session_state.time_range} time range, your metrics will be compared to the previous {st.session_state.time_range} data.')

                    st.session_state.n_data_delta = st.session_state.n_data-cgm2.available_data()
                    st.session_state.avg_delta = round(st.session_state.avg-cgm2.average_glucose(), 2)
                    st.session_state.std_delta = round(st.session_state.std-cgm2.sd(),2)
                    st.session_state.ea1c_delta = round(st.session_state.ea1c-cgm2.eA1c(), 2)
                    st.session_state.trange_delta = f'{round(st.session_state.trange-cgm2.time_in_range(), 2)}%'
                    st.session_state.thyper_delta = f'{round(st.session_state.thyper-cgm2.hyper_time(), 2)}%'
                    st.session_state.thypo_delta = f'{round(st.session_state.thypo-cgm2.hypo_time(), 2)}%'
                    st.session_state.iqr_delta = st.session_state.iqr-cgm2.inter_qr()
                    st.session_state.intersd_delta = round(st.session_state.intersd-cgm2.interdaysd(), 1)
                    st.session_state.intrasd_delta = round(st.session_state.intrasd-cgm2.intradaysd()[0], 1)
                    st.session_state.mage_delta = round(st.session_state.mage-cgm2.MAGE(), 2)
                    st.session_state.jindex_delta = round(st.session_state.jindex-cgm2.J_index(), 2)
                    st.session_state.lgbi_delta = round(st.session_state.lgbi-cgm2.LBGI(), 2)
                    st.session_state.hbgi_delta = round(st.session_state.hbgi-cgm2.HBGI(), 2)
                    st.session_state.modd_delta = round(st.session_state.modd-cgm2.MODD(), 2)
                    st.session_state.conga_delta = round(st.session_state.conga-cgm2.CONGA24(), 2)
                    st.session_state.gmi_delta = round(st.session_state.gmi-cgm2.GMI(), 2)

                    col1.metric(label="GMI", value=st.session_state.gmi, delta=st.session_state.gmi_delta, delta_color="inverse")
                    col1.metric(label="Time in range", value=trange_str, delta=st.session_state.trange_delta)
                    col1.metric(label='Time in hyper', value=thyper_str, delta=st.session_state.thyper_delta, delta_color="inverse")
                    col1.metric(label='Time in hypo', value=thypo_str, delta=st.session_state.thypo_delta, delta_color="inverse")
                    col2.metric(label="Average Glucose", value=f'{st.session_state.avg}mg/dL', delta=f'{st.session_state.avg_delta}mg/dL', delta_color="inverse")
                    col2.metric(label="Intraday SD", value=f'{st.session_state.intrasd}mg/dL', delta=f'{st.session_state.intrasd_delta}mg/dL', delta_color="inverse")
                    col2.metric(label='Interquartile range', value=f'{st.session_state.iqr}mg/dL', delta=f'{st.session_state.iqr_delta}mg/dL', delta_color="inverse")
                    col2.metric(label="HBGI", value=st.session_state.hbgi, delta=st.session_state.hbgi_delta, delta_color="inverse")
                    col3.metric(label="Standard Deviation (SD)", value=f'{st.session_state.std}mg/dL', delta=f'{st.session_state.std_delta}mg/dL', delta_color="inverse")
                    col3.metric(label="Interday SD", value=f'{st.session_state.intersd}mg/dL', delta=f'{st.session_state.intersd_delta}mg/dL', delta_color="inverse")
                    col3.metric(label="MAGE", value=f'{st.session_state.mage}mg/dL', delta=f'{st.session_state.mage_delta}mg/dL', delta_color="inverse")
                    col3.metric(label="LBGI", value=st.session_state.lgbi, delta=st.session_state.lgbi_delta)
                    col4.metric(label="Estimated A1c", value=f'{st.session_state.ea1c}%', delta=f'{st.session_state.ea1c_delta}%', delta_color="inverse")
                    col4.metric(label="CONGA24", value=st.session_state.conga, delta=st.session_state.conga_delta, delta_color="inverse")
                    col4.metric(label="J-Index", value=st.session_state.jindex, delta=st.session_state.jindex_delta, delta_color="inverse")
                    col4.metric(label="Number of measurements", value=st.session_state.n_data, delta=st.session_state.n_data_delta)
                
                else:

                    col1.metric(label="GMI", value=st.session_state.gmi)
                    col1.metric(label="Time in range", value=trange_str)
                    col1.metric(label='Time in hyper', value=thyper_str)
                    col1.metric(label='Time in hypo', value=thypo_str)
                    col2.metric(label="Average Glucose", value=f'{st.session_state.avg}mg/dL')
                    col2.metric(label="Intraday SD", value=f'{st.session_state.intrasd}mg/dL')
                    col2.metric(label='Interquartile range', value=f'{st.session_state.iqr}mg/dL')
                    col2.metric(label="HBGI", value=st.session_state.hbgi)
                    col3.metric(label="Standard Deviation (SD)", value=f'{st.session_state.std}mg/dL')
                    col3.metric(label="Interday SD", value=f'{st.session_state.intersd}mg/dL')
                    col3.metric(label="MAGE", value=f'{st.session_state.mage}mg/dL')
                    col3.metric(label="LBGI", value=st.session_state.lgbi)
                    col4.metric(label="Estimated A1c", value=f'{st.session_state.ea1c}%')
                    col4.metric(label="CONGA24", value=st.session_state.conga)
                    col4.metric(label="J-Index", value=st.session_state.jindex)
                    col4.metric(label="Number of measurements", value=st.session_state.n_data)

            with st.container():
                
                st.header('Visualize glucose data') 
                cgm.histogram()
                cgm.scatter()
                cgm.one_day_scatter()

if __name__ == '__main__':
    main()