import matplotlib.dates as mdates
import mplfinance as mpf
import yfinance as yf
import pandas as pd
# style.use('ggplot')

mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='both', gridstyle=':')


def graph_data(stock, period='ytd', interval='1d'):
    data = yf.download(stock, period=period, interval=interval, group_by='ticker', prepost=True)

    apds = [mpf.make_addplot(data['Adj Close'].rolling(window=9).mean(), type='line'),
            mpf.make_addplot(data['Adj Close'].rolling(window=20).mean(), type='line'),
            mpf.make_addplot(data['Adj Close'], type='line', panel=2, ylabel='RSI')]

    # style='charles'
    mpf.plot(data, type='candle', title=f'\n{stock}', ylabel='Price ($)', style=s,
             volume=True, xrotation=90, addplot=apds)


if __name__ == '__main__':
    graph_data('AAPL')
