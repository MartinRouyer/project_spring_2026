class TimelapseManager:
    def __init__(self, gui):
        self.gui = gui
        self.active = False
        self.picts_left = 0
        self.picts_count = 0
        self.ms_interval = 0
        self.next_pict_time = None
        self.end_time = None
    
    def get_timelapse_params(self):
        timelapse_params = {}
        
        for param_id, entry in self.gui.timelapse_entries.items():
            timelapse_params[param_id] = entry.get()
            
        return timelapse_params

    def start_timelapse(self):
        import os
        from datetime import datetime, timedelta
        params = self.get_timelapse_params()
        self.ms_interval = int(params['interval']) * 60000
        self.picts_left = int(params['length']) // int(params['interval'])
        self.picts_count = 0 
        self.active = True

        self.end_time = datetime.now() + timedelta(minutes=int(params['length']))

        folder = self.gui.ent_folder.get()
        exp_name = params['exp_name']
        self.gui.regul.log_path = os.path.join(folder, f"{exp_name}_data.csv")

        temp = self.gui.regul.hw.get_temperature()
        hum = self.gui.regul.hw.get_humidity()
        self.gui.regul._log_data(temp, hum)

        self.gui.regul.day_start = params['day_start']
        self.gui.regul.day_end = params['day_end']
        self.gui.regul.day_intensity = int(params['day_intensity'])

        print(f"Timelapse lauched : {self.picts_left} pictures to be taken.")
        self.run_timelapse()
        
    def stop_timelapse(self):
        self.active = False
        print("User Stop Request")


    def run_timelapse(self):
        from datetime import datetime, timedelta
        if self.active and self.picts_left > 0:
            from datetime import datetime
            import os
            
            self.gui.regul.hw.live_preview(False) 
            self.gui.btn_preview.config(text="Start live preview")
            
            params = self.get_timelapse_params()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = self.gui.ent_folder.get()
            exp_name = params['exp_name']
            filename = os.path.join(folder, f"{exp_name}_{self.picts_count:03d}_{timestamp}.jpg")

            self.gui.regul.hw.take_pict(filename,params)
            self._embed_exif(filename, params)

            self.picts_left -= 1
            self.picts_count += 1
            print(f"{self.picts_count} picture taken. {self.picts_left} picts remaining")

            self.gui.after(self.ms_interval, self.run_timelapse)

            self.next_pict_time = datetime.now() + timedelta(milliseconds=self.ms_interval)

        else:
            self.active = False
            print("Timelapse end")

    def _embed_exif(self, filename, params):
        import piexif
        import csv
        import os
    
        if not self.gui.regul.log_path:
            return
        
        if not os.path.isfile(self.gui.regul.log_path):
            print("[EXIF] CSV not yet created, skipping.")
            return
    
        with open(self.gui.regul.log_path, 'r') as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return
    
        last_row = rows[-1]
    
        # Commentaire exif dans UserComment
        comment = ", ".join(f"{k}={v}" for k, v in last_row.items())
        camera_info = f", iso={params['iso']}, name={params['name']}, shutter={params['shutter']}, brightness={params['brightness']}, contrast={params['contrast']}, saturation={params['saturation']}, awb_mode={params['awb_mode']}"
        comment += camera_info

        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
        exif_dict["Exif"][piexif.ExifIFD.UserComment] = comment.encode()
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        print(f"Metadata embedded -> {comment}")