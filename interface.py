from tkinter import ttk, simpledialog as sd, messagebox as mb
from ttkwidgets import Table
import tkinter as tk
from db import db
from logger import logger


class AppTable(Table):
    def __init__(self, root, columns=('Receipt Number', 'Item Number', 'BBD', 'DEX_ROW_ID')):
        super().__init__(show='headings', columns=columns, drag_cols=False, drag_rows=False, sortable=True)
        self.root = root
        self.columns = columns
        self.__populate_columns()
        self.__add_scrollbars()
        self.__add_context_menu()
        self.bind("<Button-3>", self.popup)

    def __populate_columns(self):
        for col in self.columns:
            if col == 'DEX_ROW_ID':
                type_ = int
            else:
                type_ = str
            self.heading(col, text=col, anchor="w")
            self.column(col, width=150, stretch=False, type=type_)

    def clear_table(self):
        self.delete(*self.get_children())

    def __add_scrollbars(self):
        self.sx = ttk.Scrollbar(self.root, orient='horizontal', command=self.xview)
        self.sy = ttk.Scrollbar(self.root, orient='vertical', command=self.yview)
        self.configure(yscrollcommand=self.sy.set, xscrollcommand=self.sx.set)

    def __add_context_menu(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Edit BBD",
                                    command=self.edit_selected)

    def edit_selected(self):
        item = self.item(self.selection())
        new_value = sd.askstring(parent=None,
                                 title="New BBD Value",
                                 prompt="Enter new BBD value",
                                 initialvalue=item['values'][2].strip())
        if new_value:
            db.change_bbd(new_value, item['values'][3])
            self.root.query_data()

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.__configure_gui()
        self.__add_variables()
        self.__define_styles()
        self.add_widgets()

    def __configure_gui(self):
        self.paddings = {'padx': 5,
                         'pady': 5,
                         }
        self.minsize(630, 300)
        self.resizable(False, False)
        self.title("BBD Changer")
        self.iconbitmap('source\\Dynamics-Waves.ico')
        self.columnconfigure(2, weight=1)
        self.rowconfigure(2, weight=1)

    def __add_variables(self):
        self.receipt = tk.StringVar()
        self.item = tk.StringVar()

    def __define_styles(self):
        self.style = ttk.Style(self)
        self.call('source', 'source\\forest-dark.tcl')
        self.style.theme_use('forest-dark')

        self.button_style = ttk.Style(self)
        self.button_style.configure('TButton', font=('Helvetica', 14))

        self.label_style = ttk.Style(self)
        self.label_style.configure('TLabel', font=('Verdana', 12))

    def add_widgets(self):
        self.receipt_label = ttk.Label(self, text="Receipt Number")
        self.receipt_label.grid(column=0, row=0, sticky=tk.W, **self.paddings)
        self.receipt_entry = ttk.Entry(self, textvariable=self.receipt)
        self.receipt_entry.grid(column=1, row=0, sticky=tk.EW, **self.paddings)

        self.item_label = ttk.Label(self, text="Item Number")
        self.item_label.grid(column=0, row=1, sticky=tk.W, **self.paddings)
        self.item_entry = ttk.Entry(self, textvariable=self.item)
        self.item_entry.grid(column=1, row=1, sticky=tk.EW, **self.paddings)

        self.app_table = AppTable(self)
        self.app_table.grid(column=0, row=2, sticky='enws', columnspan=5, padx=(5, 0))
        self.app_table.sx.grid(column=0, row=3, sticky='ew', columnspan=5, padx=(5, 0))
        self.app_table.sy.grid(column=5, row=2, sticky='ns')

        self.query_button = ttk.Button(self, text="Query", command=self.query_data)
        self.query_button.grid(column=3, row=4, sticky=tk.E, **self.paddings)

        self.clear_button = ttk.Button(self, text="Clear", command=self.clear)
        self.clear_button.grid(column=4, row=4, sticky=tk.E, **self.paddings)

    def insert_into_table(self, values):
        self.app_table.insert('', 'end', iid=values[0], values=values[1:])

    def clear(self):
        self.__clear_entries()
        self.app_table.clear_table()

    def __clear_entries(self):
        self.receipt.set("")
        self.item.set("")

    def query_data(self):
        if not any((self.receipt.get(), self.item.get())):
            mb.showwarning(title="Error",
                           message="Leaving Receipt Number or Item Number blank will read millions of rows.\n"
                                   "Please specify either of those.")
            return
        df = db.get_bbd(self.receipt.get(), self.item.get())
        self.app_table.clear_table()
        try:
            for row in df.itertuples():
                self.insert_into_table(row)
        except BaseException as e:
            logger.log_info(e)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    # RCT070342
