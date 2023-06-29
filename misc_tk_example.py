import os
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
from database import FrontierTables, FrontierDatabase
from tables import available_tools

LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

IMG_LOC = os.path.join(os.getcwd(), 'images')
IMG_WIDTH = 250
WIN_SIZE = '640x500'
PADDING = 2


def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title('!')
    label = ttk.Label(popup, text=msg, font=NORM_FONT)
    label.pack(side='top', fill='x', pady=10)
    b1 = ttk.Button(popup, text='Okay', command=popup.destroy)
    b1.pack()
    popup.mainloop()


# [tools_table, assy_table, rcb_table, setting_dog_sub_table, tbr_table, landing_collar_table, hyd_rt_table]
class FrontierTechSheet(tk.Tk):

    def __init__(self, db, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.db = db

        # Set the title for the window
        tk.Tk.wm_title(self, 'Frontier Tech Sheets')

        # This is the main window frame. Everything will be contained here.
        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Add a menubar
        menubar = tk.Menu(container)
        # Create the file menu
        # tkinter will open the menu bars in new windows unless specifying below, that is why "tearoff=False"
        filemenu = tk.Menu(menubar, tearoff=False, activebackground='#BFBFB7')
        filemenu.add_command(label='New', command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label='Open...', command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label='Save...', command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_command(label='Save to PDF', command=lambda: popupmsg('Not supported just yet!'))
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=quit)
        # Adds the 'File' and cascade to the menubar.
        menubar.add_cascade(label='File', menu=filemenu)

        # Add the menubar to the window
        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        self.available_frames = [StartPage, RCB, SettingDogSub, TBR, LandingCollar, HydRTGen2, ]

        for F in self.available_frames:
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def show_tool(self, cont):
        tool_dict = cont.get_dict_values()
        if tool_dict['toolbox'] == '' or tool_dict['assembly'] == '' or tool_dict['desc'] == '':
            popupmsg('Missing values')
            return

        val_loc = available_tools.index(tool_dict['toolbox'])
        self.show_frame(self.available_frames[val_loc])
        if val_loc == 1:
            self.frames[self.available_frames[val_loc]].f_table = FrontierTables(self.db, FrontierTables.RCB)
            self.frames[self.available_frames[val_loc]].update_img()
        elif val_loc == 2:
            self.frames[self.available_frames[val_loc]].f_table = FrontierTables(self.db,
                                                                                 FrontierTables.SETTING_DOG_SUB)
            self.frames[self.available_frames[val_loc]].update_img()
        elif val_loc == 3:
            self.frames[self.available_frames[val_loc]].f_table = FrontierTables(self.db, FrontierTables.TBR)
            self.frames[self.available_frames[val_loc]].update_img()
        elif val_loc == 4:
            self.frames[self.available_frames[val_loc]].f_table = FrontierTables(self.db, FrontierTables.LANDING_COLLAR)
            self.frames[self.available_frames[val_loc]].update_img()
        elif val_loc == 5:
            self.frames[self.available_frames[val_loc]].f_table = FrontierTables(self.db, FrontierTables.HYD_RT)
            self.frames[self.available_frames[val_loc]].update_img()
        self.frames[self.available_frames[val_loc]].set_tool_dict(tool_dict)


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text=(
            """
            This program is used for the creation 
            of Tech Data Sheets for Frontier Oil Tools.

            All Fields with '*' are required.
            Please double check all values entered.
            """), font=LARGE_FONT, fg='red').pack(pady=10, padx=10)

        tool_info = tk.LabelFrame(self, text='Tool Information')
        tool_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ************ Row 0 ****************
        # ========= set up the tool selection =========
        tk.Label(tool_info, text='Tool Selection*:', justify='center').grid(row=0, sticky=tk.NE, pady=PADDING)
        self.toolbox_str = tk.StringVar()
        ttk.Combobox(tool_info, textvariable=self.toolbox_str, values=available_tools).grid(row=0, column=1,
                                                                                            sticky='nsew', pady=PADDING)

        # ************ Row 1 ****************
        # ========= Name of the current tool =========
        tk.Label(tool_info, text='Assembly Number*:').grid(row=1, sticky=tk.NE, pady=PADDING)
        self.assy_number = tk.StringVar()
        tk.Entry(tool_info, textvariable=self.assy_number).grid(row=1, column=1, columnspan=2, sticky=tk.NSEW,
                                                                pady=PADDING)

        # ************ Row 2 ****************
        # ========= Model of tool =========
        tk.Label(tool_info, text='Model Number:').grid(row=2, sticky=tk.NE, pady=PADDING)
        self.model = tk.StringVar()
        tk.Entry(tool_info, textvariable=self.model).grid(row=2, column=1, sticky=tk.NSEW, pady=PADDING)

        # ************ Row 3 ****************
        # ========= Material Grade of tool =========
        tk.Label(tool_info, text='Material Grade:').grid(row=3, sticky=tk.NE, pady=PADDING)
        self.material = tk.StringVar()
        tk.Entry(tool_info, textvariable=self.material).grid(row=3, column=1, sticky=tk.NSEW, pady=PADDING)

        # ************ Row 4 ****************
        # ========= Connection of tool =========
        tk.Label(tool_info, text='Connection:').grid(row=4, sticky=tk.NE, pady=PADDING)
        self.connection = tk.StringVar()
        tk.Entry(tool_info, textvariable=self.connection).grid(row=4, column=1, columnspan=3, sticky=tk.NSEW,
                                                               pady=PADDING)
        tk.Label(tool_info, text='(i.e. 5.00 18.0# VAM TOP PIN Down)').grid(row=4, column=4,
                                                                            sticky=tk.NSEW, pady=PADDING)

        # ************ Row 5 ****************
        # ========= Description of tool =========
        tk.Label(tool_info, text='Tool Description*:').grid(row=5, sticky=tk.NE, pady=PADDING)
        self.tool_desc = tk.StringVar()
        tk.Entry(tool_info, textvariable=self.tool_desc).grid(row=5, column=1, columnspan=5, sticky=tk.NSEW,
                                                              pady=PADDING)

        # Pack in buttons to open the desired information
        ttk.Button(self, text='Cancel', command=quit).pack(side=tk.RIGHT, padx=PADDING, pady=PADDING)
        # Open the desired tool
        ttk.Button(self, text='Open',
                   command=lambda: controller.show_tool(self)).pack(side=tk.RIGHT, padx=PADDING, pady=PADDING)

    def get_dict_values(self):
        return {'toolbox': self.toolbox_str.get(), 'assembly': self.assy_number.get(), 'model': self.model.get(),
                'material': self.material.get(), 'connection': self.connection.get(), 'desc': self.tool_desc.get()}


