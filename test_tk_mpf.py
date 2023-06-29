import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
import yfinance as yf
import tkinter as tk

mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='both', gridstyle=':')

stock = 'AAPL'
period = 'ytd'
interval = '1d'


data = yf.download(stock, period=period, interval=interval, group_by='ticker', prepost=True)

apds = [mpf.make_addplot(data['Adj Close'].rolling(window=9).mean(), type='line'),
        mpf.make_addplot(data['Adj Close'].rolling(window=20).mean(), type='line'),
        mpf.make_addplot(data['Adj Close'], type='line', panel=2, ylabel='RSI')]


fig, ax = mpf.plot(data, type='candle', title=f'\n{stock}', ylabel='Price ($)', style=s,
                   volume=True, xrotation=90, addplot=apds, returnfig=True)

top = tk.Toplevel()
canvas = FigureCanvasTkAgg(fig, top)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
