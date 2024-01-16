"""
UTILIZAMOS PANDAS - TA COMO LIBRERIA DE INDICADORES
UTILIZAMOS YFINANCE COMO PROVEEDOR DE DATOS 
"""

import pandas as pd
import pandas_ta as ta
import yfinance as yf
import matplotlib.pyplot as plt
import os
import datetime as dt

ticker = "V"
hoy = dt.datetime.now().strftime("%Y-%m-%d")

try:
    os.mkdir(os.path.join(os.getcwd(), 'KONC'))
except FileExistsError:
    pass

path = os.path.join(os.getcwd(), 'KONC')

data = yf.Ticker(ticker)
data = data.history(period="2y")
data.drop(['Dividends','Stock Splits'], axis=1, inplace=True)

def koncorpy(open, close, high, low, volume):
    NVI = ta.nvi(close, volume)
    PVI = ta.pvi(close, volume)
    HLC3 = ta.hlc3(high, low, close)
    OHLC4 = ta.ohlc4(open, high, low, close)
    MFI = ta.mfi(high, low, close, volume)
    RSI = ta.rsi(OHLC4, 14)
    BBO = ta.bbands(close, 25)
    
    OB1 = (BBO.iloc[:,2] + BBO.iloc[:,0])/2
    OB2 = BBO.iloc[:,2] - BBO.iloc[:,0]
    BBO1 = pd.Series(100*(close - OB1) / OB2)
    
    STOCH = ta.stoch(high, low, OHLC4, k=21, mamode='ema')
    NVIM = ta.ema(NVI, 15)
    PVIM = ta.ema(PVI, 15)

    NVIMIN = NVIM.rolling(90).min()
    NVIMAX = NVIM.rolling(90).max()
    PVIMAX = PVIM.rolling(90).max()
    PVIMIN = PVIM.rolling(90).min()
    OSCP = (PVI - PVIM) * 100 / (PVIMAX - PVIMIN)
    
    azul = (NVI - NVIM)*100 / (NVIMAX - NVIMIN)
    marron = (RSI + MFI + BBO1 + (STOCH.iloc[:,0] / 3))/2
    verde = marron + OSCP
    media = ta.ema(marron, 15)
    media_series = pd.Series(media, index=azul.index)

    df = pd.concat([azul, marron, verde, media_series], axis=1)
    df.columns = ['azul','marron','verde','media']
    return df


def graficoKoncpy ( df, symbol, data_close, path_konc): # GRAFICA Y GUARDA
        
        plt.style.use('fivethirtyeight')
        stock = df[-80:]

        # GRAFICAMOS LA SALIDA DE CRUCE OPTIMO
        fig=plt.figure(figsize=(12.2, 8), dpi=100)
        plt.suptitle(f'{symbol}')

        ax1= plt.subplot(211)  
        ax1.plot(data_close[-80:], label=f'Precio de cierre {symbol}', linewidth=3, alpha=0.5)
        ax1.legend (loc='upper left', fontsize='x-small')

        ax2=plt.subplot(212)

        indice=stock.index[-80:]
        media=0.0
        m_cp=(stock['marron'] >= media)
        m_cn=(stock['marron'] < media)
        v_cp=(stock['marron'] >= media)
        v_cn=(stock['marron'] < media)
        a_cp=(stock['marron'] >= media)
        a_cn=(stock['marron'] < media)

        ax2.plot(indice, stock['marron'], color='brown', linewidth=2, alpha=0.35)
        ax2.plot(indice, stock['azul'], color='blue', linewidth=2, alpha=0.35)
        ax2.plot(indice, stock['verde'], color='green', linewidth=2, alpha=0.35)
        ax2.plot(indice, stock['media'], color='red', linewidth=2, alpha=0.35)
        ax2.fill_between(indice, stock['marron'], media, where=m_cp, color="brown", alpha=0.5)
        ax2.fill_between(indice, stock['marron'], media, where=m_cn, color="brown", alpha=0.5)
        ax2.fill_between(indice, stock['verde'], media, where=v_cp, color="green", alpha=0.35)
        ax2.fill_between(indice, stock['verde'], media, where=v_cn, color="green", alpha=0.35)
        ax2.fill_between(indice, stock['azul'], media, where=a_cp, color="blue", alpha=0.35)
        ax2.fill_between(indice, stock['azul'], media, where=a_cn, color="blue", alpha=0.35)
        ax2.legend (loc='upper left', fontsize='x-small')
        
        fig = plt.savefig(os.path.join(path_konc, f'{hoy}_{symbol}_EST01.png'))

konc = koncorpy(data["Open"], data["Close"], data["High"], data["Low"], data["Volume"])

graficoKoncpy(konc, ticker, data['Close'], path)