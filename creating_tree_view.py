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

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Helvetica", 10)
PADDING = 2

PANEL_SELECTION = [1, 2, 3, 4, 5]

SELECTED_STOCK = 'HOLX'


def pop_up_msg(msg):
    popup = tk.Tk()
    popup.wm_title('!')
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    button1 = ttk.Button(popup, text='Okay', command=popup.destroy)
    button1.pack()
    popup.mainloop()


# this is inheriting from tk.Tk
class BasicPage(tk.Tk):
    # args are typical parameters and kwargs are dictionaries
    def __init__(self, *args, **kwargs):
        # initialize inherited class
        tk.Tk.__init__(self, *args, **kwargs)

        # in order to add an icon to the program
        # tk.Tk.iconbitmap(self, default='clienticon.ico')
        tk.Tk.wm_title(self, 'Power X Strategy')

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
        self.available_frames = [FirstPage]

        for F in self.available_frames:
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(FirstPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        # bring the frame to the top for the user to see
        frame.tkraise()

    def show_stock_info(self, cont, stock):
        self.frames[cont].set_stock(stock)
        self.show_frame(cont)


class FirstPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.stock = ''
        self.stock_info = ''

        ttk.Label(self, text='HOLX', justify='center', anchor=tk.CENTER).pack(side=tk.TOP, fill=tk.X)

        chart_frame = tk.LabelFrame(self, text="Chart Criteria")
        chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        options_frame = tk.LabelFrame(self, text="Options Chain")
        options_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)

        # -----------------------------------------------------------
        # ----------------------- Chart Frame -----------------------
        # -----------------------------------------------------------
        this_row = 0
        ttk.Label(chart_frame, text='Indicator:',
                  font="Verdana 12 underline").grid(row=this_row, sticky=tk.NSEW)
        ttk.Label(chart_frame, text='Chart Loc:',
                  font="Verdana 12 underline").grid(row=this_row, column=2, sticky=tk.NSEW)
        # ========= Set up the Headings =========
        this_row = 1
        # ========= Set up the EMA Short =========
        self.ema_sh_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='EMA Short', variable=self.ema_sh_int).grid(row=this_row, sticky=tk.NSEW)
        self.ema_sh_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='ema_sh_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.ema_sh_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        this_row = 2
        # ========= Set up the EMA Long =========
        self.ema_lg_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='EMA Long', variable=self.ema_lg_int).grid(row=this_row, sticky=tk.NSEW)
        self.ema_lg_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='ema_lg_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.ema_lg_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        this_row = 3
        # ========= Set up the RSI =========
        self.rsi_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='RSI', variable=self.rsi_int).grid(row=this_row, sticky=tk.NSEW)
        self.rsi_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='rsi_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.rsi_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        this_row = 4
        # ========= Set up the Stochastic =========
        self.stochastic_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='Stochastic', variable=self.stochastic_int).grid(row=this_row, sticky=tk.NSEW)
        self.stochastic_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='stochastic_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.stochastic_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        this_row = 5
        # ========= Set up the MACD =========
        self.macd_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='MACD', variable=self.macd_int).grid(row=this_row, sticky=tk.NSEW)
        self.macd_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='macd_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.macd_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        this_row = 6
        # ========= Set up the CCI =========
        self.cci_int = tk.IntVar()
        ttk.Checkbutton(chart_frame, text='CCI', variable=self.cci_int).grid(row=this_row, sticky=tk.NSEW)
        self.cci_pan_str = tk.StringVar(self, value=PANEL_SELECTION[0], name='cci_pan_str')
        ttk.Combobox(chart_frame, textvariable=self.cci_pan_str,
                     values=PANEL_SELECTION).grid(row=this_row, column=2, sticky='nsew', pady=PADDING)

        # ========= Set up the Separator =========
        ttk.Separator(chart_frame, orient=tk.VERTICAL).grid(row=1, rowspan=6, column=9, sticky=tk.NS,
                                                            pady=PADDING, padx=10)

        # ========= Set up the Show Chart Button =========
        ttk.Button(chart_frame, text='Show Chart',
                   command=lambda: pop_up_msg('Not set up yet')).grid(row=1, rowspan=6, column=10,
                                                                      sticky=tk.NSEW, pady=PADDING)

        # -------------------------------------------------------------
        # ----------------------- Options Frame -----------------------
        # -------------------------------------------------------------
        ttk.Button(options_frame, text='CALL',
                   command=lambda: self.set_stock(SELECTED_STOCK, 'CALL')).grid(row=0, column=0, columnspan=6,
                                                                                sticky=tk.NSEW, pady=PADDING)
        ttk.Separator(options_frame, orient=tk.VERTICAL).grid(row=0, column=6, sticky=tk.NS, pady=PADDING)
        ttk.Button(options_frame, text='PUT',
                   command=lambda: self.set_stock(SELECTED_STOCK, 'PUT')).grid(row=0, column=7, columnspan=6,
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

    def set_stock(self, stock, call_put):
        self.stock = stock
        self.stock_info = yf.Ticker(stock)
        self.add_options(call_put=call_put)

    def add_options(self, call_put):
        self.tree.delete(*self.tree.get_children())
        for opt in self.stock_info.options:
            self.tree.insert('', index='end', iid=opt, text=opt, values=(opt, '', '', '', '', '', '', ''))
            option_chain = self.stock_info.option_chain(opt)
            # TODO need to add a way to change whether you want to see puts or calls
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
                self.tree.insert(opt, index='end', text='strike', tags=(tag, ),
                                 values=('', option['openInterest'].iloc[index], option['volume'].iloc[index],
                                         f"{option['impliedVolatility'].iloc[index]:.3f}",
                                         option['lastPrice'].iloc[index], option['bid'].iloc[index],
                                         option['ask'].iloc[index], option['strike'].iloc[index]))
        self.tree.tag_configure('itm', background='green')
        self.tree.tag_configure('otm', background='blue')


if __name__ == '__main__':
    app = BasicPage()
    # app.geometry("1024x480")
    app.geometry("960x480")
    app.mainloop()
