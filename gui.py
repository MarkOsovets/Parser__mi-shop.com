import tkinter as tk
from main import main
import sqlite3

root = tk.Tk()
root.title("Парсер")
root.geometry("640x640") 

button = tk.Button(root, text="Запустить парсер", command=main)
button.pack(pady=20)

#def get_data_from_db():
#     conn = sqlite3.connect("bd.db")
#     cursor = conn.cursor()
#     cursor.execute("SELECT product_id, name, price FROM Products", "SELECT image, color, article FROM Specifications")



root.mainloop()




#def on_select(event):
#    for row in tree.get_children():
#        tree.delete(row)
#    selected_index = fio_listbox.curselection()
#    if not selected_index:
#        return None
#    selected_fio = fio_listbox.get(selected_index[0])
#    for i in fio_list:
#        if i["FIO"] == selected_fio:
#            for x in i["Addresses"]:
#                tree.insert("", "end", values=(x["town"], x["street"], x["house"]))
#            break


# fio_list_var = Variable(value=[i["FIO"] for i in fio_list])
# fio_listbox = Listbox(listvariable=fio_list_var)
# fio_listbox.pack(anchor=NW, fill=X, padx=5, pady=5)
# fio_listbox.bind('<<ListboxSelect>>', on_select)

# tree = ttk.Treeview(root)
# tree["columns"] = ("Город", "Улица", "Дом")
# tree.column("#0", width=0, stretch=NO)
# tree.column("Город", width=100, anchor="center")
# tree.column("Улица", width=150, anchor="center")
# tree.column("Дом", width=50, anchor="center")

# tree.heading("Город", text="Город")
# tree.heading("Улица", text="Улица")
# tree.heading("Дом", text="Дом")

# frameforbutton = Frame(root)
# frameforbutton.pack(fill=X, padx=10, pady=10)

# def initdata():
#     fio_list_var.set([i["FIO"] for i in fio_list])

# def reset():
#     fio_list_var.set(())
#     tree.delete(*tree.get_children())

# init_button = Button(frameforbutton, text="Инициализация", command=initdata)
# init_button.pack(side=LEFT, padx=5, pady=5)

# reset_button = Button(frameforbutton, text="Сброс", command=reset)
# reset_button.pack(side=LEFT, padx=5,pady=5)

# menu = Menu(root)
# root.config(menu=menu)
# menu.add_command(label="Инициализация", command=initdata)
# menu.add_command(label="Сброс", command=reset)


# def toggle_filter():
#     if filter_var.get():
#         filtered_fios = [i["FIO"] for i in fio_list if any(addr["town"] == "Брест" for addr in i["Addresses"])]
#         fio_list_var.set(filtered_fios)
#     else:
#         initdata()
# filter_var = BooleanVar()
# filter_checkbox = Checkbutton(root, text="Показать только из Бреста", variable=filter_var, command=toggle_filter)
# filter_checkbox.pack(anchor=W, padx=5, pady=5)


# tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

# root.mainloop()

