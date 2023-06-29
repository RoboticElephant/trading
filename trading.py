import matplotlib
import mplfinance as mpf
import tkinter as tk
# this will add style to the windows
from tkinter import ttk
from matplotlib import style
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import math
from tkinter import filedialog
import sys
from tkinter import PhotoImage

# TODO List:
# 1) Look into the Graph class
# 2) Add a new combobox that only contains different stocks based on date.

matplotlib.use('TkAgg')
style.use('ggplot')

mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
s = mpf.make_mpf_style(marketcolors=mc, y_on_right=False, gridaxis='both', gridstyle=':')

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)

# ===========================
# Global Variables
# ===========================
ANY = 'ANY'
PADDING = 2
DEBUG = False

# ===========================
# END OF Global Variables
# ===========================


def pop_up_msg(msg):
    popup = tk.Tk()
    popup.wm_title('!')
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    button1 = ttk.Button(popup, text='Okay', command=popup.destroy)
    button1.pack()
    popup.mainloop()


def save_to_file(cont, sel=None):
    directory = filedialog.asksaveasfilename(defaultextension='.txt')
    if directory is not None:
        with open(directory, 'w', encoding='utf-8') as fp:
            if sel is None:
                for index in list(cont.scan_cmb['values']):
                    fp.write(f"{index}\n")
            else:
                for index in list(cont.diff_scan_cmb['values']):
                    fp.write(f"{index}\n")


class WebSetUp:
    @staticmethod
    def url_(exchange=ANY, index=ANY, avg_vol=200, low_price=1, high_price=100, gap=ANY):
        return f'https://finviz.com/screener.ashx?v=111&f={exchange}geo_usa,{index}sh_avgvol_o{avg_vol},' \
            f'sh_opt_option,sh_price_{low_price}to{high_price},{gap}&r='

    @staticmethod
    def make_request(url, pg=1):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.98 Safari/537.36'}
        response = requests.get(f'{url}{pg}', headers=headers)

        if response.status_code != 200:
            print("Invalid web url")
            quit()

        return response

    @staticmethod
    def total_pages(url, qty_pg=20):
        response = WebSetUp.make_request(url=url)
        soup = BeautifulSoup(response.text, 'html.parser')
        total = soup.find(attrs={'class': 'count-text'}).text.split(" ")[1]
        return math.ceil(int(total) / qty_pg)

    @staticmethod
    def grab_tickers(exchange=ANY, index=ANY, avg_vol=200, low_price=1, high_price=100, gap=''):
        tickers = []
        url = WebSetUp.url_(exchange, index, avg_vol, low_price, high_price, gap)
        pages = WebSetUp.total_pages(url=url)
        if DEBUG:
            print('Grabbing tickers from finviz...')
        for page in range(pages):
            response = WebSetUp.make_request(url, pg=(page * 20 + 1))

            soup = BeautifulSoup(response.text, 'html.parser')
            t_rows = soup.find_all(attrs={'class': 'screener-link-primary'})
            for row in t_rows:
                tickers.append(row.text)
        return tickers

    @staticmethod
    def stocks_db(tickers, period='ytd', interval='1d', group_by='column'):
        # can add 'prepost=True' to have it pull pre/post regular market hours data
        df = yf.download(tickers, period=period, interval=interval, group_by=group_by)
        return df


# this is inheriting from tk.Tk
class StockStrategiesScanner(tk.Tk):
    # args are typical parameters and kwargs are dictionaries
    def __init__(self, *args, **kwargs):
        # initialize inherited class
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "JB's Stock Scanner and Strategies")

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Save Settings', command=lambda: pop_up_msg('Not supported just yet!'))
        filemenu.add_command(label='Save Tickers', command=lambda: pop_up_msg('Not supported just yet!'))
        filemenu.add_command(label='Save Database', command=lambda: pop_up_msg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=quit)
        menubar.add_cascade(label='File', menu=filemenu)

        # add the menu bar to the window
        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        self.available_frames = [StrategyPage, StockPage]

        for F in self.available_frames:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StrategyPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # bring the frame to the top for the user to see
        frame.tkraise()

    def show_stock_info(self, cont, stock):
        self.frames[cont].set_stock(stock)
        self.show_frame(cont)


