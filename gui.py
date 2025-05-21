import tkinter as tk
from main import main

root = tk.Tk()
root.title("Парсер")

button = tk.Button(root, text="Запустить парсер", command=main)
button.pack(pady=20)

root.mainloop()