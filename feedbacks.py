import streamlit as st
import copy
import diccionarios as dc
import yfinance as yf
import algoritmo_1 as al1
import algoritmo_2 as al2
import algoritmo_3 as al3
import calculos as cal
import plotly.express as px
import time

# FUNCION MENU LATERAL
def menu():
    # CABECERA MENU
    st.write("**:red[ASSETS SELECTION LIBRARY]**")

    # TABS PARA LAS DISTINTAS LIBRERIAS
    cryptos, currencies, indices, commodities, custom = st.tabs(["CRYPTO", "CURRENCIES", "INDICES", "COMMODITIES", "CUSTOM"])
    activo = ""
    nombre = ""

    # EN CASO DE SELECCIONAR UNA CRIPTO
    with cryptos:
        result1 = st.button("SUBMIT CRYPTO")
        crypto = st.radio( "SELECT YOUR CRYPTO ASSET FOR FORECASTING",
                          (list(dc.dic_criptos.keys())))
        if result1:
            nombre = crypto
            activo = dc.dic_criptos[crypto][1]

    # EN CASO DE SELECCIONAR UNA DIVISA               
    with currencies:
        result2 = st.button("SUBMIT CURRENCY")
        currency = st.radio( "SELECT YOUR CURRENCY ASSET FOR FORECASTING",
                          (list(dc.dic_divisas.keys()))) 
        if result2:
            nombre = currency
            activo = dc.dic_divisas[currency][1]

    # EN CASO DE SELECCIONAR UN INDICE                     
    with indices:
        result3 = st.button("SUBMIT INDEX")
        index = st.radio( "SELECT YOUR INDEX ASSET FOR FORECASTING",
                          (list(dc.dic_indices.keys())))

        if result3:
            nombre = index
            activo = dc.dic_indices[index][1]

    # EN CASO DE SELECCIONAR UNA MATERIA PRIMA                  
    with commodities:
        result4 = st.button("SUBMIT COMMODITY")
        commodity = st.radio( "SELECT YOUR COMMODITY ASSET FOR FORECASTING",
                          (list(dc.dic_materias.keys())))
        if result4:
            nombre = commodity
            activo = dc.dic_materias[commodity][1]

    # EN CASO DE SELECCIONAR UN ACTIVO PERSONALIZADO
    with custom:
        custom = st.text_input( "ENTER CUSTOM ASSET WITH ITS YAHOO FINANCE KEYCODE", "EX: EURUSD=X")
        result5 = st.button("SUBMIT CUSTOM ASSET")
        if result5:
            df = yf.download(custom, "2023-1-1", "2023-3-1", interval="1D" )
            if df.empty == True:
                nombre = custom + " IS NOT A PROPERLY ASSET OR MY BE DELISTED"
                activo = custom     
            else:
                nombre = custom 
                activo = custom    

    return nombre, activo


