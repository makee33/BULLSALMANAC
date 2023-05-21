import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from feedbacks import menu, feedback
import datetime
import diccionarios as dc
import matplotlib.pyplot as plt


# CONFIGURACION GENERAL PÁGINA
response = requests.get('http://diegohigeo.fatcow.com/images/BULL_FAVICON.png')
favicon = Image.open(BytesIO(response.content))
st.set_page_config(layout="wide", page_title="BULLS ALMANAC", page_icon = favicon )

# CABECERA
st.image("./BULLS_HEADER.png") 
st.markdown("""---""")

# SELECCION ACTIVO Y ALMACENAMIENTO EN ESTADO DE SESSION
if "asset" not in st.session_state:
    st.session_state.asset = ('Please select an asset from the left menu', "")

with st.sidebar:
    seleccion = menu()

if seleccion != (("","")):
    st.session_state.asset = seleccion  

st.header( f'SELECTED ASSET: :orange[{st.session_state.asset[0]}]')


# FORMULARIO ENVIO DE FECHAS
with st.form("form1", clear_on_submit=False):

    subcol1, subcol2, subcol3, subcol4 = st.columns([1, 1, 1, 1])

    with subcol1:
        fecha1 = st.date_input(":red[TRAINING PERIOD START DATE]", datetime.date(2021, 1, 1))        
        st.write('Train Start:', fecha1)

    with subcol2:
        fecha2 = st.date_input(":red[TRAINING PERIOD END DATE]", datetime.date(2021, 3, 1))       
        st.write('Train End:', fecha2)

    with subcol3:
        fecha3 = st.date_input(":orange[TEST PERIOD START DATE]", datetime.date(2021, 3, 2))        
        st.write('Test Start:', fecha3)

    with subcol4:
        fecha4 = st.date_input(":orange[TEST PERIOD END DATE]", datetime.date(2021, 4, 2))       
        st.write('Test Start:', fecha4)

    submitted = st.form_submit_button("SUBMIT DATES")

# UNA VEZ HACEMOS EL SUBMITTED RECOPILAMOS LOS DATOS PARA CONSULTA FEEDBACK
if submitted: 
    if st.session_state.asset[1] == "": st.write("Remember to select an asset to get the predictions")
    elif fecha2 < fecha1 or fecha4 < fecha3: st.write("End dates could not be setted before start dates, please check")
    else: 
        try:
            feedback(fecha1,fecha2,fecha3,fecha4,st.session_state.asset[1])
        except:
            st.write("Due to some problem prediction could not be made, please check:")
            st.write("- If the Asset was available at the selected dates")
            st.write("- If yahoo finance has historical data for this periods") 
            st.write("- Feel free to make the query with other intputs") 
            st.write("Sorry for the inconvenience!")              