class StrategyPage(tk.Frame):
    # TODO add , '3BP', '4BP'; need to create a strategy for this: 3BP, 4BP
    STRATEGY = ['Power X', 'OptionAlpha']
    EXCHANGES = {'ANY': '', 'NASDAQ': 'exch_nasd,', 'NYSE': 'exch_nyse,'}
    GAPPING = {'ANY': '', 'Gap UP': 'ta_gap_u,', 'Gap Down': 'ta_gap_d,'}
    INDEXES = {'ANY': '', 'DJIA': 'idx_dji,', 'S&P500': 'idx_sp500,'}
    DIRECTIONS = ['BUY', 'SELL']

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        controller.bind('<Return>', self.scan_stocks)

        ttk.Label(self, text=(
            """
            This program is used to find stocks that
            are either OptionAlpha Strategy or
            Power X Strategy.
            
            All the fields are selectable to help 
            find the right stock.
            """), justify='center', anchor=tk.CENTER, font=LARGE_FONT).pack(pady=10, padx=10, fill=tk.X)

        scanner_frame = ttk.LabelFrame(self, text='Stock Scanner Criteria')
        scanner_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.db = None
        # self.controller = controller

        # **************** Row 0 ****************
        this_row = 0
        # ========= Set up the Exchange =========
        ttk.Label(scanner_frame, text='Exchange:', justify='center').grid(row=this_row, sticky='ne', pady=PADDING)
        self.exchange_str = tk.StringVar(self, value=ANY, name='exchange_str')
        ttk.Combobox(scanner_frame, textvariable=self.exchange_str,
                     values=list(self.EXCHANGES.keys())).grid(row=this_row, column=1, sticky='nsew', pady=PADDING)
        # ========= Set up the Index =========
        ttk.Label(scanner_frame, text='Index:', justify='center').grid(row=this_row, column=4,
                                                                       sticky='ne', pady=PADDING)
        self.index_str = tk.StringVar(self, value=ANY, name='index_str')
        ttk.Combobox(scanner_frame, textvariable=self.index_str,
                     values=list(self.INDEXES.keys())).grid(row=this_row, column=5, sticky='nsew', pady=PADDING)
        # ========= Set up the Gap =========
        ttk.Label(scanner_frame, text='Gap:', justify='center').grid(row=this_row, column=8, sticky='ne', pady=PADDING)
        self.gap_str = tk.StringVar(self, value=ANY, name='gap_str')
        ttk.Combobox(scanner_frame, textvariable=self.gap_str,
                     values=list(self.GAPPING.keys())).grid(row=this_row, column=9, sticky='nsew', pady=PADDING)

        # **************** Row 1 ****************
        this_row = 1
        # ========= Set up Min Price =========
        ttk.Label(scanner_frame, text='Min Price:', justify='center').grid(row=this_row, sticky='ne', pady=PADDING)
        # The 'name' is added that way if you want to add a trace, you know what is being called
        # The 'value' will give an initial value that it is set to
        self.min_share_price = tk.IntVar(self, value=1, name='min_share_price')
        ttk.Entry(scanner_frame, textvariable=self.min_share_price).grid(row=this_row, column=1,
                                                                         sticky=tk.NSEW, pady=PADDING)
        # ========= Set up Max Price =========
        ttk.Label(scanner_frame, text='Max Price:',
                  justify='center').grid(row=this_row, column=4, sticky='ne', pady=PADDING)
        self.max_share_price = tk.IntVar(self, value=150, name='max_share_price')
        ttk.Entry(scanner_frame, textvariable=self.max_share_price).grid(row=this_row, column=5,
                                                                         sticky=tk.NSEW, pady=PADDING)
        # ========= Set up Max Price =========
        ttk.Label(scanner_frame, text='Avg Vol (K):',
                  justify='center').grid(row=this_row, column=8, sticky='ne', pady=PADDING)
        self.avg_vol = tk.IntVar(self, value=200, name='avg_vol')
        # This will call the callback every time the value changes
        # self.avg_vol.trace_variable('w', callback=self.callback)
        ttk.Entry(scanner_frame, textvariable=self.avg_vol).grid(row=this_row, column=9, sticky=tk.NSEW, pady=PADDING)

        # ******************** Row 2 ********************
        this_row = 2
        # ========= Scan for stocks =========
        ttk.Button(scanner_frame, text='Search',
                   command=lambda: self.scan_stocks()).grid(row=this_row, column=9, sticky=tk.NSEW, pady=PADDING)

        # ******************** Row 3 ********************
        this_row = 3
        ttk.Separator(scanner_frame, orient=tk.HORIZONTAL).grid(row=this_row, columnspan=10, sticky='ew', pady=PADDING)

        # ******************** Row 4 ********************
        this_row = 4
        # ========= Show specific stock chart =========
        ttk.Label(scanner_frame, text='Search a Stock:', justify='center').grid(row=this_row, sticky='ne', pady=PADDING)
        self.scan_stock_str = tk.StringVar(self, name='scan_stock_str')
        ttk.Entry(scanner_frame, textvariable=self.scan_stock_str).grid(row=this_row, column=1,
                                                                        sticky=tk.NSEW, pady=PADDING)
        ttk.Button(scanner_frame, text='Search',
                   command=lambda: controller.show_stock_info(StockPage,
                                                              self.scan_stock_str.get())).grid(row=this_row, column=4,
                                                                                               sticky='nsew',
                                                                                               pady=PADDING)
        ttk.Label(scanner_frame,
                  text='(This can be run independent of the strategy)',
                  justify='center').grid(row=this_row, column=5, columnspan=4, sticky=tk.NSEW, pady=PADDING)

        # ******************** Row 5 ********************
        this_row = 5
        ttk.Separator(scanner_frame, orient=tk.HORIZONTAL).grid(row=this_row, columnspan=10, sticky='ew', pady=PADDING)

        # ******************** Row 6 ********************
        this_row = 6
        # ========= Set up the Strategy =========
        ttk.Label(scanner_frame, text='Strategy:', justify='center').grid(row=this_row, sticky='ne', pady=PADDING)
        self.strategy_str = tk.StringVar(self, value=self.STRATEGY[0], name='strategy_str')
        ttk.Combobox(scanner_frame, textvariable=self.strategy_str,
                     values=self.STRATEGY).grid(row=this_row, column=1, sticky='nsew', pady=PADDING)
        # ========= Set up whether to Buy or Sell =========
        ttk.Label(scanner_frame, text='Direction:', justify='center').grid(row=this_row, column=4,
                                                                           sticky='ne', pady=PADDING)
        self.direction_str = tk.StringVar(self, value=self.DIRECTIONS[0], name='marker_str')
        ttk.Combobox(scanner_frame, textvariable=self.direction_str,
                     values=self.DIRECTIONS).grid(row=this_row, column=5, sticky=tk.NSEW, pady=PADDING)

        # ******************** Row 7 ********************
        this_row = 7
        # ========= Setup the amount of days to span =========
        ttk.Label(scanner_frame, text='Days Cumulative:', justify='center').grid(row=this_row, sticky='ne',
                                                                                 pady=PADDING)
        self.days_int = tk.IntVar(self, value=1, name='days_int')
        ttk.Entry(scanner_frame, textvariable=self.days_int).grid(row=this_row, column=1, sticky='nsew', pady=PADDING)

        self.strategy_btn = ttk.Button(scanner_frame, text='Run', command=lambda: self.run_strategy())
        self.strategy_btn.grid(row=this_row, column=4, sticky='nsew', pady=PADDING)
        self.strategy_btn.grid_remove()

        # self.new_tickers_btn = ttk.Button(scanner_frame, text='Find New Tickers',
        #                                   command=lambda: self.find_diff_stocks(True))
        # self.new_tickers_btn.grid(row=this_row, column=5, sticky=tk.NSEW, pady=PADDING)
        # self.new_tickers_btn.grid_remove()

        # ******************** Row 8 ********************
        this_row = 8
        ttk.Separator(scanner_frame, orient=tk.HORIZONTAL).grid(row=this_row, columnspan=10, sticky='ew', pady=PADDING)

        # ******************** Row 9 ********************
        this_row = 9
        self.scan_lbl = ttk.Label(scanner_frame, text='hello', justify='center')
        self.scan_lbl.grid(row=this_row, columnspan=4, sticky=tk.NSEW, pady=PADDING)
        self.scan_lbl.grid_remove()

        # ******************** Row 10 ********************
        this_row = 10
        # ========= Setup Stock Scanner Results =========
        self.stock_selection_str = tk.StringVar(self, name='stock_selection')
        self.stock_selection_str.trace_variable('w', callback=self.callback)
        self.scan_cmb = ttk.Combobox(scanner_frame, textvariable=self.stock_selection_str, values=[])
        self.scan_cmb.grid(row=this_row, columnspan=5, sticky='nsew', pady=PADDING)
        self.scan_cmb.grid_remove()

        # ========= Save button to save tickers =========
        self.save_btn = ttk.Button(scanner_frame, text='Save All Tickers', command=lambda: save_to_file(self))
        self.save_btn.grid(row=this_row, column=5, sticky='nsew', pady=PADDING)
        self.save_btn.grid_remove()

        # ========= Setup Show Chart Button =========
        self.chart_btn = ttk.Button(scanner_frame, text='Show Chart',
                                    command=lambda: self.create_chart(self.stock_selection_str.get(), self.db))
        self.chart_btn.grid(row=this_row, column=8, sticky='nsew', pady=PADDING)
        self.chart_btn.grid_remove()

        # ========= Setup Show More Stock Info Button =========
        self.info_btn = ttk.Button(scanner_frame, text='Show Stock Info',
                                   command=lambda: controller.show_stock_info(StockPage,
                                                                              self.stock_selection_str.get()))
        self.info_btn.grid(row=this_row, column=9, sticky='nsew', pady=PADDING)
        self.info_btn.grid_remove()



        # ******************** Row 11 ********************
        this_row = 11
        # ========= Setup Stock Scanner Results =========
        self.diff_stock_sel_str = tk.StringVar(self, name='diff_stock_selection')
        self.diff_stock_sel_str.trace_variable('w', callback=self.callback)
        self.diff_scan_cmb = ttk.Combobox(scanner_frame, textvariable=self.diff_stock_sel_str, values=[])
        self.diff_scan_cmb.grid(row=this_row, columnspan=5, sticky='nsew', pady=PADDING)
        self.diff_scan_cmb.grid_remove()

        # ========= Save button to save tickers =========
        self.diff_save_btn = ttk.Button(scanner_frame, text='Save Diff Tickers',
                                        command=lambda: save_to_file(self, 'diff'))
        self.diff_save_btn.grid(row=this_row, column=5, sticky='nsew', pady=PADDING)
        self.diff_save_btn.grid_remove()

        # ========= Setup Show Chart Button =========
        self.diff_chart_btn = ttk.Button(scanner_frame, text='Show Chart',
                                         command=lambda: self.create_chart(self.diff_stock_sel_str.get(), self.db))
        self.diff_chart_btn.grid(row=this_row, column=8, sticky='nsew', pady=PADDING)
        self.diff_chart_btn.grid_remove()

        # ========= Setup Show More Stock Info Button =========
        self.diff_info_btn = ttk.Button(scanner_frame, text='Show Stock Info',
                                        command=lambda: controller.show_stock_info(StockPage,
                                                                                   self.diff_stock_sel_str.get()))
        self.diff_info_btn.grid(row=this_row, column=9, sticky='nsew', pady=PADDING)
        self.diff_info_btn.grid_remove()


        # # ******************** Row 12 ********************
        # this_row = 12

    def scan_stocks(self, event=None):
        exchange, index, gap = self.exchange_str.get(), self.index_str.get(), self.gap_str.get()
        min_price, max_price, avg_vol = self.min_share_price.get(), self.max_share_price.get(), self.avg_vol.get()

        if DEBUG:
            print('Grabbing Tickers')
        tickers = WebSetUp.grab_tickers(exchange=self.EXCHANGES[exchange], index=self.INDEXES[index], avg_vol=avg_vol,
                                        low_price=min_price, high_price=max_price, gap=self.GAPPING[gap])
        if DEBUG:
            print(tickers)
        self.db = WebSetUp.stocks_db(tickers)

        if self.db is not None:
            self.strategy_btn.grid()
            # self.new_tickers_btn.grid()

    def run_strategy(self):
        strategy = self.strategy_str.get()
        stocks = []
        previous_day = []
        if DEBUG:
            print('Running Power X Strategy')
        if strategy == self.STRATEGY[0]:
            stocks = StockCalculations.power_x_strategy(self.db, marker=self.direction_str.get(),
                                                        days_spanning=self.days_int.get())
            previous_day = StockCalculations.power_x_strategy(self.db, marker=self.direction_str.get(),
                                                              days_spanning=(self.days_int.get() + 1))

        elif strategy == self.STRATEGY[1]:
            stocks = StockCalculations.option_alpha_strategy(self.db, marker=self.direction_str.get(),
                                                             days_spanning=self.days_int.get())
            previous_day = StockCalculations.option_alpha_strategy(self.db, marker=self.direction_str.get(),
                                                                   days_spanning=(self.days_int.get() + 1))

        diff_stocks = stocks.copy()

        if diff_stocks and previous_day:
            [diff_stocks.remove(day) for day in previous_day]

        if DEBUG:
            print(stocks)

        # This will show the label and combobox after searching
        self.scan_lbl.grid()
        self.scan_lbl['text'] = f'{strategy} Stock Picks:'

        if stocks:
            self.scan_cmb.grid()
            self.scan_cmb['values'] = stocks
            self.save_btn.grid()
        if diff_stocks:
            self.diff_scan_cmb.grid()
            self.diff_scan_cmb['values'] = diff_stocks
            self.diff_save_btn.grid()

    @staticmethod
    def create_chart(stock, data=None):
        if data is None:
            data = yf.download(stock, period='ytd', interval='1d', group_by='column')
        else:
            # This will grab only the stock information for the specific stock we want. i.e. Adj Close, Close,
            # High Low Volume
            data = data.iloc[:, data.columns.get_level_values(1) == stock]
            # This will delete the stock column and reduce the index size
            data.columns = data.columns.droplevel(1)
        loc_stock = yf.Ticker(stock)

        apds = [mpf.make_addplot(data['Adj Close'].rolling(window=9).mean(), type='line'),
                mpf.make_addplot(data['Adj Close'].rolling(window=20).mean(), type='line'),
                mpf.make_addplot(StockCalculations.stochastic_oscillator(data), type='line', panel=2, ylabel='%K (b)',
                                 color='b'),
                mpf.make_addplot(StockCalculations.relative_strength_index(data), type='line', panel=2,
                                 ylabel='RSI (o)', color='orange'),
                mpf.make_addplot(StockCalculations.commodity_channel_index(data), type='line', panel=3, ylabel='CCI',
                                 color='purple'),
                mpf.make_addplot(StockCalculations.moving_average_convergence_divergence(data, s_period=15,
                                                                                         l_period=30),
                                 type='line', panel=4, ylabel='MACD', color='fuchsia')]

        mpf.plot(data, type='candle',
                 title=f'\n{loc_stock.info["shortName"]} ({stock.upper()}):\nClose ${data["Close"].iloc[-1]:.2f}',
                 ylabel='Price ($)',
                 style=s, volume=True, xrotation=45, addplot=apds, panel_ratios=(5, 1), ylabel_lower='Vol')

    def callback(self, *args):
        if DEBUG:
            print("Callback called with: ", args)
        # Show the button when the stock is selected
        if args[0] == 'stock_selection':
            self.chart_btn.grid()
            self.info_btn.grid()
        elif args[0] == 'diff_stock_selection':
            self.diff_chart_btn.grid()
            self.diff_info_btn.grid()

    def find_diff_stocks(self):
        print("Shouldn't be here any more.")
        strategy = self.strategy_str.get()
        direction = self.direction_str.get()
        days = self.days_int.get()
        current_day = []
        previous_day = []
        if strategy == self.STRATEGY[0]:
            current_day = StockCalculations.power_x_strategy(self.db, marker=direction, days_spanning=days)
            previous_day = StockCalculations.power_x_strategy(self.db, marker=direction, days_spanning=(days + 1))
        elif strategy == self.STRATEGY[1]:
            current_day = StockCalculations.option_alpha_strategy(self.db, marker=direction, days_spanning=days)
            previous_day = StockCalculations.option_alpha_strategy(self.db, marker=direction, days_spanning=(days + 1))

        if current_day and previous_day:
            [current_day.remove(day) for day in previous_day]
            return current_day

            # directory = filedialog.asksaveasfilename(defaultextension='.txt')
            # if directory is not None:
            #     with open(directory, 'w', encoding='utf-8') as fp:
            #         for index in current_day:
            #             fp.write(f"{index}\n")
        else:
            print("The lists are empty")


