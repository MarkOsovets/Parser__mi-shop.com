import tkinter as tk
from main import pars_async, pars_sync
import sqlite3
from tkinter import ttk
from PIL import Image, ImageTk
import io


BG_COLOR = "#ffffff"       # Белый 
FG_COLOR = "#000000"       # Чёрный текст
ACCENT_COLOR = "#ff6700" #оранжевый

# База данных 
conn = sqlite3.connect("bd.db")
cursor = conn.cursor()

selected_entry_id = None    

# Функции отображения 
def show_data():
    # Очистка таблиц
    for item in tree_stats.get_children():
        tree_stats.delete(item)
    for item in tree_products.get_children():
        tree_products.delete(item)

    # Загрузка статистики
    cursor.execute("SELECT date, product_count, entry_id FROM category_stats")
    for row in cursor.fetchall():
        tree_stats.insert('', 'end', values=row)

    # Загрузка продуктов
    cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products")
    for row in cursor.fetchall():
        tree_products.insert('', 'end', values=row)


# Фильтрация 
def filter_data(date_str, price_str):
    for item in tree_stats.get_children():
        tree_stats.delete(item)
    for item in tree_products.get_children():
        tree_products.delete(item)

    query = "SELECT date, product_count, entry_id FROM category_stats WHERE 1=1"
    params = []

    if date_str:
        query += " AND date = ?"
        params.append(date_str)

    if selected_entry_id is not None:
        query += " AND entry_id = ?"
        params.append(selected_entry_id)

    cursor.execute(query, params)
    stats = cursor.fetchall()

    product_ids = set()
    for row in stats:
        tree_stats.insert('', 'end', values=row)
        product_ids.add(row[2])

    if product_ids:
        price_filter = ""
        price_param = []
        if price_str:
            price_filter = " AND price <= ?"
            price_param = [price_str]

        for pid in product_ids:
            cursor.execute(
                f"SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id = ? {price_filter}",
                [pid] + price_param
            )
            for prod in cursor.fetchall():
                tree_products.insert('', 'end', values=prod)


