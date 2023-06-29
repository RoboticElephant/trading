import yfinance as yf
import pandas as pd
from pandas_datareader import data as pdr

yf.pdr_override()


def stocks_db(tickers, period='ytd', interval='1d', group_by='column'):
    # can add 'prepost=True' to have it pull pre/post regular market hours data
    df = yf.download(tickers, period=period, interval=interval, group_by=group_by, threads=True)
    return df


ticks = ['AAL', 'ADI', 'ADP', 'AKAM', 'ALXN', 'AMAT', 'AMD', 'APA', 'ATVI', 'CDNS', 'CDW', 'CERN', 'CHRW', 'CMCSA',
         'CPRT', 'CSCO', 'CSX', 'CTXS', 'DISCA', 'DISCK', 'DISH', 'DLTR', 'EA', 'ETFC', 'EXC', 'EXPD', 'EXPE', 'FANG',
         'FAST', 'FFIV', 'FISV', 'FITB', 'FLIR', 'FOX', 'FOXA', 'FTNT', 'GILD', 'HAS', 'HOLX', 'HSIC', 'INCY', 'INTC',
         'JBHT', 'KHC', 'LKQ', 'LNT', 'MAR', 'MCHP', 'MDLZ', 'MNST', 'MXIM', 'NDAQ', 'NLOK', 'NTAP', 'NTRS', 'NWL',
         'NWS', 'NWSA', 'PAYX', 'PBCT', 'PCAR', 'PEP', 'PFG', 'QCOM', 'QRVO', 'REG', 'ROST', 'SBUX', 'SWKS', 'TMUS',
         'TROW', 'TSCO', 'TTWO', 'TXN', 'UAL', 'VIAC', 'WBA', 'WDC', 'WYNN', 'XRAY', 'ZION']

# print(stocks_db(tickers=['AAL', 'ADI', 'ADP']).head())
# print(len(['AAL', 'ADI', 'ADP', 'AKAM', 'ALXN', 'AMAT', 'AMD', 'APA', 'ATVI', 'CDNS',
#                          'CDW', 'CERN', 'CHRW', 'CMCSA', 'CPRT', 'CSCO', 'CSX', 'CTXS', 'DISCA', 'DISCK', 'DISH',
#                          'DLTR', 'EA', 'ETFC', 'EXC', 'EXPD']))

# db1 = stocks_db(tickers=['AAL', 'ADI', 'ADP'])
# db2 = stocks_db(tickers=['AKAM', 'ALXN', 'AMAT'])
#
# db = pd.concat([db1, db2])
# print(db.columns)

# db = stocks_db(ticks[0])
#
# for tick in ticks[1:]:
#     db1 = stocks_db(tick)
#     db = pd.concat([db, db1])

db = pdr.get_data_yahoo(ticks, period='ytd', interval='1d')

print(db.head())
print(db.columns)