class BaseTool(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.f_table = None

        self.tool_info = tk.LabelFrame(self, text='Tool Information')
        self.tool_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        tk.Label(self.tool_info, text='Tool Selection:', justify='center').grid(row=0, sticky=tk.NE, pady=PADDING)
        tk.Label(self.tool_info, text='Assembly Number:').grid(row=0, column=3, sticky=tk.NE, pady=PADDING)
        tk.Label(self.tool_info, text='Tool Description:').grid(row=1, sticky=tk.NE, pady=PADDING)

        btn_save = ttk.Button(self, text='Save', command=self.save)
        btn_save.pack(side=tk.BOTTOM, anchor=tk.SE)

        self.nb = ttk.Notebook(self)
        self.nb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=PADDING, pady=PADDING)
        self.prop_tab = ttk.Frame(self.nb)
        self.nb.add(self.prop_tab, text='Mechanical Properties')
        self.dim_tab = ttk.Frame(self.nb)
        self.nb.add(self.dim_tab, text='Dimensions')

    def update_img(self):
        if self.f_table.tool_exists():
            pic_frame = tk.Frame(self, relief=tk.SUNKEN)
            pic_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=2, pady=5)

            image = Image.open(self.f_table.img)
            if image.width > IMG_WIDTH:
                image = image.resize((IMG_WIDTH, image.height), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image)

            # need to store an extra image of this. Otherwise garbage collection will remove the file
            label = tk.Label(pic_frame, image=img, relief=tk.RAISED)
            label.image = img
            label.pack()
        else:
            popupmsg("Can't find image")

    def set_tool_dict(self, loc_dict):
        tk.Label(self.tool_info, text=loc_dict['toolbox'], justify='center').grid(row=0, column=1,
                                                                                  sticky=tk.NE, pady=PADDING, padx=20)
        tk.Label(self.tool_info, text=loc_dict['assembly']).grid(row=0, column=4, sticky=tk.NE, pady=PADDING)
        tk.Label(self.tool_info, text=loc_dict['desc']).grid(row=1, column=1, columnspan=4, sticky=tk.NW, pady=PADDING)

    def save(self):
        print('saving')


class RCB(BaseTool):

    def __init__(self, parent, controller):
        super(RCB, self).__init__(parent, controller)

        tk.Label(self.dim_tab, text='This is "A":').grid(row=0, column=0, sticky=tk.NE)
        self.dim_a_val = tk.DoubleVar()
        dim_a = ttk.Entry(self.dim_tab, textvariable=self.dim_a_val)
        dim_a.grid(row=0, column=1, sticky=tk.NW)
        ttk.Label(self.dim_tab, text='in').grid(row=0, column=2, sticky=tk.NSEW)


class SettingDogSub(BaseTool):

    def __init__(self, parent, controller):
        super(SettingDogSub, self).__init__(parent, controller)


class TBR(BaseTool):

    def __init__(self, parent, controller):
        super(TBR, self).__init__(parent, controller)


class LandingCollar(BaseTool):

    def __init__(self, parent, controller):
        super(LandingCollar, self).__init__(parent, controller)


class HydRTGen2(BaseTool):

    def __init__(self, parent, controller):
        super(HydRTGen2, self).__init__(parent, controller)


def store_imgs_db(db):
    print('updating db images')
    locations = ['retrievable_cement_bushing_dim_bubbles_gen2.PNG', 'rotating_dog_assembly_dim_gen2.PNG', 'tbr_dim.PNG',
                 'landing_collar_dims.png', 'hydraulic_running_tool_dims_gen2.PNG']
    tbl_types = [FrontierTables.RCB, FrontierTables.SETTING_DOG_SUB, FrontierTables.TBR, FrontierTables.LANDING_COLLAR,
                 FrontierTables.HYD_RT]

    for loc, tbl_type in zip(locations, tbl_types):
        tbl = FrontierTables(db, tbl_type)
        tbl.tools_table(os.path.join(IMG_LOC, loc))


def main(db_loc, img=False):
    db = FrontierDatabase(db_loc=db_loc, master=True)
    if img:
        store_imgs_db(db)

    app = FrontierTechSheet(db)
    app.geometry(WIN_SIZE)
    app.mainloop()


if __name__ == '__main__':
    database_location = os.path.join(os.getcwd(), 'database', 'frontier_database.db')
    # print(os.listdir(img_path))
    main(database_location)
    # main(database_location, True)