# Поиск 
def search_tree():
    query = search_var.get().strip()
    if not query:
        return

    for item in tree_products.get_children():
        tree_products.delete(item)

    like_query = f"%{query}%"

    sql= """
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

    if selected_entry_id is not None:
        sql = f"SELECT * FROM ({sql}) AS sub WHERE entry_id = ?"
        params += (selected_entry_id,)

    cursor.execute(sql, params)
    results = cursor.fetchall()

    for row in results:
        tree_products.insert('', 'end', values=row)
    
    if not results:
        print("Ничего не найдено.")


# Сортировка 
def sort_products():
    for item in tree_products.get_children():
        tree_products.delete(item)

    sort_option = sort_var.get()

    if sort_option == "Цена ↑":
        if selected_entry_id is not None:
            cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id = ? ORDER BY price ASC", (selected_entry_id,))
        else:
            cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products ORDER BY price ASC")

    elif sort_option == "Цена ↓":
        if selected_entry_id is not None:
            cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id = ? ORDER BY price DESC", (selected_entry_id,))
        else:
            cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products ORDER BY price DESC")

    elif sort_option == "Дата ↑":
        if selected_entry_id is not None:
            cursor.execute("""
                SELECT p.name, p.price, p.article, p.color, p.entry_id, p.spec_id 
                FROM Products p
                JOIN category_stats cs ON p.entry_id = cs.entry_id
                WHERE p.entry_id = ?
                ORDER BY cs.date ASC
            """, (selected_entry_id,))
        else:
            cursor.execute("""
                SELECT p.name, p.price, p.article, p.color, p.entry_id, p.spec_id 
                FROM Products p
                JOIN category_stats cs ON p.entry_id = cs.entry_id
                ORDER BY cs.date ASC
            """)

    elif sort_option == "Дата ↓":
        if selected_entry_id is not None:
            cursor.execute("""
                SELECT p.name, p.price, p.article, p.color, p.entry_id, p.spec_id 
                FROM Products p
                JOIN category_stats cs ON p.entry_id = cs.entry_id
                WHERE p.entry_id = ?
                ORDER BY cs.date DESC
            """, (selected_entry_id,))
        else:
            cursor.execute("""
                SELECT p.name, p.price, p.article, p.color, p.entry_id, p.spec_id 
                FROM Products p
                JOIN category_stats cs ON p.entry_id = cs.entry_id
                ORDER BY cs.date DESC
            """)

    else:
        return

    for row in cursor.fetchall():
        tree_products.insert('', 'end', values=row)


# Показ изображения 
def show_image(spec_id):
    cursor.execute("SELECT image FROM Products WHERE spec_id = ?", (spec_id,))
    result = cursor.fetchone()

    if result and result[0]:
        image_data = result[0]
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((200, 200))
        photo = ImageTk.PhotoImage(image)
        image_label.configure(image=photo, text="")
        image_label.image = photo
    else:
        image_label.configure(image='', text="Нет изображения")


# !Tkinter GUI 

# Главное окно
root = tk.Tk()
root.title("Парсер mi-shop.com")
root.geometry("1250x700")
root.configure(bg=BG_COLOR)



# Верхние кнопки 
button_frame = tk.Frame(root)
button_frame.grid(row=0, column=0, columnspan=3, pady=20)

tk.Button(button_frame, text="Асинхронный парсер", command=pars_async).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Синхронный парсер", command=pars_sync).grid(row=0, column=1, padx=5)
tk.Button(text="Показать данные", command=show_data).grid(row=0, column=2, padx=5)


# Отображение изображения товара 
image_frame = tk.Frame(root)
image_frame.grid(row=1, column=2, rowspan=3, padx=10, pady=10, stic='ne')

image_label = tk.Label(image_frame, text="Изображение товара будет здесь")
image_label.pack()


# Сортировка и поиск
sort_search_frame = tk.Frame(root)
sort_search_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky="w")

search_var = tk.StringVar()
entry = tk.Entry(sort_search_frame, textvariable=search_var, width=30)
entry.grid(row=0, column=0, padx=5)

btn = tk.Button(sort_search_frame, text="Поиск", command=search_tree)
btn.grid(row=0, column=1, padx=5)

sort_var = tk.StringVar()
sort_combobox = ttk.Combobox(sort_search_frame, textvariable=sort_var, state="readonly", width=15)
sort_combobox['values'] = ("Цена ↑", "Цена ↓", "Дата ↑", "Дата ↓")
sort_combobox.set("Сортировка")
sort_combobox.grid(row=0, column=2, padx=10)


tk.Button(sort_search_frame, text="Применить сортировку", command=sort_products).grid(row=0, column=3, padx=5)


# Фильтрация
filter_frame = tk.Frame(root)
filter_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")

tk.Label(filter_frame, text="Дата (например 2024-05-26):").grid(row=0, column=0)
entry_date = tk.Entry(filter_frame)
entry_date.grid(row=0, column=1, padx=5)

tk.Label(filter_frame, text="Макс. цена:").grid(row=0, column=2)
entry_price = tk.Entry(filter_frame)
entry_price.grid(row=0, column=3, padx=5)

tk.Button(filter_frame, text="Фильтровать", command=lambda: filter_data(entry_date.get(), entry_price.get())).grid(row=0, column=4, padx=10)


# Фреймы таблиц 
frame_top = tk.Frame(root)
frame_top.grid(row=4, column=0, columnspan=3, pady=10, sticky="nsew")

frame_bottom = tk.Frame(root)
frame_bottom.grid(row=5, column=0, columnspan=3, pady=10, sticky="nsew")


# Таблица продуктов
columns = ("Name", "Price", "Article", "Color", "entry_id", "spec_id")
tree_products = ttk.Treeview(frame_top, columns=columns, show="headings")
tree_products.heading("Name", text="Название")
tree_products.heading("Price", text="Цена")
tree_products.heading("Article", text="Артикль")
tree_products.heading("Color", text="Цвет")
tree_products.heading("entry_id", text="ID записи")
tree_products.heading("spec_id", text="ID продукта")
tree_products.pack()


# Таблица статистики
tree_stats = ttk.Treeview(frame_bottom, columns=("Date", "Count", "entryID"), show="headings", height=6)
tree_stats.heading("Date", text="Дата")
tree_stats.heading("Count", text="Количество")
tree_stats.heading("entryID", text="ID записи")
tree_stats.pack()


# События выбора строк
def on_date_select(event):
    global selected_entry_id
    selected_item = tree_stats.selection()
    if not selected_item:
        return
    values = tree_stats.item(selected_item)['values']
    selected_entry_id = values[2]

    for row in tree_products.get_children():
        tree_products.delete(row)

    cursor.execute("SELECT name, price, article, color, entry_id, spec_id FROM Products WHERE entry_id = ?", (selected_entry_id,))
    result = cursor.fetchall()

    for row in result:
        tree_products.insert('', 'end', values=row)


def on_product_select(event):
    selected_item = tree_products.selection()
    if not selected_item:
        return

    values = tree_products.item(selected_item)['values']
    spec_id = values[5]
    show_image(spec_id)

#очистка выбора
clear_frame = tk.Frame(root)
clear_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="nw")

def clear_selection():
    global selected_entry_id
    selected_entry_id = None
    show_data()

tk.Button(clear_frame, text="Сбросить выбор", command=clear_selection).grid(padx=5)

for frame in [button_frame, image_frame, sort_search_frame, filter_frame, frame_top, frame_bottom, clear_frame]:
    frame.configure(bg=BG_COLOR)

tree_stats.bind("<<TreeviewSelect>>", on_date_select)
tree_products.bind("<<TreeviewSelect>>", on_product_select)


# Инициализация
show_data()


 
root.mainloop()
