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
        self.geometry("420x800")

        # Scrollable container
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        scroll_canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(scroll_canvas)
        scroll_canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))
        scroll_canvas.bind_all("<Button-4>", lambda e: scroll_canvas.yview_scroll(-1, "units"))
        scroll_canvas.bind_all("<Button-5>", lambda e: scroll_canvas.yview_scroll(1, "units"))

        # Sensors
        self.lbl_temp = tk.Label(self.inner, text="Temp : -- °C -> --")
        self.lbl_temp.pack(anchor="w")
        self.lbl_hum = tk.Label(self.inner, text="Humidity : -- % -> --")
        self.lbl_hum.pack(anchor="w")

        # Settings

        row_t = tk.Frame(self.inner)
        row_t.pack(fill="x", pady=5)
        tk.Label(row_t, text="Target Temp:").pack(side="left")
        self.ent_temp = tk.Entry(row_t, width=5)
        self.ent_temp.insert(0, str(self.regul.target_temp))
        self.ent_temp.pack(side="left", padx=5)
        tk.Button(row_t, text="Set", command=self.update_target_temp).pack(side="left")

        row_h = tk.Frame(self.inner)
        row_h.pack(fill="x", pady=5)
        tk.Label(row_h, text="Target Hum: ").pack(side="left")
        self.ent_hum = tk.Entry(row_h, width=5)
        self.ent_hum.insert(0, str(self.regul.target_hum))
        self.ent_hum.pack(side="left", padx=5)
        tk.Button(row_h, text="Set", command=self.update_target_hum).pack(side="left")


        # Modules

        self.status_indicators = {}
        
        for module in ["heat", "mist", "fan", "light"]:
            row = tk.Frame(self.inner)
            row.pack(fill="x", pady=2)

            lbl_name = tk.Label(row, text=f"{module.upper()} :", width=10, anchor="w", font=("Arial", 10))
            lbl_name.pack(side="left")
            
            indicator = tk.Label(row, width=1, height=1, relief="sunken", bg="white")
            indicator.pack(side="left", padx=10)
            
            self.status_indicators[module] = indicator


        # Timelapse
        self.setup_timelapse_interface()

        row_btn = tk.Frame(self.inner)
        row_btn.pack(fill="x", pady=5, anchor="w")

        self.btn_start = tk.Button(row_btn, text="Start Timelapse", command=self.timelapse.start_timelapse)
        self.btn_start.pack(side="left", padx=5)

        tk.Button(row_btn, text="Stop Timelapse", command=self.timelapse.stop_timelapse).pack(side="left", padx=5)

        self.btn_reset = tk.Button(row_btn, text="Reset", command=self.reset_timelapse_params)
        self.btn_reset.pack(side="left", padx=5)

        # Timelapse status
        self.lbl_status = tk.Label(self.inner, text="Status: OFF", anchor="w")
        self.lbl_status.pack(fill="x", padx=5)

        self.lbl_picts = tk.Label(self.inner, text="Photos: 0 / 0", anchor="w")
        self.lbl_picts.pack(fill="x", padx=5)

        self.lbl_time_left = tk.Label(self.inner, text="Time remaining: --", anchor="w")
        self.lbl_time_left.pack(fill="x", padx=5)

        self.lbl_next_pict = tk.Label(self.inner, text="Next picture: --", anchor="w")
        self.lbl_next_pict.pack(fill="x", padx=5)


        # Cycle day/night status
        self.canvas_timeline = tk.Canvas(self.inner, height=40, width=380, bg="white", highlightthickness=0)
        self.canvas_timeline.pack(anchor="w", padx=5, pady=5)

        row_legend = tk.Frame(self.inner)
        row_legend.pack(anchor="w", padx=5)

        tk.Label(row_legend, width=2, bg="#FFD700").pack(side="left")
        self.lbl_legend_day = tk.Label(row_legend, text="Day (--%)  ")
        self.lbl_legend_day.pack(side="left")

        tk.Label(row_legend, width=2, bg="#2C3E50").pack(side="left")
        tk.Label(row_legend, text="Night (0%)").pack(side="left")

        # Templating
        row_template = tk.Frame(self.inner)
        row_template.pack(fill="x", pady=5, anchor="w")

        tk.Label(row_template, text="Parameters template :").pack(side="left")
        tk.Button(row_template, text="Export", command=self.export_template).pack(side="left", padx=5)
        tk.Button(row_template, text="Import", command=self.import_template).pack(side="left", padx=5)

        # Live preview
        self.preview_on = False

        row_preview = tk.Frame(self.inner)
        row_preview.pack(fill="x", pady=5, anchor="w")

        self.btn_preview = tk.Button(row_preview, text="Start live preview", command=self.toggle_camera_preview)
        self.btn_preview.pack(side="left", padx=5)

        # Test picture
        row_test_picture = tk.Frame(self.inner)
        row_test_picture.pack(fill="x", pady=10, anchor="w")
        
        tk.Label(row_test_picture, text="Test picture file name:", width=20, anchor="w").pack(side="left")
        
        self.test_picture_filename = tk.Entry(row_test_picture, width=15)
        self.test_picture_filename.insert(0, "test_picture.jpg")
        self.test_picture_filename.pack(side="left", padx=5)

        tk.Button(row_test_picture, text="Take Test Picture", command=self.take_test_picture).pack(side="left", padx=5)


        # Test light
        row_test_light = tk.Frame(self.inner)
        row_test_light.pack(fill="x", pady=10, anchor="w")

        tk.Label(row_test_light, text="Test light intensity (%):", width=20, anchor="w").pack(side="left")

        self.test_light_intensity = tk.Entry(row_test_light, width=15)
        self.test_light_intensity.insert(0, "50")
        self.test_light_intensity.pack(side="left", padx=5)

        tk.Button(row_test_light, text="Set Light", command=self.test_light).pack(side="left", padx=5)

        self.update_gui()



    def setup_timelapse_interface(self):
        params_timelaps = {
            "exp_name": "Experiment name:",
            "length": "Total length (min):",
            "interval": "Interval (min):",
            "iso": "ISO (100-800):",
            "shutter": "Shutter speed (ms):",
            "brightness": "Brightness (-1 to 1):",
            "contrast": "Contrast (0 to 32):",
            "saturation": "Saturation (0 to 32):",
            "awb_mode": "AWB Mode (0-6):",
            "name": "Base Filename:",
            "day_duration": "Day duration (min):",
            "night_duration": "Night duration (min):",
            "day_intensity": "Day Light Intensity (%)"
        }

        self.default_values = {
            "exp_name": "exp_001",
            "length": "180",
            "interval": "20",
            "iso": "100",
            "shutter": "10.0",
            "brightness": "0.0",
            "contrast": "1.0",
            "saturation": "1.0",
            "awb_mode": "5",
            "name": "test",
            "day_duration": "480",
            "night_duration": "480",
            "start_with": "day",
            "day_intensity": "80"

        }

        self.timelapse_entries = {}

        for param_id, param_text in params_timelaps.items():
            row = tk.Frame(self.inner)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=param_text, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=10)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        row_start = tk.Frame(self.inner)
        row_start.pack(fill="x", pady=2)
        tk.Label(row_start, text="Start with:", width=20, anchor="w").pack(side="left")
        self.start_with_var = tk.StringVar(value="day")
        tk.Radiobutton(row_start, text="Day", variable=self.start_with_var, value="day").pack(side="left")
        tk.Radiobutton(row_start, text="Night", variable=self.start_with_var, value="night").pack(side="left")

        row_folder = tk.Frame(self.inner)
        row_folder.pack(fill="x", pady=2)
        tk.Label(row_folder, text="Save folder:", width=20, anchor="w").pack(side="left")
        self.ent_folder = tk.Entry(row_folder, width=20)
        self.ent_folder.insert(0, "/home/sevjorry/M2_BIOINFO/PROJET/Test_folder")
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

        if self.timelapse.active:
            from datetime import datetime, timedelta
            total = self.timelapse.picts_count + self.timelapse.picts_left
            seconds_left = max(0, int((self.timelapse.end_time - datetime.now()).total_seconds()))
            time_left = str(timedelta(seconds=seconds_left)).split('.')[0]
            self.lbl_time_left.config(text=f"Time remaining: {time_left}")
            self.lbl_status.config(text="Status: Running")
            self.lbl_picts.config(text=f"Photos: {self.timelapse.picts_count} / {total}")
            self.lbl_time_left.config(text=f"Time remaining: {str(time_left).split('.')[0]}")
            if self.timelapse.next_pict_time:
                seconds = max(0, int((self.timelapse.next_pict_time - datetime.now()).total_seconds()))
                next_pict_str = str(timedelta(seconds=seconds))
                self.lbl_next_pict.config(text=f"Next picture in: {next_pict_str}")

        self._draw_timeline()

        if self.timelapse.active:
            self.btn_start.config(state="disabled")
        else:
            self.btn_start.config(state="normal")

        self.btn_reset.config(state="disabled" if self.timelapse.active else "normal")

        self.after(1000, self.update_gui)

    def browse_folder(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, folder)
            print(f"Folder selected : {folder}")


    def setup_template_interface(self):
        tk.Button(self.inner, text="Export", command=self.export_template).pack(side="left")
        tk.Button(self.inner, text="Import", command=self.import_template).pack(side="left")

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


    def take_test_picture(self):      
        import os

        filename = self.test_picture_filename.get()

        params = self.timelapse.get_timelapse_params()

        self.regul.hw.live_preview(False) 
        self.btn_preview.config(text="Start live preview")
            
        self.regul.hw.take_pict(filename, params)
            
        print(f"Test picture saved: {filename}")
        messagebox.showinfo("Success", f"Photo saved to:\n{filename}")

    def test_light(self):
        try:
            val = int(self.test_light_intensity.get())
            self.regul.hw.set_light(val)
            self.regul.live_data["light"] = val > 0
            print(f"Test intensity set to {val}%")
        except ValueError:
            print("Invalid value")

    
    def _draw_timeline(self):
        from datetime import datetime, timedelta
        c = self.canvas_timeline
        c.delete("all")
        w = 380
    
        if not self.timelapse.active or not self.timelapse.end_time:
            return

        c.create_rectangle(0, 0, w, 40, fill="#2C3E50", outline="")

        now = datetime.now()
        total_s = (self.timelapse.end_time - self.timelapse.start_time).total_seconds()
        elapsed_s = (now - self.timelapse.start_time).total_seconds()

        # Draw day/night zones
        c.create_rectangle(0, 0, w, 40, fill="#2C3E50", outline="")

        if self.timelapse.gui.regul.day_duration and self.timelapse.gui.regul.night_duration:
            cycle_s = (self.timelapse.gui.regul.day_duration + self.timelapse.gui.regul.night_duration) * 60
            t = 0
            is_day = self.timelapse.gui.regul.start_with == "day"
            while t < total_s:
                x1 = t / total_s * w
                duration = self.timelapse.gui.regul.day_duration * 60 if is_day else self.timelapse.gui.regul.night_duration * 60
                x2 = min((t + duration) / total_s * w, w)
                if is_day:
                    intensity = self.timelapse.gui.regul.day_intensity
                    yellow = f"#{'%02x' % int(255 * intensity/100)}{'%02x' % int(200 * intensity/100)}00"
                    c.create_rectangle(x1, 0, x2, 40, fill=yellow, outline="")
                t += duration
                is_day = not is_day

        # Marker
        x_now = min(elapsed_s / total_s * w, w)
        c.create_line(x_now, 0, x_now, 40, fill="red", width=2)

        self.lbl_legend_day.config(text=f"Day ({self.timelapse.gui.regul.day_intensity}%)  ")