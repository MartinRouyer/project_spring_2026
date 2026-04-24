import tkinter as tk
import os
from tkinter import ttk
import json
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Interface(tk.Tk):
    def __init__(self, regul, timelapse_manager):
        """
        Initialize the main application window, UI components, and data structures.

        Sets up the tabbed interface, initializes history buffers for 
        environmental data, builds the setup/timelapse layouts, and starts 
        the background GUI update loop.
        """
        super().__init__()

        self.regul = regul
        self.timelapse = timelapse_manager
        self.title("Plant timelapse app")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.resizable(True, True)

        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # notebook = tabs 
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.history_limit = 50
        self.temp_history = []
        self.hum_history = []


        # tab 1 : parameters
        self.tab_setup = tk.Frame(self.notebook)
        self.notebook.add(self.tab_setup, text="Setup")

        # tab 2 : timelapse (only if start)
        self.tab_timelapse = tk.Frame(self.notebook)
        self.notebook.add(self.tab_timelapse, text="Timelapse")
        self.notebook.hide(self.tab_timelapse)

        # Settings

        self._build_setup_tab()
        self._build_timelapse_tab()

        self.update_gui()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    
    # Setup tab
    def _build_setup_tab(self):
        parent = self.tab_setup
        
        # Scrollbar
        container = tk.Frame(parent)
        container.pack(fill="both", expand=True)
        self.scroll_canvas_setup = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.scroll_canvas_setup.yview, width=25)
        self.scroll_canvas_setup.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas_setup.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(self.scroll_canvas_setup)
        self.scroll_canvas_setup.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: self.scroll_canvas_setup.configure(
            scrollregion=(0, 0, max(inner.winfo_reqwidth(), self.scroll_canvas_setup.winfo_width()),
                                max(inner.winfo_reqheight(), self.scroll_canvas_setup.winfo_height()))))
        self.scroll_canvas_setup.bind("<Configure>", lambda e: self.scroll_canvas_setup.configure(scrollregion=self.scroll_canvas_setup.bbox("all")))
        self.scroll_canvas_setup.bind("<Enter>", lambda e: [
            self.bind_all("<Button-4>", lambda e: self.scroll_canvas_setup.yview_scroll(-1, "units")),
            self.bind_all("<Button-5>", lambda e: self.scroll_canvas_setup.yview_scroll(1, "units"))
        ])

        # 2 columns to separate parameters 
        col_left = tk.Frame(inner)
        col_left.pack(side="left", fill="both", expand=True)

        col_right = tk.Frame(inner)
        col_right.pack(side="left", fill="both", expand=True)

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

        # General informations bloc
        frm_general = tk.LabelFrame(col_left, text="General", padx=5, pady=5)
        frm_general.pack(fill="x", padx=8, pady=5)

        for param_id, label in [("exp_name", "Experiment name:"), ("name", "Base Filename:")]:
            row = tk.Frame(frm_general)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=15)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        row_folder = tk.Frame(frm_general)
        row_folder.pack(fill="x", pady=2)
        tk.Label(row_folder, text="Save folder:", width=20, anchor="w").pack(side="left")
        self.ent_folder = tk.Entry(row_folder, width=15)

        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(root_dir, "data")
        self.ent_folder.insert(0, data_dir)

        self.ent_folder.pack(side="left", padx=5)
        tk.Button(row_folder, text="Browse", command=self.browse_folder).pack(side="left")

        # Timelapse bloc
        frm_timelapse = tk.LabelFrame(col_left, text="Timelapse", padx=5, pady=5)
        frm_timelapse.pack(fill="x", padx=8, pady=5)

        for param_id, label in [("length", "Total length (min):"), ("interval", "Interval (min):")]:
            row = tk.Frame(frm_timelapse)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=10)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        # Camera bloc
        frm_camera = tk.LabelFrame(col_left, text="Camera", padx=5, pady=5)
        frm_camera.pack(fill="x", padx=8, pady=5)

        for param_id, label in [
            ("iso", "ISO (100-800):"),
            ("shutter", "Shutter speed (ms):"),
            ("brightness", "Brightness (-1 to 1):"),
            ("contrast", "Contrast (0 to 32):"),
            ("saturation", "Saturation (0 to 32):")
        ]:
            row = tk.Frame(frm_camera)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=10)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        # AWB choice
        AWB_OPTIONS = ["auto", "incandescent", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
        row_awb = tk.Frame(frm_camera)
        row_awb.pack(fill="x", pady=2)
        tk.Label(row_awb, text="AWB Mode:", width=20, anchor="w").pack(side="left")
        awb_var = tk.StringVar(value=AWB_OPTIONS[int(self.default_values["awb_mode"])])
        awb_menu = ttk.Combobox(row_awb, textvariable=awb_var, values=AWB_OPTIONS, width=15, state="readonly")
        awb_menu.pack(side="left", padx=5)
        self.timelapse_entries["awb_mode"] = awb_var

        # Day/night Cycle bloc
        frm_cycle = tk.LabelFrame(col_right, text="Day / Night Cycle", padx=5, pady=5)
        frm_cycle.pack(fill="x", padx=8, pady=5)

        for param_id, label in [
            ("day_duration", "Day duration (min):"),
            ("night_duration", "Night duration (min):"),
            ("day_intensity", "Day intensity (%):")
        ]:
            row = tk.Frame(frm_cycle)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row, width=10)
            entry.insert(0, self.default_values.get(param_id, ""))
            entry.pack(side="left", padx=5)
            self.timelapse_entries[param_id] = entry

        row_start = tk.Frame(frm_cycle)
        row_start.pack(fill="x", pady=2)
        tk.Label(row_start, text="Start with:", width=20, anchor="w").pack(side="left")
        self.start_with_var = tk.StringVar(value="day")
        tk.Radiobutton(row_start, text="Day", variable=self.start_with_var, value="day").pack(side="left")
        tk.Radiobutton(row_start, text="Night", variable=self.start_with_var, value="night").pack(side="left")

        # Regulation bloc
        frm_regul = tk.LabelFrame(col_right, text="Regulation", padx=5, pady=5)
        frm_regul.pack(fill="x", padx=8, pady=5)

        row_t = tk.Frame(frm_regul)
        row_t.pack(fill="x", pady=2)
        tk.Label(row_t, text="Target Temp (°C):", width=20, anchor="w").pack(side="left")
        self.ent_temp = tk.Entry(row_t, width=5)
        self.ent_temp.insert(0, str(self.regul.target_temp))
        self.ent_temp.pack(side="left", padx=5)
        tk.Button(row_t, text="Set", command=self.update_target_temp).pack(side="left")

        row_h = tk.Frame(frm_regul)
        row_h.pack(fill="x", pady=2)
        tk.Label(row_h, text="Target Humidity (%):", width=20, anchor="w").pack(side="left")
        self.ent_hum = tk.Entry(row_h, width=5)
        self.ent_hum.insert(0, str(self.regul.target_hum))
        self.ent_hum.pack(side="left", padx=5)
        tk.Button(row_h, text="Set", command=self.update_target_hum).pack(side="left")

        # Buttons 
        frm_btns = tk.Frame(col_left)
        frm_btns.pack(fill="x", padx=8, pady=8)

        self.btn_start = tk.Button(frm_btns, text="Start", bg="#2ECC71", fg="white",
                                   font=("Arial", 10, "bold"), command=self._start_timelapse)
        self.btn_start.pack(side="left", padx=4)

        tk.Button(frm_btns, text="Stop", bg="#E74C3C", fg="white",
                  font=("Arial", 10, "bold"), command=self._stop_timelapse).pack(side="left", padx=4)

        self.btn_reset = tk.Button(frm_btns, text="Reset", command=self.reset_timelapse_params)
        self.btn_reset.pack(side="left", padx=4)

        # Templating bloc

        frm_template = tk.LabelFrame(col_right,  text="Templating", padx=5, pady=5)
        frm_template.pack(fill="x", padx=8, pady=8)

        tk.Button(frm_template, text="Export", command=self.export_template).pack(side="left", padx=4)
        tk.Button(frm_template, text="Import", command=self.import_template).pack(side="left", padx=4)

        # Tests bloc
        frm_tests = tk.LabelFrame(col_right, text="Tests", padx=5, pady=5)
        frm_tests.pack(fill="x", padx=8, pady=5)

        self.preview_on = False
        self.btn_preview = tk.Button(frm_tests, text="Start live preview", command=self.toggle_camera_preview)
        self.btn_preview.pack(anchor="w", pady=2)

        row_test_pic = tk.Frame(frm_tests)
        row_test_pic.pack(fill="x", pady=2)
        tk.Label(row_test_pic, text="Test picture:", width=15, anchor="w").pack(side="left")
        self.test_picture_filename = tk.Entry(row_test_pic, width=15)
        self.test_picture_filename.insert(0, "test_picture.jpg")
        self.test_picture_filename.pack(side="left", padx=5)
        tk.Button(row_test_pic, text="Take", command=self.take_test_picture).pack(side="left")

        row_test_light = tk.Frame(frm_tests)
        row_test_light.pack(fill="x", pady=2)
        tk.Label(row_test_light, text="Light intensity (%):", width=15, anchor="w").pack(side="left")
        self.test_light_intensity = tk.Entry(row_test_light, width=5)
        self.test_light_intensity.insert(0, "50")
        self.test_light_intensity.pack(side="left", padx=5)
        tk.Button(row_test_light, text="Set", command=self.test_light).pack(side="left")

    # Timelapse tab (only if start)
    def _build_timelapse_tab(self):
        parent = self.tab_timelapse

        # Scrollbar
        container = tk.Frame(parent)
        container.pack(fill="both", expand=True)
        self.scroll_canvas_timelapse = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.scroll_canvas_timelapse.yview, width=25)
        self.scroll_canvas_timelapse.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.scroll_canvas_timelapse.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(self.scroll_canvas_timelapse)
        self.scroll_canvas_timelapse.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: self.scroll_canvas_timelapse.configure(
            scrollregion=(0, 0, max(inner.winfo_reqwidth(), self.scroll_canvas_timelapse.winfo_width()),
                                max(inner.winfo_reqheight(), self.scroll_canvas_timelapse.winfo_height()))))
        self.scroll_canvas_timelapse.bind("<Configure>", lambda e: self.scroll_canvas_timelapse.configure(scrollregion=self.scroll_canvas_timelapse.bbox("all")))
        self.scroll_canvas_timelapse.bind("<Enter>", lambda e: [
            self.bind_all("<Button-4>", lambda e: self.scroll_canvas_timelapse.yview_scroll(-1, "units")),
            self.bind_all("<Button-5>", lambda e: self.scroll_canvas_timelapse.yview_scroll(1, "units"))
        ])

        frm_top_row = tk.Frame(inner)
        frm_top_row.pack(fill="x", padx=8, pady=5)

        # Status bloc
        frm_status = tk.LabelFrame(frm_top_row, text="Timelapse Status", padx=5, pady=5)
        frm_status.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.lbl_status = tk.Label(frm_status, text="Status: OFF", anchor="w", font=("Arial", 10, "bold"))
        self.lbl_status.pack(fill="x")
        self.lbl_picts = tk.Label(frm_status, text="Photos: 0 / 0", anchor="w")
        self.lbl_picts.pack(fill="x")
        self.lbl_time_left = tk.Label(frm_status, text="Time remaining: --", anchor="w")
        self.lbl_time_left.pack(fill="x")
        self.lbl_next_pict = tk.Label(frm_status, text="Next picture: --", anchor="w")
        self.lbl_next_pict.pack(fill="x")

        # Modules bloc
        frm_modules = tk.LabelFrame(frm_top_row, text="Components", padx=5, pady=5)
        frm_modules.pack(side="left", fill="both", expand=True, padx=(5, 0))

        self.status_indicators = {}
        for module in ["heat", "mist", "light"]:
            row = tk.Frame(frm_modules)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{module.upper()} :", width=10, anchor="w", font=("Arial", 10)).pack(side="left")
            indicator = tk.Label(row, width=2, height=1, relief="sunken", bg="white")
            indicator.pack(side="left", padx=10)
            self.status_indicators[module] = indicator

        # Day/night timeline bloc 
        frm_timeline = tk.LabelFrame(inner, text="Day / Night Cycle", padx=5, pady=5)
        frm_timeline.pack(fill="x", padx=8, pady=5)

        self.canvas_timeline = tk.Canvas(frm_timeline, height=40, width=440, bg="white", highlightthickness=0)
        self.canvas_timeline.pack(anchor="w", pady=2)

        row_legend = tk.Frame(frm_timeline)
        row_legend.pack(anchor="w")
        tk.Label(row_legend, width=2, bg="#FFD700").pack(side="left")
        self.lbl_legend_day = tk.Label(row_legend, text="Day (--%)  ")
        self.lbl_legend_day.pack(side="left")
        tk.Label(row_legend, width=2, bg="#2C3E50").pack(side="left")
        tk.Label(row_legend, text="Night (0%)").pack(side="left")

        # Graph 
        frm_graph = tk.LabelFrame(inner, text="Environment", padx=5, pady=5)

        self.fig = Figure(figsize=(3, 3), dpi=100)
        frm_graph.pack(fill="x", padx=8, pady=5)
        
        self.ax_t = self.fig.add_subplot(211) #2 ligne 1 colonne 1 ère position
        self.ax_h = self.fig.add_subplot(212) #2 ligne 1 colonne 2 eme position
        
        self.fig.tight_layout(pad=1.0)

        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=frm_graph)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True) # , padx=2, pady=2

    

    def _start_timelapse(self):
        self.timelapse.start_timelapse()
        self.update_target_temp()
        self.update_target_hum()
        self.notebook.add(self.tab_timelapse, text=f"Timelapse -- {self.timelapse_entries['exp_name'].get()}")
        self.notebook.select(self.tab_timelapse)

    def _stop_timelapse(self):
        self.timelapse.stop_timelapse()
        self.notebook.hide(self.tab_timelapse)
        self.notebook.select(self.tab_setup)

    
    def update_gui(self):
        """
        Refresh the user interface with the latest sensor data and system states.

        This method updates environmental labels, plots sensor history, manages 
        component status indicators, and handles the timelapse countdown logic. 
        It self-schedules its next execution every 1000ms.
        """
        data = self.regul.live_data
        self.t = data["temp"]
        self.h = data["hum"]

        if self.t is not None:
            self.temp_history.append(self.t)
            if len(self.temp_history) > self.history_limit:
                self.temp_history.pop(0)
        
        if self.h is not None:
            self.hum_history.append(self.h)
            if len(self.hum_history) > self.history_limit:
                self.hum_history.pop(0)

        self.draw_plots()

        for module in ["heat", "mist", "light"]:
            is_on = data.get(module, False)
            self.status_indicators[module].config(bg="#2ECC71" if is_on else "white")

        if self.timelapse.active:
            from datetime import datetime, timedelta
            total = self.timelapse.picts_count + self.timelapse.picts_left
            seconds_left = max(0, int((self.timelapse.end_time - datetime.now()).total_seconds()))
            time_left = str(timedelta(seconds=seconds_left)).split('.')[0]
            self.lbl_status.config(text="Status: Running", fg="#2ECC71")
            self.lbl_picts.config(text=f"Photos: {self.timelapse.picts_count} / {total}")
            self.lbl_time_left.config(text=f"Time remaining: {time_left}")
            if self.timelapse.next_pict_time:
                seconds = max(0, int((self.timelapse.next_pict_time - datetime.now()).total_seconds()))
                self.lbl_next_pict.config(text=f"Next picture in: {str(timedelta(seconds=seconds))}")
        else:
            self.lbl_status.config(text="Status: ■ Idle", fg="black")

        self._draw_timeline()

        self.btn_start.config(state="disabled" if self.timelapse.active else "normal")
        self.btn_reset.config(state="disabled" if self.timelapse.active else "normal")

        self.after(1000, self.update_gui)

    def _draw_timeline(self):
        from datetime import datetime, timedelta
        c = self.canvas_timeline
        c.delete("all")
        w = 440

        if not self.timelapse.active or not self.timelapse.end_time:
            return

        c.create_rectangle(0, 0, w, 40, fill="#2C3E50", outline="")

        now = datetime.now()
        total_s = (self.timelapse.end_time - self.timelapse.start_time).total_seconds()
        elapsed_s = (now - self.timelapse.start_time).total_seconds()

        if self.timelapse.gui.regul.day_duration and self.timelapse.gui.regul.night_duration:
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

        # Photo markers
        total_photos = self.timelapse.picts_count + self.timelapse.picts_left
        for i in range(total_photos):
            elapsed = i * self.timelapse.ms_interval / 1000
            x = min(elapsed / total_s * w, w)
            color = "#2ECC71" if i < self.timelapse.picts_count else "white"
            c.create_line(x, 0, x, 40, fill=color, width=2)

        # Current position marker
        x_now = min(elapsed_s / total_s * w, w)
        c.create_line(x_now, 0, x_now, 40, fill="red", width=2)

        self.lbl_legend_day.config(text=f"Day ({self.timelapse.gui.regul.day_intensity}%)  ")

    def reset_timelapse_params(self):
        for param_id, entry in self.timelapse_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, self.default_values[param_id])
        print("Reset parameters")

    def update_target_temp(self):
        try:
            val = float(self.ent_temp.get())

            if val != self.regul.target_temp :
                self.regul.target_temp = val
                print(f"Temperature target value set to : {val}°C")
                messagebox.showinfo("Temp set",f"Temperature target value set to : {val}°C")

        except ValueError:
            print("Enter a valid value for temperature")

    def update_target_hum(self):
        try:
            val = int(self.ent_hum.get())

            if val != self.regul.target_hum :
                self.regul.target_hum = val
                print(f"Humidity target value set to : {val}%")
                messagebox.showinfo("Hum set",f"Humidity target value set to : {val}°C")

        except ValueError:
            print("Enter a valid value for humidity")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, folder)
            print(f"Folder selected : {folder}")

    def export_template(self):
        data = {
            "target_temp": self.ent_temp.get(),
            "target_hum": self.ent_hum.get(),
            "folder": self.ent_folder.get(),
            "timelapse_params": {id: entry.get() for id, entry in self.timelapse_entries.items()}
        }
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Template"
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo('Done', f'Template saved : {filepath}')
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def import_template(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath:
            return
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.ent_temp.delete(0, tk.END)
            self.ent_temp.insert(0, data.get("target_temp", ""))
            self.ent_hum.delete(0, tk.END)
            self.ent_hum.insert(0, data.get("target_hum", ""))
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, data.get("folder", ""))

            for p_id, value in data.get("timelapse_params", {}).items():
                if p_id in self.timelapse_entries:
                    item = self.timelapse_entries[p_id]
                    
                    # Check for other sort of entries exemple AWD Mode
                    if isinstance(item, tk.StringVar):
                        item.set(value)
                    else:
                        item.delete(0, tk.END)
                        item.insert(0, value)

            # Application des valeurs à la régulation
            self.update_target_temp()
            self.update_target_hum()
            messagebox.showinfo('Done', f'Template loaded : {filepath}')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def toggle_camera_preview(self):
        self.preview_on = not self.preview_on
        if self.preview_on:
            params = self.timelapse.get_timelapse_params()
            self.regul.hw.live_preview(True, params)
            self.btn_preview.config(text="Stop live preview")
        else:
            self.regul.hw.live_preview(False)
            self.btn_preview.config(text="Start live preview")

    def take_test_picture(self):
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

    def draw_plots(self):
        configs = [
            (self.temp_history, self.ax_t, 'red', f"Temperature = {self.t:.1f} °C - Target = {self.regul.target_temp} °C", self.regul.target_temp),
            (self.hum_history, self.ax_h, 'blue', f"Humidity = {self.h:.1f} % - Target = {self.regul.target_hum} %", self.regul.target_hum)
        ]

        for data, ax, color, title, target in configs:
            ax.clear()
            
            ax.grid(True, linestyle=':', alpha=0.6)
            ax.set_facecolor('#f9f9f9')
            
            if data:
                ax.plot(data, color=color, linewidth=1.5, alpha=0.9)
                
                ax.fill_between(range(len(data)), data, color=color, alpha=0.1)
            
            ax.axhline(target, color="#2e7d2e", linestyle='--', linewidth=1.2, label='Cible')
            
            ax.set_xticks([])
            ax.set_title(title, color=color, fontweight='semibold', fontsize=10, pad=10)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('#cccccc')
        
        self.canvas_plot.figure.tight_layout()

        self.canvas_plot.draw()

    def on_closing(self):
        self.regul.stop()

        self.destroy()
