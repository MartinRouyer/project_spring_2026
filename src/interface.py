import tkinter as tk
from tkinter import ttk

class Interface(tk.Tk):
    def __init__(self, regul):
        super().__init__()
        
        self.regul = regul
        self.title("Arabidopsis infection monitoring")
        self.geometry("400x500")
        self.configure(bg="#f0f0f0")

        # Sensing zone
        self.frame_values = tk.LabelFrame(self, text="Sensors", padx=20, pady=10)
        self.frame_values.pack(padx=20, pady=10, fill="x")

        self.lbl_temp = tk.Label(self.frame_values, text="Temp : -- °C")
        self.lbl_temp.pack(anchor="w")

        self.lbl_hum = tk.Label(self.frame_values, text="Humidity : -- %")
        self.lbl_hum.pack(anchor="w")

        # Modules zone
        self.frame_acts = tk.LabelFrame(self, text="Modules", padx=20, pady=10)
        self.frame_acts.pack(padx=20, pady=10, fill="x")

        self.status_indicators = {} # On stocke les "cases" de couleur ici
        
        for module in ["heat", "mist", "fan", "light"]:
            row = tk.Frame(self.frame_acts)
            row.pack(fill="x", pady=2)

            lbl_name = tk.Label(row, text=f"{module.upper()} :", width=10, anchor="w", font=("Arial", 10))
            lbl_name.pack(side="left")
            
            indicator = tk.Label(row, width=1, height=1, relief="sunken", bg="white")
            indicator.pack(side="left", padx=10)
            
            self.status_indicators[module] = indicator

        self.update_gui()

    def update_gui(self):
        """Récupère les données de Regulation.live_data et met à jour les widgets"""
        data = self.regul.live_data

        t = data["temp"]
        h = data["hum"]
        self.lbl_temp.config(text=f"Température: {t:.1f} °C" if t is not None else "Temp: ERR")
        self.lbl_hum.config(text=f"Humidité: {h:.1f} %" if h is not None else "Hum: ERR")

        for module in ["heat", "mist", "fan", "light"]:
            is_on = data.get(module, False)
            color = "#2ECC71" if is_on else "white" 
            self.status_indicators[module].config(bg=color)

        self.after(1000, self.update_gui)