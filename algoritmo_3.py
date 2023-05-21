import pandas as pd
from ta.momentum import RSIIndicator
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.tree import DecisionTreeRegressor
import calculos as cl
import warnings
warnings.filterwarnings('ignore')

# PARTE EN QUE CREAMOS VARIABLES Y PROCESAMOS LOS DATOS
def procesado_3(df):
    # RSI OPEN
    indicador_RSI1 = RSIIndicator(close = df["Open"], window = 14)
    df["OP_RSI"] = indicador_RSI1.rsi()
    df["OP_RSI"] = df["OP_RSI"].fillna(method="bfill")

    # RSI HIGH
    indicador_RSI2 = RSIIndicator(close = df["High"], window = 14)
    df["HI_RSI"] = indicador_RSI2.rsi()
    df["HI_RSI"] = df["HI_RSI"].fillna(method="bfill")

    # RSI LOW
    indicador_RSI3 = RSIIndicator(close = df["Low"], window = 14)
    df["LO_RSI"] = indicador_RSI3.rsi()
    df["LO_RSI"] = df["LO_RSI"].fillna(method="bfill")

    # RSI CLOSE
    indicador_RSI4 = RSIIndicator(close = df["Close"], window = 14)
    df["CL_RSI"] = indicador_RSI4.rsi()
    df["CL_RSI"] = df["CL_RSI"].fillna(method="bfill")

    # CLASE A PREDECIR
    df["CLASE"] = df['CL_RSI'].shift(-1)
    df["CLASE"] = df["CLASE"].fillna(method="ffill") 

    # CLASE AUXILIAR
    df["CLASE_AUX"] = df['Close'].shift(-1) - df['Open'].shift(-1)
    df.loc[(df["CLASE_AUX"] >= 0), "CLASE_AUX"] = 1
    df.loc[(df["CLASE_AUX"] < 0), "CLASE_AUX"] = 0
    df["CLASE_AUX"] = df["CLASE_AUX"].fillna(method="ffill")

    del df["Open"],df["High"],df["Low"],df["Close"] 

    # RETORNAMOS EL DF CON LAS VARIABLES
    print("al 3 var")
    return df

def prediccion_3(df_train, df_test):
    print("prediccion")
    # VARIABLES
    df_tr = procesado_3(df_train)
    df_te = procesado_3(df_test)   
    
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

    #CONSERVAMOS LA CLASE AUXILIAR DEL TEST
    X_train = X_train.drop(["CLASE_AUX"], axis=1)
    CLASES_AUX_TEST = X_test["CLASE_AUX"].tolist()
    X_test = X_test.drop(["CLASE_AUX"], axis=1)

    # MODELO
    modelo = DecisionTreeRegressor(max_depth=4)
    modelo.fit(X_train, y_train)

    #PREDICCION
    prediccion = modelo.predict(X_test)

    # BINARIZACIÓN DE LOS RESULTADOS    
    X_test["Y_PRED"] = prediccion
    X_test["PRED"] = 0
    X_test.loc[(X_test["Y_PRED"] > X_test["CL_RSI"]), "PRED"] = 1 
    X_test["CLASE_AUX"] = CLASES_AUX_TEST
    del X_test["Y_PRED"]

    # METRICAS
    acc = accuracy_score(X_test["CLASE_AUX"], X_test["PRED"])
    cm = confusion_matrix(X_test["CLASE_AUX"], X_test["PRED"])

    # PASAMOS LAS PREDICCIONES PROCESADAS
    prediccion_bin = X_test["PRED"]

    # PASAMOS CLASES PROCESADAS BINARIAS
    clase_binaria = X_test["CLASE_AUX"]

    # RETORNAMOS LO QUE QUEREMOS
    print("al 3 pred")
    info = "POWERED BY AL3 TORA"
    return acc,cm,clase_binaria,prediccion_bin,info     



