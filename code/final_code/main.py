# This module starts our application.

# Make you sure you executed the command "pip install tkcalendar geopy matplotlib seaborn Pillow tkintermapview" 
# to make sure the application is able to work.

import tkinter as tk
from ui import TrafficDiaryApp

def main():
    root = tk.Tk()
    app = TrafficDiaryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()