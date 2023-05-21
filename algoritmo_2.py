import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.svm import SVC
import calculos as cl
import warnings
warnings.filterwarnings('ignore')

# PARTE EN QUE CREAMOS VARIABLES Y PROCESAMOS LOS DATOS
def procesado_2(df):
    # VARIABLES BALANCE PORCENTUAL DIAS PREVIOS
    df["Porcentaje"] = ((df["Close"]*100)/df["Open"])-100
    df["POR-3"] = df["Porcentaje"].shift(3)
    df["POR-3"] = df["POR-3"].fillna(method="bfill")
    df["POR-2"] = df["Porcentaje"].shift(2)
    df["POR-2"] = df["POR-2"].fillna(method="bfill")
    df["POR-1"] = df["Porcentaje"].shift(1)
    df["POR-1"] = df["POR-1"].fillna(method="bfill")
    df["POR-0"] = df["Porcentaje"]
    del df["Porcentaje"]

    # RSI 
    indicador_RSI = RSIIndicator(close = df["Close"], window = 14)
    df["RSI"] = indicador_RSI.rsi()
    df["RSI"] = df["RSI"].fillna(method="bfill")
    df["RSI"] = df["RSI"].fillna(method="ffill")
    df["RSI"] = df["RSI"].replace(to_replace=0, method='ffill')
    df["RSI"] = df["RSI"].replace(to_replace=0, method='bfill')

    # ADX SACAMOS DIFERENCIA ENTRE +DI Y -DI
    indicador_ADX = ADXIndicator(high = df["High"], low = df["Low"], close = df["Close"], window = 10 )
    df["ADX"] = indicador_ADX.adx()
    df["ADX"] = df["ADX"].replace(to_replace=0, method='bfill')
    df["-DI"] = indicador_ADX.adx_neg()
    df["-DI"] = df["-DI"].replace(to_replace=0, method='bfill')
    df["+DI"] = indicador_ADX.adx_pos()
    df["+DI"] = df["+DI"].replace(to_replace=0, method='bfill')
    df["DDI"] = df["+DI"] - df["-DI"]

    # CLASE A PREDECIR
    df["CLASE"] = df['Close'].shift(-1) - df['Open'].shift(-1)
    df.loc[(df["CLASE"] >= 0), "CLASE"] = 1
    df.loc[(df["CLASE"] < 0), "CLASE"] = 0
    df["CLASE"] = df["CLASE"].fillna(method="ffill")
    del df["Open"],df["High"],df["Low"],df["Close"],df["ADX"],df["-DI"],df["+DI"]  

    # ESCALAMOS LOS INDICADORES 
    df["RSI"] = df["RSI"]/100
    df["DDI"] = df["DDI"]/100

    # RETORNAMOS EL DF CON LAS VARIABLES
    print("al 2 var")
    return df

def prediccion_2(df_train, df_test):
    print("prediccion")
    # VARIABLES
    df_tr = procesado_2(df_train)
    df_te = procesado_2(df_test)   
    
    # ELIMINACION REGISTROS EXTRA
    df_tr = cl.el_reg(df_train)
    df_te = cl.el_reg(df_test)

    # X_train
    X_train = df_tr.copy()
    X_train = X_train.drop(["CLASE"], axis=1)

    # X_test
    X_test = df_te.copy()
    X_test = X_test.drop(["CLASE"], axis=1)

    # y_train, y_test
    y_train = df_tr["CLASE"]
    y_test = df_te["CLASE"]

    # MODELO
    modelo = SVC(C=6, class_weight='balanced', kernel='rbf', gamma=0.4)
    modelo.fit(X_train, y_train)

    # PREDICCION
    prediccion = modelo.predict(X_test)

    # METRICAS
    acc = accuracy_score(y_test, prediccion)
    cm = confusion_matrix(y_test, prediccion)

    # RETORNAMOS LO QUE QUEREMOS
    print("al 2 pred")
    info = "POWERED BY AL2 SHIBA"
    prediccion = pd.Series(prediccion)
    return acc,cm,y_test,prediccion,info      



