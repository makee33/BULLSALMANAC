import streamlit as st
import yfinance as yf
import pandas as pd
pd.options.mode.chained_assignment = None
import datetime


# FUNCION SOLUCION BUGS DE PLATAFPRMA YFINANCE
def solucion_bug(df):
    df["Close_aux"] = df["Close"]
    df.loc[(df["Open"] == df["Close"]), "Close"] = df["Open"].shift(-1)
    df["Close"].iloc[-1] = df["Close_aux"].iloc[-1]
    del df["Close_aux"]
    return df

# FUNCION DESCARGAR LOS DATOS DE YFINANCE
def descarga_datos (consulta):
    # MONTAMOS LAS FECHAS PARA LAS CONSULTAS, AÑADIMOS DIAS ANTERIORES PARA CALCULOS
    inicio_train = consulta[0] - datetime.timedelta(days=14)
    fin_train = consulta[1]
    inicio_test = consulta[2] - datetime.timedelta(days=14)
    # NECESITAMOS AÑADIR UN DIA PORQUE YFINANCE COGE EL DIA DE ANTES
    fin_test = consulta[3] + datetime.timedelta(days=1)

    # LOS DATOS FINANCIEROS PARA LOS ALGORITMOS
    df_train = yf.download(consulta[4], inicio_train, fin_train, interval="1D" )
    df_test = yf.download(consulta[4], inicio_test, fin_test, interval="1D" )
    del df_train["Adj Close"], df_test["Adj Close"], df_train["Volume"], df_test["Volume"]

    df_train_debug = solucion_bug(df_train)
    df_test_debug = solucion_bug(df_test)

    # VARIABLE 1 
    return df_train_debug, df_test_debug

# FUNCION ELIMINAR REGISTROS EXTRA DESCARGADOS PARA CALCULOS
def el_reg(df):
    df.drop(df.head(14).index, inplace = True)
    return(df)

# FUNCION COLOREAR TABLA
def colorear(row):
    value = row.loc['HITS']
    if value == 'OK':
        color = '#4ba32d' # VERDE
    else: 
        color = ""
    return ['background-color: {}'.format(color) for r in row]


#FUNCION PARA OBTENER EL DF DEL FEEDBACK
def df_feedback(metricas,test_original):
    #ELIMINAMOS LOS REGISTROS SOBRANTES AL TEST ORIGINAL
    test_orig = el_reg(test_original)
    df_feedback = test_orig.copy()

    # AÑADIMOS COLUMNA CON LOS PREDECIDOS
    predecidos = metricas[3].tolist()
    df_feedback["DAY PREDICTION"] = predecidos

    #AÑADIMOS COLUMNA CON LOS VALORES REALES
    df_feedback["DAY REAL BALANCE"]= metricas[2]

    #AÑADIMOS COLUMNA DE COMPARACION
    df_feedback["HITS"] = "KO"
    df_feedback.loc[(df_feedback["DAY PREDICTION"] == df_feedback["DAY REAL BALANCE"]), "HITS"] = "OK"

    #ELIMINAMOS DATOS QUE NO QUEREMOS
    del df_feedback["High"],df_feedback["Low"]

    #MOVEMOS LAS PREDICCIONES PORQUE SON DEL DIA SIGUIENTE, QUE EL USUARIO LAS VEA EN SU DIA
    df_feedback["DAY PREDICTION"] = df_feedback["DAY PREDICTION"].shift(1)
    df_feedback["DAY REAL BALANCE"] = df_feedback["DAY REAL BALANCE"].shift(1)
    df_feedback["HITS"] = df_feedback["HITS"].shift(1)

    # ELIMINAMOS EL PRIMER REGISTRO PUES LA PREDICION ESTA VACIA
    df_feedback.drop(df_feedback.head(1).index, inplace = True)

    #CREAMOS COLUMNA DE BALANCE DEL DIA, POSITIVO SI ACERTAMOS NEGATIVO SI NO
    df_feedback["DAILY PERCENT"] = abs(((df_feedback["Close"]*100)/df_feedback["Open"])-100)
    df_feedback.loc[(df_feedback["HITS"] == "KO"), "DAILY PERCENT"] = -(df_feedback["DAILY PERCENT"])

    #SUMAMOS EL ACUMULADO
    df_feedback["CUMULATIVE P&L"] = df_feedback["DAILY PERCENT"].cumsum()
    # partimos de 100%
    df_feedback["CUMULATIVE P&L"] = df_feedback["CUMULATIVE P&L"]+100

    # COLUMNA DE INTERES COMPUESTO
    df_feedback["COMPOUND P&L"] = df_feedback["CUMULATIVE P&L"].shift(1)*((df_feedback["DAILY PERCENT"]/100)+1) 
    # el primero es nulo
    df_feedback["COMPOUND P&L"].iloc[0] = df_feedback["CUMULATIVE P&L"].iloc[0]


    #RENOMBRAMOS PARA QUE LA GENTE NO VEA CLASES CATEGORICAS
    df_feedback.loc[(df_feedback["DAY PREDICTION"] == 0), "DAY PREDICTION"] = "BEARISH"
    df_feedback.loc[(df_feedback["DAY PREDICTION"] == 1), "DAY PREDICTION"] = "BULLISH" 
    df_feedback.loc[(df_feedback["DAY REAL BALANCE"] == 0), "DAY REAL BALANCE"] = "BEARISH"
    df_feedback.loc[(df_feedback["DAY REAL BALANCE"] == 1), "DAY REAL BALANCE"] = "BULLISH"      

    return df_feedback