class StockPage(tk.Frame):
    PANEL_SELECTION = [0, 2, 3, 4, 5]

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.stock = ''
        self.stock_info = ''
        self.stock_db = ''

        self.stock_lbl = ttk.Label(self, text='', justify='center', anchor=tk.CENTER, font=LARGE_FONT)
        self.stock_lbl.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(self, text='Go Back', command=lambda: controller.show_frame(StrategyPage)).pack(side=tk.TOP)

        chart_frame = tk.LabelFrame(self, text="Chart Criteria")
        chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        options_frame = tk.LabelFrame(self, text="Options Chain")
        options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        # -----------------------------------------------------------
        # ----------------------- Chart Frame -----------------------
        # -----------------------------------------------------------
        # **************** Row 0 ****************
        this_row = 0
        # ========= Set up the Headings =========
        ttk.Label(chart_frame, text='Indicator:',
                  font="Verdana 12 underline").grid(row=this_row, sticky=tk.NSEW)
        ttk.Label(chart_frame, text='Chart Loc:',
                  font="Verdana 12 underline").grid(row=this_row, column=2, sticky=tk.NSEW)

        # **************** Row 1 ****************
        this_row = 1
        # ========= Set up the EMA Short =========
        self.ema_sh_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='EMA Short', variable=self.ema_sh_int).grid(row=this_row, sticky=tk.NSEW)
        self.ema_sh_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[0], name='ema_sh_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.ema_sh_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # ========= Set up the Bid/Ask =========
        ttk.Label(chart_frame, text='Bid:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=4)
        self.bid_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.bid_lbl.grid(row=this_row, column=5)
        ttk.Label(chart_frame, text='Ask:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=7)
        self.ask_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.ask_lbl.grid(row=this_row, column=8)

        # **************** Row 2 ****************
        this_row = 2
        # ========= Set up the EMA Long =========
        self.ema_lg_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='EMA Long', variable=self.ema_lg_int).grid(row=this_row, sticky=tk.NSEW)
        self.ema_lg_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[0], name='ema_lg_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.ema_lg_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # ========= Set up the High/Low =========
        ttk.Label(chart_frame, text='High:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=4)
        self.high_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.high_lbl.grid(row=this_row, column=5)
        ttk.Label(chart_frame, text='Low:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=7)
        self.low_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.low_lbl.grid(row=this_row, column=8)

        # **************** Row 3 ****************
        this_row = 3
        # ========= Set up the RSI =========
        self.rsi_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='RSI', variable=self.rsi_int).grid(row=this_row, sticky=tk.NSEW)
        self.rsi_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[1], name='rsi_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.rsi_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # ========= Set up the Open/Close =========
        ttk.Label(chart_frame, text='Open:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=4)
        self.open_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.open_lbl.grid(row=this_row, column=5)
        ttk.Label(chart_frame, text='Close:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=7)
        self.close_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.close_lbl.grid(row=this_row, column=8)

        # **************** Row 4 ****************
        this_row = 4
        # ========= Set up the Stochastic =========
        self.stochastic_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='Stochastic', variable=self.stochastic_int).grid(row=this_row, sticky=tk.NSEW)
        self.stochastic_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[1], name='stochastic_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.stochastic_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # ========= Set up the Float Shares =========
        ttk.Label(chart_frame, text='Float Shares:', justify='right', anchor=tk.CENTER,
                  font="Verdana 8 underline").grid(row=this_row, column=4, columnspan=2)
        self.float_lbl = ttk.Label(chart_frame, text='', justify='center', anchor=tk.CENTER, font="Verdana 8 bold")
        self.float_lbl.grid(row=this_row, column=6, columnspan=3)

        # **************** Row 5 ****************
        this_row = 5
        # ========= Set up the MACD =========
        self.macd_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='MACD', variable=self.macd_int).grid(row=this_row, sticky=tk.NSEW)
        self.macd_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[3], name='macd_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.macd_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # **************** Row 6 ****************
        this_row = 6
        # ========= Set up the CCI =========
        self.cci_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='CCI', variable=self.cci_int).grid(row=this_row, sticky=tk.NSEW)
        self.cci_pan_int = tk.IntVar(self, value=self.PANEL_SELECTION[2], name='cci_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.cci_pan_int,
                     values=self.PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # **************** Vertical Spanned ****************
        # ========= Set up the Separator =========
        ttk.Separator(chart_frame, orient=tk.VERTICAL).grid(row=1, rowspan=6, column=3, sticky=tk.NS,
                                                            pady=PADDING, padx=10)
        ttk.Separator(chart_frame, orient=tk.VERTICAL).grid(row=1, rowspan=3, column=6, sticky=tk.NS,
                                                            pady=PADDING, padx=10)
        ttk.Separator(chart_frame, orient=tk.VERTICAL).grid(row=1, rowspan=6, column=9, sticky=tk.NS,
                                                            pady=PADDING, padx=10)

        # ========= Set up the Show Chart Button =========
        ttk.Button(chart_frame, text='Show Chart',
                   command=lambda: self.show_chart()).grid(row=1, rowspan=6, column=10,
                                                                      sticky=tk.NSEW, pady=PADDING)

        # -------------------------------------------------------------
        # ----------------------- Options Frame -----------------------
        # -------------------------------------------------------------
        ttk.Button(options_frame, text='CALL',
                   command=lambda: self.add_options('CALL')).grid(row=0, column=0, columnspan=6,
                                                                  sticky=tk.NSEW, pady=PADDING)
        ttk.Separator(options_frame, orient=tk.VERTICAL).grid(row=0, column=6, sticky=tk.NS, pady=PADDING)
        ttk.Button(options_frame, text='PUT',
                   command=lambda: self.add_options('PUT')).grid(row=0, column=7, columnspan=6,
                                                                 sticky=tk.NSEW, pady=PADDING)

        self.tree = ttk.Treeview(options_frame)
        self.tree.grid(row=1, rowspan=15, column=0, columnspan=12, sticky='nsew', pady=PADDING)

        # Defining number of columns
        self.tree["columns"] = ("1", "2", "3", "4", "5", "6", "7", "8")

        # Defining Headings
        self.tree['show'] = 'headings'

        # Assigning the width and anchor to  the respective columns
        for ind in range(1, 8):
            self.tree.column(f"{ind}", width=90, anchor='c')

        # Assigning the heading names to the respective columns
        # 'date', 'openInterest', 'volume', 'impliedVolatility', 'lastPrice', 'bid', 'ask', 'strike'
        self.tree.heading("1", text="Date")
        self.tree.heading("2", text="Open Int")
        self.tree.heading("3", text="Vol")
        self.tree.heading("4", text="IV")
        self.tree.heading("5", text="Mark")
        self.tree.heading("6", text="BID")
        self.tree.heading("7", text="ASK")
        self.tree.heading("8", text="Strike")

    def set_stock(self, stock):
        self.stock = stock
        self.stock_info = yf.Ticker(stock)
        self.stock_lbl['text'] = f"{self.stock_info.info['shortName']} [{stock.upper()}]"
        self.set_chart_frame()
        self.tree.delete(*self.tree.get_children())

    def set_chart_frame(self):
        self.ema_sh_int.set(0)
        self.ema_lg_int.set(0)
        self.rsi_int.set(0)
        self.stochastic_int.set(0)
        self.macd_int.set(0)
        self.cci_int.set(0)
        self.bid_lbl['text'] = f"${self.stock_info.info['bid']:.2f}"
        self.ask_lbl['text'] = f"${self.stock_info.info['ask']:.2f}"
        self.high_lbl['text'] = f"${self.stock_info.info['dayHigh']:.2f}"
        self.low_lbl['text'] = f"${self.stock_info.info['dayLow']:.2f}"
        self.open_lbl['text'] = f"${self.stock_info.info['open']:.2f}"
        self.close_lbl['text'] = f"${self.stock_info.info['previousClose']:.2f}"
        self.float_lbl['text'] = f"{self.stock_info.info['floatShares']}"

    def add_options(self, call_put):
        self.tree.delete(*self.tree.get_children())
        for opt in self.stock_info.options:
            self.tree.insert('', index='end', iid=opt, text=opt, values=(opt, '', '', '', '', '', '', ''))
            option_chain = self.stock_info.option_chain(opt)
            if call_put == 'CALL':
                option = option_chain.calls[['inTheMoney', 'openInterest', 'volume', 'impliedVolatility', 'lastPrice',
                                             'bid', 'ask', 'strike']]
            else:
                option = option_chain.puts[['inTheMoney', 'openInterest', 'volume', 'impliedVolatility', 'lastPrice',
                                            'bid', 'ask', 'strike']]
            for index in range(option.shape[0]):
                if option['inTheMoney'].iloc[index]:
                    tag = 'itm'
                else:
                    tag = 'otm'
                self.tree.insert(opt, index='end', text='strike', tags=(tag,),
                                 values=('', option['openInterest'].iloc[index], option['volume'].iloc[index],
                                         f"{option['impliedVolatility'].iloc[index]:.3f}",
                                         option['lastPrice'].iloc[index], option['bid'].iloc[index],
                                         option['ask'].iloc[index], option['strike'].iloc[index]))
        self.tree.tag_configure('itm', background='green')
        # self.tree.tag_configure('otm', background='blue')

    def show_chart(self):
        self.stock_db = yf.download(self.stock, period='ytd', interval='1d', group_by='column')
        
        apds = []
        # If the user selects certain boxes then add them to the display of the chart
        if self.ema_sh_int.get():
            apds.append(mpf.make_addplot(self.stock_db['Adj Close'].rolling(window=9).mean(),
                                         panel=self.ema_sh_pan_int.get(), type='line'))
        if self.ema_lg_int.get():
            apds.append(mpf.make_addplot(self.stock_db['Adj Close'].rolling(window=20).mean(),
                                         panel=self.ema_lg_pan_int.get(), type='line'))
        if self.rsi_int.get():
            apds.append(mpf.make_addplot(StockCalculations.relative_strength_index(self.stock_db), type='line',
                                         panel=self.rsi_pan_int.get(), ylabel='RSI (o)', color='orange'))
        if self.stochastic_int.get():
            apds.append(mpf.make_addplot(StockCalculations.stochastic_oscillator(self.stock_db), type='line',
                                         panel=self.stochastic_pan_int.get(), ylabel='%K (b)', color='b'))
        if self.macd_int.get():
            apds.append(mpf.make_addplot(StockCalculations.moving_average_convergence_divergence(self.stock_db,
                                                                                                 s_period=15,
                                                                                                 l_period=30),
                                         type='line', panel=self.macd_pan_int.get(), ylabel='MACD', color='fuchsia'))
        if self.cci_int.get():
            apds.append(mpf.make_addplot(StockCalculations.commodity_channel_index(self.stock_db), type='line',
                                         panel=self.cci_pan_int.get(), ylabel='CCI', color='purple'))

        mpf.plot(self.stock_db, type='candle',
                 title=f'\n{self.stock_info.info["shortName"]} ({self.stock.upper()}):\n'
                 f'Close ${self.stock_db["Close"].iloc[-1]:.2f}', ylabel='Price ($)',
                 style=s, volume=True, xrotation=45, addplot=apds, panel_ratios=(5, 1), ylabel_lower='Vol')


class StockCalculations:

    @staticmethod
    def stochastic_oscillator(db, win_len=14, period=3):
        # this is technically the stochastic %K Fast
        stochastic = ((db['Close'] - db['Low'].rolling(win_len).min()) /
                      (db['High'].rolling(win_len).max() - db['Low'].rolling(win_len).min())) * 100.0
        # This is the Fast %D or %K slow
        return stochastic.rolling(period).mean()

    @staticmethod
    def relative_strength_index(db, win_len=14):
        # Get just the adjusted close
        close = db['Adj Close']
        # get difference in price from previous step
        delta = close.diff()

        # make the positive gains (up) and negative gains (down) series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # Calculate the EWMA (Exponentially Weighted Moving Average)
        roll_up = up.ewm(span=win_len, adjust=False).mean()
        roll_down = down.abs().ewm(span=win_len, adjust=False).mean()
        rs = roll_up / roll_down
        return 100.0 - (100.0 / (1.0 + rs))

    @staticmethod
    def commodity_channel_index(db, period=31):
        typ_price = (db['High'] + db['Low'] + db['Close']) / 3
        return (typ_price - typ_price.rolling(period).mean()) / (0.015 * typ_price.rolling(period).std())

    @staticmethod
    def moving_average_convergence_divergence(db, win_len_sig=9, s_period=12, l_period=26):
        close = db['Adj Close']

        ema_sh = close.ewm(span=s_period, adjust=False).mean()
        ema_lg = close.ewm(span=l_period, adjust=False).mean()
        _macd = ema_sh - ema_lg
        ema_sig = _macd.ewm(span=win_len_sig, adjust=False).mean()
        return _macd - ema_sig

    # The threshold will need to be between 0 <=> days_spanning
    @staticmethod
    def power_x_strategy(db, stoch_per=50, rsi_per=50, macd_val=0, marker=StrategyPage.DIRECTIONS[0], days_spanning=2):
        macd = StockCalculations.moving_average_convergence_divergence(db, win_len_sig=9, s_period=12, l_period=26)
        rsi = StockCalculations.relative_strength_index(db, win_len=7)
        stochastic = StockCalculations.stochastic_oscillator(db, win_len=14, period=3)

        # This will set all the values to true or false based on the markers
        macd.fillna(value=False, inplace=True)
        macd = macd.where(macd <= macd_val, other=True)
        macd = macd.where(macd > macd_val, other=False)

        rsi.fillna(value=False, inplace=True)
        rsi = rsi.where(rsi > rsi_per, other=False)
        rsi = rsi.where(rsi <= rsi_per, other=True)

        stochastic.fillna(value=False, inplace=True)
        stochastic = stochastic.where(stochastic > stoch_per, other=False)
        stochastic = stochastic.where(stochastic <= stoch_per, other=True)

        if marker == StrategyPage.DIRECTIONS[1]:
            macd = ~macd.astype(bool)
            rsi = ~rsi.astype(bool)
            stochastic = ~stochastic.astype(bool)

        trigger = macd * rsi * stochastic
        if days_spanning <= 0:
            days_spanning = 1
        trig_sum = trigger[trigger == 1].iloc[-days_spanning:].sum()
        return list(trig_sum[trig_sum >= days_spanning].index)

    @staticmethod
    def option_alpha_strategy(db, cci_per=0, rsi_per=50, macd_val=0,
                              marker=StrategyPage.DIRECTIONS[0], days_spanning=2):
        macd = StockCalculations.moving_average_convergence_divergence(db, win_len_sig=9, s_period=15, l_period=30)
        rsi = StockCalculations.relative_strength_index(db, win_len=14)
        cci = StockCalculations.commodity_channel_index(db, period=31)

        # This will set all the values to true or false based on the markers
        macd.fillna(value=False, inplace=True)
        macd = macd.where(macd <= macd_val, other=True)
        macd = macd.where(macd > macd_val, other=False)

        rsi.fillna(value=False, inplace=True)
        rsi = rsi.where(rsi > rsi_per, other=False)
        rsi = rsi.where(rsi <= rsi_per, other=True)

        cci.fillna(value=False, inplace=True)
        cci = cci.where(cci > cci_per, other=False)
        cci = cci.where(cci <= cci_per, other=True)

        if marker == StrategyPage.DIRECTIONS[1]:
            macd = ~macd.astype(bool)
            rsi = ~rsi.astype(bool)
            cci = ~cci.astype(bool)

        trigger = macd * rsi * cci
        if days_spanning <= 0:
            days_spanning = 1
        trig_sum = trigger[trigger == 1].iloc[-days_spanning:].sum()
        return list(trig_sum[trig_sum >= days_spanning].index)


if __name__ == '__main__':
    app = StockStrategiesScanner()
    # app.geometry("1024x480")
    app.geometry("960x480")
    # in order to add an icon to the program
    # logo = PhotoImage(file='jb_stock.png')
    # app.tk.call('wm', 'iconphoto', tk.Tk._w, logo)
    app.mainloop()
