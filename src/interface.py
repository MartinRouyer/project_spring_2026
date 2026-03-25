import tkinter as tk
from tkinter import ttk

class Interface(tk.Tk):
    def __init__(self, regul, timelapse_manager):
        super().__init__()
        
        self.regul = regul
        self.timelapse = timelapse_manager
        self.title("Arabidopsis infection monitoring")
        self.geometry("400x400")

        # Sensors

        self.lbl_temp = tk.Label(self, text="Temp : -- °C -> --")
        self.lbl_temp.pack(anchor="w")

        self.lbl_hum = tk.Label(self, text="Humidity : -- % -> --")
        self.lbl_hum.pack(anchor="w")


        # Settings

        row_t = tk.Frame(self)
        row_t.pack(fill="x", pady=5)
        tk.Label(row_t, text="Target Temp:").pack(side="left")
        self.ent_temp = tk.Entry(row_t, width=5)
        self.ent_temp.insert(0, str(self.regul.target_temp))
        self.ent_temp.pack(side="left", padx=5)
        tk.Button(row_t, text="Set", command=self.update_target_temp).pack(side="left")

        row_h = tk.Frame(self)
        row_h.pack(fill="x", pady=5)
        tk.Label(row_h, text="Target Hum: ").pack(side="left")
        self.ent_hum = tk.Entry(row_h, width=5)
        self.ent_hum.insert(0, str(self.regul.target_hum))
        self.ent_hum.pack(side="left", padx=5)
        tk.Button(row_h, text="Set", command=self.update_target_hum).pack(side="left")


        # Modules

        self.status_indicators = {}
        
        for module in ["heat", "mist", "fan", "light"]:
            row = tk.Frame(self)
            row.pack(fill="x", pady=2)

            lbl_name = tk.Label(row, text=f"{module.upper()} :", width=10, anchor="w", font=("Arial", 10))
            lbl_name.pack(side="left")
            
            indicator = tk.Label(row, width=1, height=1, relief="sunken", bg="white")
            indicator.pack(side="left", padx=10)
            
            self.status_indicators[module] = indicator



        # Timelapse
        self.setup_timelapse_interface()

        row_btn = tk.Frame(self)
        row_btn.pack(pady=5)

        tk.Button(self, text="Start Timelapse", command=self.timelapse.start_timelapse).pack(side="left", padx=5)

        tk.Button(self, text="Stop Timelapse", command=self.timelapse.stop_timelapse).pack(side="left", padx=5)

        tk.Button(self, text="Reset", command=self.reset_timelapse_params).pack(side="left", padx=5)

        self.update_gui()


    def setup_timelapse_interface(self):
        params_timelaps = {
            "exp_name": "Experiment name:",
            "length": "Timelapse length (min):",
            "interval": "Take pict every (min):", 
            "iso": "ISO for photo:",
            "name": "Base Filename:"
        }

        self.default_values = {
            "exp_name": "exp_001",
            "length": "180",
            "interval": "20",
            "iso": "100",
            "name": "test"
        }

        self.timelapse_entries = {}

        for param_id, param_text in params_timelaps.items():
            row = tk.Frame(self)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=param_text, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=10)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        row_folder = tk.Frame(self)
        row_folder.pack(fill="x", pady=2)
        tk.Label(row_folder, text="Save folder:", width=20, anchor="w").pack(side="left")
        self.ent_folder = tk.Entry(row_folder, width=20)
        self.ent_folder.insert(0, "/home/pi/timelapse")
        self.ent_folder.pack(side="left", padx=5)
        tk.Button(row_folder, text="Browse", command=self.browse_folder).pack(side="left")


    def reset_timelapse_params(self):
        for param_id, entry in self.timelapse_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, self.default_values[param_id])
        print("Reset parameters")

        
    '''
    def get_timelapse_params(self):
        timelapse_params = {}
        
        for param_id, entry_widget in self.timelapse_entries.items():
            timelapse_params[param_id] = entry_widget.get()
            
        return timelapse_params


    def start_timelapse(self):
        timelapse_params = self.get_timelapse_params()
        self.ms_interval = int(params['interval']) * 60000
        self.picts_left = int(timelapse_params['length']) // int(timelapse_params['interval'])
        self.picts_count = 0 
        self.timelapse_active = True

    def run_timelapse(self):
        if self.timelapse_active and self.picts_left > 0:
            
            params = self.get_timelapse_params()
            self.regul.hw.take_pict(params)

            self.picts_left -= 1
            self.picts_count += 1
            print(f"{self.picts_count} picture taken. {self.picts_left} picts remaining")

            self.after(self.ms_interval, self.run_timelapse)
        else:
            self.timelapse_active = False
            print("Timelapse end")
    '''

    def update_target_temp(self):
        try:
            val = float(self.ent_temp.get())
            self.regul.target_temp = val
            print(f"Temperature target value set to : {val}°C")
        except ValueError:
            print("Enter a valid values for temperature")

    def update_target_hum(self):
        try:
            val = int(self.ent_hum.get())
            self.regul.target_hum = val
            print(f"Humidity target value set to : {val}%")
        except ValueError:
            print("Enter a valid value for humidity")

    def update_gui(self):
        data = self.regul.live_data

        t = data["temp"]
        h = data["hum"]
        
        self.lbl_temp.config(text=f"Temperature: {t:.1f} °C -> {self.regul.target_temp}" if t is not None else "Temp: ERR")
        self.lbl_hum.config(text=f"Humidity: {h:.1f} % -> {self.regul.target_hum}" if h is not None else "Hum: ERR")

        for module in ["heat", "mist", "fan", "light"]:
            is_on = data.get(module, False)
            color = "#2ECC71" if is_on else "white" 
            self.status_indicators[module].config(bg=color)

        self.after(1000, self.update_gui)

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, folder)
            print(f"Folder selected : {folder}")