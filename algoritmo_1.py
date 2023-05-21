import pandas as pd
from ta.momentum import RSIIndicator
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.linear_model import LogisticRegression
import calculos as cl

# PARTE EN QUE CREAMOS VARIABLES Y PROCESAMOS LOS DATOS
def procesado_1(df):
    # VARIABLE PATRONES DE VELAS
    df["MECHA_ARR"] = 0
    df["BALANCE"] = df['Close'] - df['Open']
    df.loc[(df["BALANCE"] > 0) , "MECHA_ARR"] = df["High"]-df["Close"]
    df.loc[(df["BALANCE"] < 0) , "MECHA_ARR"] = df["High"]-df["Open"]
    df["MECHA_ABA"] = 0
    df.loc[(df["BALANCE"] > 0) , "MECHA_ABA"] = df["Open"]-df["Low"]
    df.loc[(df["BALANCE"] < 0) , "MECHA_ABA"] = df["Close"]-df["Low"]
    df["CUERPO"] = abs(df["Open"]-df["Close"])
    df["RANGO"] = abs(df["High"]-df["Low"])
    df["VELA_DIA"] = 0
    df.loc[((df["BALANCE"] > 0) & (df["MECHA_ARR"] > df["CUERPO"]) & (df["MECHA_ABA"] > df["CUERPO"])) , "VELA_DIA"] = 1
    df.loc[((df["BALANCE"] > 0) & (df["MECHA_ARR"] < df["CUERPO"]) & (df["MECHA_ABA"] > df["CUERPO"])) , "VELA_DIA"] = 2
    df.loc[((df["BALANCE"] > 0) & (df["MECHA_ARR"] > df["CUERPO"]) & (df["MECHA_ABA"] < df["CUERPO"])) , "VELA_DIA"] = 3
    df.loc[((df["BALANCE"] > 0) & (df["MECHA_ARR"] < df["CUERPO"]) & (df["MECHA_ABA"] < df["CUERPO"])) , "VELA_DIA"] = 4
    df.loc[((df["BALANCE"] < 0) & (df["MECHA_ARR"] > df["CUERPO"]) & (df["MECHA_ABA"] > df["CUERPO"])) , "VELA_DIA"] = 5
    df.loc[((df["BALANCE"] < 0) & (df["MECHA_ARR"] < df["CUERPO"]) & (df["MECHA_ABA"] > df["CUERPO"])) , "VELA_DIA"] = 6
    df.loc[((df["BALANCE"] < 0) & (df["MECHA_ARR"] > df["CUERPO"]) & (df["MECHA_ABA"] < df["CUERPO"])) , "VELA_DIA"] = 7
    df.loc[((df["BALANCE"] < 0) & (df["MECHA_ARR"] < df["CUERPO"]) & (df["MECHA_ABA"] < df["CUERPO"])) , "VELA_DIA"] = 8
    df.loc[(df["RANGO"] > (20*df["CUERPO"])) , "VELA_DIA"] = 9
    df["VELA_AYER"] = df["VELA_DIA"].shift(1)
    df["VELA_AYER"] = df["VELA_AYER"].fillna(method="bfill")
    del df["MECHA_ARR"],df["MECHA_ABA"],df["CUERPO"],df["RANGO"],df["BALANCE"]

    #VARIABLE RSI CATEGORICO
    indicador_RSI = RSIIndicator(close = df["Close"], window = 14)
    df["RSI"] = indicador_RSI.rsi()
    df["RSI_CAT"] = 0
    df.loc[(df["RSI"] <= 30), "RSI_CAT"] = 1
    df.loc[(df["RSI"] >= 70), "RSI_CAT"] = 2
    df.loc[(df["RSI"] <  70) & (df["RSI"] >= 50), "RSI_CAT"] = 3
    df.loc[(df["RSI"] >  30) & (df["RSI"] <  50), "RSI_CAT"] = 4
    df["RSI_CAT"] = df["RSI_CAT"].fillna(method="ffill")
    df["RSI_CAT"] = df["RSI_CAT"].fillna(method="bfill")
    df["RSI_CAT"] = df["RSI_CAT"].replace(to_replace=0, method='ffill')
    df["RSI_CAT"] = df["RSI_CAT"].replace(to_replace=0, method='bfill')
    del df["RSI"]    

    # VARIABLE RENKO INVENTADA EN EL PROYECTO
    df["BAL"] = df['Close'] - df['Open']
    df["BAL_M"] = abs(df["BAL"])
    df["BAL_M"] = df["BAL_M"].rolling(10).mean()
    df["BAL_F"] = df['BAL']/df['BAL_M']
    df["+BAL_F"] = 0
    df.loc[(df["BAL_F"] > 0), "+BAL_F"] = df["BAL_F"]
    
    list_pos = df["+BAL_F"].tolist()
    suma_pos = []
    for li in list_pos:
        if li == 0:
            aux = 0
            suma_pos.append(aux)        
        if li != 0:
            suma_pos.append(aux + li)    
        aux = aux + li
    df["+BAL_F_SUM"] = suma_pos

    df["-BAL_F"] = 0
    df.loc[(df["BAL_F"] < 0), "-BAL_F"] = df["BAL_F"]

    list_neg = df["-BAL_F"].tolist()
    suma_neg = []
    for li in list_neg:
        if li == 0:
            aux = 0
            suma_neg.append(aux)        
        if li != 0:
            suma_neg.append(aux + li)    
        aux = aux + li
    df["-BAL_F_SUM"] = suma_neg

    df["COMPUTO"] = 0
    df.loc[(abs(df["+BAL_F_SUM"]) > 1), "COMPUTO"] = df["+BAL_F_SUM"]
    df.loc[(abs(df["-BAL_F_SUM"]) > 1), "COMPUTO"] = df["-BAL_F_SUM"]
    df["VARIABLE"] = df["COMPUTO"]
    while ((df.VARIABLE == 0).any()):
        df.loc[(df.VARIABLE == 0), "VARIABLE"] = df["VARIABLE"].shift(periods=1)
    df["VARIABLE"] = df["VARIABLE"].fillna(method="bfill")
    del df["BAL"],df["BAL_M"],df["BAL_F"],df["+BAL_F"],df["+BAL_F_SUM"]
    del df["-BAL_F"],df["-BAL_F_SUM"],df["COMPUTO"]

    #CLASE A PREDECIR
    df["CLASE"] = df['Close'].shift(-1) - df['Open'].shift(-1)
    df.loc[(df["CLASE"] >= 0), "CLASE"] = 1
    df.loc[(df["CLASE"] < 0), "CLASE"] = 0
    df["CLASE"] = df["CLASE"].fillna(method="ffill")
    del df["Open"],df["High"],df["Low"],df["Close"]    

    # DUMMIES DE LAS CATEGORIAS
    df = pd.get_dummies(df, columns=["VELA_DIA","VELA_AYER","RSI_CAT"], drop_first=True)

    # RETORNAMOS EL DF CON LAS VARIABLES
    print("al 1 var")
    return df

def prediccion_1(df_train, df_test):
    # VARIABLES
    df_tr = procesado_1(df_train)
    df_te = procesado_1(df_test)   
    
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
    modelo = LogisticRegression()
    modelo.fit(X_train, y_train)

    # PREDICCION
    prediccion = modelo.predict(X_test)

    # METRICAS
    acc = accuracy_score(y_test, prediccion)
    cm = confusion_matrix(y_test, prediccion)

    # RETORNAMOS LO QUE QUEREMOS
    print("al 1 pred")
    info = "POWERED BY AL1 NEKO"
    prediccion = pd.Series(prediccion)
    return acc,cm,y_test,prediccion,info      



