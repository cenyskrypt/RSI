import pandas as pd
#import matplotlib.pyplot as plt
import streamlit as st
import datetime 
import yfinance as yf
import plotly.express as px

st.set_page_config("Relative Strength Index", layout='wide')
st.sidebar.header("Select Ticker and Start and End date")

today = datetime.date.today()
ticker = st.sidebar.text_input("Select Ticker","AAPL")
start_date = st.sidebar.text_input("Start Date","2023-11-15")
end_date = st.sidebar.text_input("End Date",f'{today}')


start = pd.to_datetime(start_date)
end = pd.to_datetime(end_date)

info = yf.Ticker(ticker).info
name = info.get('longName')
st.write(ticker+ " - " + name)

data = yf.download(ticker,start,end)
#st.dataframe(data,width=1800,height=600)


df = pd.DataFrame(data)


def get_rsi(close,daysback):
    retrace = close.diff()
    up = []
    down = []

    for i in range(len(retrace)):
        if retrace[i] <0:
            up.append(0)
            down.append(retrace[i])
        else:
            up.append(retrace[i])
            down.append(0)
    
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com=daysback-1, adjust=False).mean()
    down_ewm = down_series.ewm(com=daysback-1, adjust=False).mean()

    rs = up_ewm/down_ewm
    rsi = 100-(100/(1+rs))
    rsi_df = pd.DataFrame(rsi).rename(columns={0:"rsi"}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    return rsi_df[3:]


df['rsi_14'] = get_rsi(df['Close'],14)
df = df.dropna()

#ŚREDNIA RUCHOMA
df['30_mean'] = df['Close'].rolling(window=20).mean()
df['10_mean'] = df['Close'].rolling(window=10).mean()

#CENA ZAMKNIĘCIA
fig = px.line(x=df.index, y=df['Close'], title="Closing Price")
fig.update_layout(xaxis_title='Data', yaxis_title="price")
fig.add_scatter(x=df.index, y=df['30_mean'], mode='lines', name='Średnia ruchoma 20-dniowa')
fig.add_scatter(x=df.index, y=df['10_mean'], mode='lines', name='Średnia ruchoma 10-dniowa')
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
st.plotly_chart(fig, use_container_width=True)

#RSI
fig_rsi = px.line(x=df.index, y=df['rsi_14'], title="RSI")
fig_rsi.update_layout(xaxis_title='Data', yaxis_title="RSI")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
st.plotly_chart(fig_rsi, use_container_width=True)















