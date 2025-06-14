import tkinter as tk
from async_parser import main_async
from sync_parser import main_sync
import sqlite3
from tkinter import ttk

class AppMiShopPareser:
    def __init__(self):
        self.conn = sqlite3.connect("bd.db")
        self.cursor = self.conn.cursor()
        self.root = self.create_root()
        self.search_var = tk.StringVar()
    
    def create_root(self):
        root = tk.Tk()
        root.title("Парсер mi-shop.com")
        root.geometry("1250x700")
        return root

    def base_frame(self):
        frame_base = tk.Frame(self.root)
        frame_base.grid(row=2, column=1, columnspan=2, pady=5, sticky="nsew")

        tk.Button(frame_base, text="Асинхронный парсер", command=main_async).grid(row=0, column=0, padx=5)
        tk.Button(frame_base, text="Синхронный парсер", command=main_sync).grid(row=0, column=1, padx=5)

        frame_base.grid_columnconfigure(2, weight=1)  # Растяжка
        tk.Button(frame_base, text="Обновить данные", command=self.show_data).grid(row=0, column=3, padx=5, sticky="e")

    def create_table(self):
        frame_top = tk.Frame(self.root, bg="lightgrey", height=200)
        frame_top.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")

        frame_bottom = tk.Frame(self.root,bg="white", height=200)
        frame_bottom.grid(row=6, column=0, columnspan=3, pady=10, sticky="nsew")

        label = tk.Label(frame_top, text="Записи")
        label.pack()

        label = tk.Label(frame_bottom, text="Продукты",bg="white")
        label.pack() 

        columns = ("Name", "Price", "Article", "Color", "entry_id", "spec_id")
        products = ttk.Treeview(frame_bottom, columns=columns, show="headings")
        products.heading("Name", text="Название")
        products.heading("Price", text="Цена")
        products.heading("Article", text="Артикль")
        products.heading("Color", text="Цвет")
        #products.heading("Image", text="Изображение")
        products.heading("entry_id", text="ID записи")
        products.heading("spec_id", text="ID продукта")
        products.pack(padx=20)

        stats = ttk.Treeview(frame_top, columns=("Date", "Count", "entryID"), show="headings")
        stats.heading("Date", text="Дата")
        stats.heading("Count", text="Количество")
        stats.heading("entryID", text="ID записи")
        stats.pack()
        stats.bind("<<TreeviewSelect>>", self.on_stats_select)
        return stats, products

    def on_stats_select(self, event):
        selected_item = self.stats.focus()
        if not selected_item:
            return 
        
        entry_id = self.stats.item(selected_item)["values"][2]

        for i in self.products.get_children():
            self.products.delete(i)

        self.cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id=?", (entry_id,))

        for row in self.cursor.fetchall():
            self.products.insert("", "end", values=row)

    def build_search(self):
        frame = tk.Frame(self.root, bg="#ffffff")
        frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="s")

        entry = tk.Entry(frame, textvariable=self.search_var, width=30)
        entry.grid(row=0, column=0, padx=5)

        tk.Button(frame, text="Поиск", command=self.search_tree).grid(row=0, column=1, padx=5)




    def search_tree(self):
        query = self.search_var.get().strip()
        if not query:
            return

        for i in self.products.get_children():
            self.products.delete(i)

        selected_item = self.stats.focus()
        like_query = f"%{query}%"
        sql = """
        SELECT name, price, article, color, entry_id, spec_id 
        FROM Products 
        WHERE 
            name LIKE ? OR 
            article LIKE ? OR 
            color LIKE ? OR 
            CAST(price AS TEXT) LIKE ? OR
            CAST(entry_id AS TEXT) LIKE ? OR
            CAST(spec_id AS TEXT) LIKE ?
        """
        params = (like_query,) * 6

        if selected_item:
            item_data = self.stats.item(selected_item)["values"]
            if len(item_data) >= 3:
                entry_id = item_data[2]
                sql = f"SELECT * FROM ({sql}) AS sub WHERE entry_id = ?"
                params += (entry_id,)

        self.cursor.execute(sql, params)
        for row in self.cursor.fetchall():
            self.products.insert('', 'end', values=row)


    def show_data(self):
        for item in self.stats.get_children():
            self.stats.delete(item)
        for item in self.products.get_children():
            self.products.delete(item)
        
        self.cursor.execute("SELECT date, product_count, entry_id FROM category_stats")
        for row in self.cursor.fetchall():
            self.stats.insert('', 'end', values=row)


        self.cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products")
        for row in self.cursor.fetchall():
            self.products.insert('', 'end', values=row)


    def run(self):
        self.base_frame()
        self.stats, self.products = self.create_table()
        self.build_search()
        self.show_data()
        self.root.mainloop()
        
