class TimelapseManager:
    def __init__(self, gui):
        self.gui = gui
        self.active = False
        self.picts_left = 0
        self.picts_count = 0
        self.ms_interval = 0
    
    def get_timelapse_params(self):
        timelapse_params = {}
        
        for param_id, entry in self.gui.timelapse_entries.items():
            timelapse_params[param_id] = entry.get()
            
        return timelapse_params

    def start_timelapse(self):
        params = self.get_timelapse_params()
        self.ms_interval = int(params['interval']) * 60000
        self.picts_left = int(params['length']) // int(params['interval'])
        self.picts_count = 0 
        self.active = True
        print(f"Timelapse lauched : {self.picts_left} pictures to be taken.")
        self.run_timelapse()
        
    def stop_timelapse(self):
        self.active = False
        print("User Stop Request")

    def run_timelapse(self):
        if self.active and self.picts_left > 0:
            from datetime import datetime
            import os
            
            params = self.get_timelapse_params()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder = self.gui.ent_folder.get()
            exp_name = params['exp_name']
            filename = os.path.join(folder, f"{exp_name}_{self.picts_count:03d}_{timestamp}.jpg")

            self.gui.regul.hw.take_pict(filename)

            self.picts_left -= 1
            self.picts_count += 1
            print(f"{self.picts_count} picture taken. {self.picts_left} picts remaining")

            self.gui.after(self.ms_interval, self.run_timelapse)
        else:
            self.active = False
            print("Timelapse end")