# FUNCION FEEDBACK DEL FORMULARIO
def feedback(fecha1,fecha2,fecha3,fecha4,asset):

    # DFS CON PRIMEROS DATOS FINANCIEROS
    consulta = [fecha1,fecha2,fecha3,fecha4,asset]
    dfs = cal.descarga_datos(consulta)
    print("dfs descargados")

    # DFS MANDADOS AL ALGORITMO 1
    dfs_al1 = copy.deepcopy(dfs)
    try:
       met1 = al1.prediccion_1(dfs_al1[0],dfs_al1[1])
    except:
       # si las metricas fallan el accuracy a valorar sera 0
       met1 = (0,0,0,0)

    # DFS MANDADOS AL ALGORITMO 2
    dfs_al2 = copy.deepcopy(dfs)
    try:
       met2 = al1.prediccion_1(dfs_al2[0],dfs_al2[1])
    except:
       # si las metricas fallan el accuracy a valorar sera 0
       met2 = (0,0,0,0)

    # DFS MANDADOS AL ALGORITMO 2
    dfs_al2 = copy.deepcopy(dfs)
    try:
       met2 = al2.prediccion_2(dfs_al2[0],dfs_al2[1])
    except:
       # si las metricas fallan el accuracy a valorar sera 0
       met2 = (0,0,0,0)

    # DFS MANDADOS AL ALGORITMO 3
    dfs_al3 = copy.deepcopy(dfs)
    try:
       met3 = al3.prediccion_3(dfs_al3[0],dfs_al3[1])
    except:
       # si las metricas fallan el accuracy a valorar sera 0
       met3 = (0,0,0,0)

    # COMPARAMOS LOS ACCURACY A VER CON QUE ALGORITMO NOS QUEDAMOS
    select_algo = met1
    if met2[0] > met1[0]: 
        select_algo = met2
    if met3[0] > met2[0] and met3[0] > met1[0]: 
        select_algo = met3

    # DAMOS UN PEQUEÑO FEEDBACK PARA NOSOTROS VER QUE SE HA SELECCIONADO
    subcol5, subcol6= st.columns([4, 1])
    with subcol6:st.caption(f"{select_algo[4]} - {round(met1[0],3)}:{round(met2[0],3)}:{round(met3[0],3)}")

    # SACAMOS LOS DATOS DEL ALGORITMO SELECCIONADO
    #TOTAL BAJISTAS ACERTADOS
    baj_ok = select_algo[1][0][0]
    #TOTAL BAJISTAS FALLADOS
    baj_ko = select_algo[1][0][1]
    #TOTAL ALCISTAS FALLADOS
    alc_ko = select_algo[1][1][0]   
    #TOTAL ALCISTAS ACERTADOS
    alc_ok = select_algo[1][1][1] 
    #EFICIENCIA
    efi = (select_algo[0])*100 
    #PREDICCION PARA EL DIA SIGUIENTE
    pred = select_algo[3].iloc[-1]

    # SACAMOS EL DF FEEDBACK
    dfs_fed = copy.deepcopy(dfs)
    df_feedback = cal.df_feedback(select_algo, dfs_fed[1])

    # PREDICCION DEL DIA SIGUIENTE
    subcolA, subcolB,subcolC= st.columns([1, 1, 3])
    with subcolA:
        st.subheader( f'NEXT DAY FORECAST')
        st.write( f':orange[ PREDICTION FOR NEXT CANDLE AFTER {fecha4}]')
        if pred == 1:st.header(f':green[BULLISH]')
        else:st.header(f':red[BEARISH]')        
    st.divider()

    # EFICIENCIA DEL ALGORITMO
    st.subheader("PREDICTION ALGORITHM EFFICIENCY: " + str(round(efi,2)) + "%")
    eficiencia = st.progress(0)
    for percent_complete in range(int(efi)):
        time.sleep(0.01)
        eficiencia.progress(percent_complete + 1)
    st.divider()

    # METRICAS DE EFICIENCIA P&L
    subcolD, subcolE,subcolF= st.columns([1, 1, 1]) 
    # P&L ACUMULADO
    acumul = df_feedback["CUMULATIVE P&L"].iloc[-1]
    acumul_value = str(round((acumul-100), 5)) + " %"
    acumul_delta = "x" + str(round(acumul/100, 5))
    acumul_cod = "inverse"
    if acumul > 100:
        acumul_value = "+" + str(round((acumul-100), 5)) + " %"
        acumul_cod = "normal"
    subcolD.metric(label="CUMULATIVE P&L PERFORMANCE", value= acumul_value, delta=acumul_delta, delta_color= acumul_cod)

    # P&L MEDIA
    media = df_feedback["DAILY PERCENT"].mean()
    media_value = str(round(media, 5)) + " %"
    media_delta = "NEGATIVE AVERAGE"
    media_cod = "inverse"
    if media > 0:
        media_value = "+" + str(round(media, 5)) + " %"
        media_delta = "POSITIVE AVERAGE"
        media_cod = "normal"
    subcolE.metric(label="AVERAGE PREDICTION P&L", value = media_value, delta=media_delta, delta_color= media_cod)

    # P&L INTERES COMPUESTO
    comp = df_feedback["COMPOUND P&L"].iloc[-1]
    comp_value = str(round((comp-100), 5)) + " %"
    comp_delta = "x" + str(round(comp/100, 5))
    comp_cod = "inverse"
    if comp > 100:
        comp_value = "+" + str(round((comp-100), 5)) + " %"
        comp_cod = "normal"
    subcolF.metric(label="COMPOUND P&L PERFORMANCE", value = comp_value, delta=comp_delta, delta_color= comp_cod)
    st.divider()

    # METRICAS DE CONFUSIN EN CIRCLE CHARTS
    total_pred = baj_ok+baj_ko+alc_ok+alc_ko
    subcol7, subcol8, subcol9, subcol10, subcol11, subcol12= st.columns([5, 1, 5, 1, 5, 1])
    # PREDICCIONES GLOBALES
    with subcol7:
        st.write(f"**RIGHT PREDICTED VALUES {baj_ok+alc_ok} OF {total_pred}**")
        color_discrete_map = {'a':'#1d88c0', 'b':'#8cd0f4'}   
        fig4 = px.pie(labels=["a","b"], values=[baj_ok+alc_ok,baj_ko+alc_ko], color=["a","b"], color_discrete_map=color_discrete_map)
        st.plotly_chart(fig4, use_container_width=True)
    # PREDICCIONES ALCISTAS
    with subcol9:
        st.write(f"**RIGHT BULLISH PREDICTED VALUES {alc_ok} OF {alc_ok+alc_ko}**")
        color_discrete_map = {'a':'#38cb3f', 'b':'#89fc8f'}    
        fig5 = px.pie(labels=["a","b"], values=[alc_ok,alc_ko], color=["a","b"], color_discrete_map=color_discrete_map)
        st.plotly_chart(fig5, use_container_width=True)
    # PREDICCIONES BAJISTAS
    with subcol11:
        st.write(f"**RIGHT BEARISH PREDICTED VALUES {baj_ok} OF {baj_ok+baj_ko}**")
        color_discrete_map = {'a':'#d13342', 'b':'#fa7d88'}  
        fig6 = px.pie(labels=["a","b"], values=[baj_ok,baj_ko], color=["a","b"], color_discrete_map=color_discrete_map)
        st.plotly_chart(fig6, use_container_width=True)
 

    # EVOLUCION ACUMULADA DE P&L DEL EXPERIMENTO
    st.divider()
    st.subheader("PREDICTION P&L PERFORMANCE")    
    fig=px.line(df_feedback, x=df_feedback.index, y = df_feedback["CUMULATIVE P&L"])
    st.plotly_chart(fig, use_container_width=True)

    # EVOLUCION DEL INTERES COMPUESTO
    st.divider()
    st.subheader("PREDICTION WITH COMPOUND P&L")    
    fig2=px.line(df_feedback, x=df_feedback.index, y = df_feedback["COMPOUND P&L"])
    st.plotly_chart(fig2, use_container_width=True)


    # TABLA DE RESULTADOS DEL EXPERIMENTO
    st.divider()
    st.subheader("PREDICTION EXPERIMENT SUMMARY")
    # necesitamos 5 decimales porque hay activos muy pequeños
    st.table(df_feedback.style.apply(cal.colorear, axis=1).format(precision=5))

    st.caption("Diego Higeo Sales - TFM Master Python Escuela Internacional de Posgrados")





