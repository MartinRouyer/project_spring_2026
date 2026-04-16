import tkinter as tk
from tkinter import ttk
import json
from tkinter import filedialog, messagebox

class Interface(tk.Tk):
    def __init__(self, regul, timelapse_manager):
        super().__init__()
        
        self.regul = regul
        self.timelapse = timelapse_manager
        self.title("Arabidopsis infection monitoring")
        self.geometry("400x700")

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
        row_btn.pack(fill="x", pady=5, anchor="w")

        tk.Button(row_btn, text="Start Timelapse", command=self.timelapse.start_timelapse).pack(side="left", padx=5)

        tk.Button(row_btn, text="Stop Timelapse", command=self.timelapse.stop_timelapse).pack(side="left", padx=5)

        tk.Button(row_btn, text="Reset", command=self.reset_timelapse_params).pack(side="left", padx=5)

        # Templating
        row_template = tk.Frame(self)
        row_template.pack(fill="x", pady=5, anchor="w")

        tk.Label(row_template, text="Parameters template :").pack(side="left")
        tk.Button(row_template, text="Export", command=self.export_template).pack(side="left", padx=5)
        tk.Button(row_template, text="Import", command=self.import_template).pack(side="left", padx=5)

        # Live preview
        self.preview_on = False

        self.btn_preview = tk.Button(self, text="Start live preview", command=self.toggle_camera_preview).pack(side="left", padx=5)

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

    def setup_template_interface(self):
        tk.Button(self, text="Export", command=self.export_template).pack(side="left")
        tk.Button(self, text="Import", command=self.import_template).pack(side="left")

    def export_template(self):
        data = {
            "target_temp": self.ent_temp.get(),
            "target_hum": self.ent_hum.get(),
            "folder": self.ent_folder.get(),
            "timelapse_params": {id: entry.get() for id, entry in self.timelapse_entries.items()}
        }

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Template"
        )

        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo('Done',f'Successfully saved template : {f}')
                print(f"Template saved in : {filepath}")
            except Exception as e:
                messagebox.showerror("Error", {e})

    def import_template(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath:
            return

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            # Update values for all params
            self.ent_temp.delete(0, tk.END)
            self.ent_temp.insert(0, data.get("target_temp", ""))
            
            self.ent_hum.delete(0, tk.END)
            self.ent_hum.insert(0, data.get("target_hum", ""))
            
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, data.get("folder", ""))

            t_params = data.get("timelapse_params", {})
            for p_id, value in t_params.items():
                if p_id in self.timelapse_entries:
                    self.timelapse_entries[p_id].delete(0, tk.END)
                    self.timelapse_entries[p_id].insert(0, value)

            self.update_target_temp()
            self.update_target_hum()
            
            messagebox.showinfo('Done',f'Successfully loaded template : {filepath}')
            print(f"Tamplate loaded from : {filepath}")
        except Exception as e:
            messagebox.showerror("Error", {e})

    
    def toggle_camera_preview(self):
        # Act like a switch
        self.preview_on = not self.preview_on
        
        if self.preview_on:
            self.regul.hw.live_preview(True)
            self.btn_preview.config(text="Stop live preview")
        else:
            self.regul.hw.live_preview(False)
            self.btn_preview.config(text="Start live preview")