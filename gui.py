import tkinter as tk
from async_parser import main_async
from sync_parser import main_sync
import sqlite3
from tkinter import ttk
from PIL import Image, ImageTk
import io  # Для работы с бинарными данными

class AppMiShopPareser:
    def __init__(self):
        self.conn = sqlite3.connect("bd.db")
        self.cursor = self.conn.cursor()
        self.root = self.create_root()
        self.search_var = tk.StringVar()

        # Стилизация таблиц
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"),
                        background="#ff6900", foreground="white")
        style.configure("Treeview", font=("Arial", 10), rowheight=25,
                        fieldbackground="white", background="white")

    def create_root(self):
        root = tk.Tk()
        root.title("Парсер mi-shop.com audio")
        root.geometry("1250x850")
        root.configure(bg="#f7f7f7")  # Светлый фон в стиле Xiaomi
        return root

    def base_frame(self):
        frame_base = tk.Frame(self.root, bg="#f7f7f7")
        frame_base.grid(row=2, column=1, columnspan=2, pady=5, sticky="nsew")

        tk.Button(frame_base, text="Асинхронный парсер", command=main_async,
                  bg="#ff6900", fg="white", padx=10).grid(row=0, column=0, padx=5)
        tk.Button(frame_base, text="Синхронный парсер", command=main_sync,
                  bg="#ff6900", fg="white", padx=10).grid(row=0, column=1, padx=5)

        frame_base.grid_columnconfigure(2, weight=1)
        tk.Button(frame_base, text="Обновить данные", command=self.show_data,
                  bg="#ff6900", fg="white", padx=10).grid(row=0, column=3, padx=5, sticky="e")

    def create_table(self):
        frame_top = tk.LabelFrame(self.root, text="📊 Статистика", bg="#ffffff", padx=10, pady=5)
        frame_top.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="nsew")

        frame_bottom = tk.LabelFrame(self.root, text="🛒 Продукты", bg="#ffffff", padx=10, pady=5)
        frame_bottom.grid(row=6, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

        label = tk.Label(frame_top, text="Записи", bg="#ffffff", fg="#333333")
        label.pack()

        label = tk.Label(frame_bottom, text="Продукты", bg="#ffffff", fg="#333333")
        label.pack()

        columns = ("Name", "Price", "Article", "Color", "entry_id", "spec_id")
        products = ttk.Treeview(frame_bottom, columns=columns, show="headings", selectmode="browse")
        products.heading("Name", text="Название")
        products.heading("Price", text="Цена")
        products.heading("Article", text="Артикль")
        products.heading("Color", text="Цвет")
        products.heading("entry_id", text="ID записи")
        products.heading("spec_id", text="ID продукта")
        products.pack(fill="both", expand=True)
        products.bind("<<TreeviewSelect>>", self.create_image)

        stats = ttk.Treeview(frame_top, columns=("Date", "Count", "entryID"), show="headings", selectmode="browse")
        stats.heading("Date", text="Дата")
        stats.heading("Count", text="Количество")
        stats.heading("entryID", text="ID записи")
        stats.pack(fill="both", expand=True)
        stats.bind("<<TreeviewSelect>>", self.on_stats_select)

        return stats, products

    def create_image(self, event):
        frame_image = tk.Frame(self.root, bg="#f2f2f2", padx=10, pady=10)
        frame_image.grid(row=4, column=2, columnspan=2, sticky="nsew")

        selected_it = self.products.focus()
        if not selected_it:
            return

        spec_id = self.products.item(selected_it)["values"][5]

        result = self.cursor.execute("SELECT image FROM Products WHERE spec_id=?", (spec_id,))
        blob_data = self.cursor.fetchone()[0]
        image = Image.open(io.BytesIO(blob_data))

        image = image.resize((240, 200), Image.LANCZOS)
        image = ImageTk.PhotoImage(image)

        label = tk.Label(frame_image, image=image, bg="#f2f2f2")
        label.image = image
        label.pack()

    def on_stats_select(self, event):
        selected_item = self.stats.focus()
        if not selected_item:
            return

        entry_id = self.stats.item(selected_item)["values"][2]

        for i in self.products.get_children():
            self.products.delete(i)

        self.cursor.execute(
            "SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id=?", (entry_id,))
        for row in self.cursor.fetchall():
            self.products.insert("", "end", values=row)

    def build_search(self):
        frame = tk.Frame(self.root, bg="#f7f7f7")
        frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        entry = tk.Entry(frame, textvariable=self.search_var, width=40, font=("Arial", 11))
        entry.grid(row=0, column=0, padx=5)

        tk.Button(frame, text="🔍 Поиск", command=self.search_tree,
                  bg="#ff6900", fg="white").grid(row=0, column=1, padx=5)

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

if __name__ == "__main__":
    AppMiShopPareser().run()
