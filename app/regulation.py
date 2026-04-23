import threading
import time
import csv
from datetime import datetime
import os

class Regulation:
    def __init__(self, hardware):
        self.hw = hardware
        self.running = False
        
        # Targets values
        self.target_temp = 28
        self.target_hum = 100
        self.margin_temp = 2
        self.margin_hum = 10
        
        # Shared data with the interface
        self.live_data = {
            "temp": 0.0,
            "hum": 0.0,
            "heat": False,
            "light": False,
            "mist": False,
            "fan": False,
            "status": "Stoped"
        }

        self.log_path = None
        self.day_duration = None
        self.night_duration = None
        self.start_with = "day"
        self.cycle_start = None
        self.day_intensity = 80

    def _log_data(self, temp, hum):
        if self.log_path is None:
            return
        row = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temp": temp,
            "hum": hum,
        }
        file_exists = os.path.isfile(self.log_path)
        with open(self.log_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)


    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._control_loop, daemon=True) # daemon for the thread to close on closing the app
            self.thread.start()
            self.live_data["status"] = "Started"


    def stop(self):
        self.running = False
        self.live_data["status"] = "Off"
        self.hw.set_heat(False)
        self.hw.set_mist(False)
        #self.hw.set_fan(False)
        self.hw.set_light(False)
        self.hw.shutdown()


    def _control_loop(self):
        self.live_data["status"] = "Running"
        
        while self.running:

            print(' -- new control loop -- ')
            
            temp,hum = self.hw.get_temp_hum()

            if temp is None or hum is None:
                temp = self.live_data["temp"]
                hum = self.live_data["hum"]
            else:
                self.live_data["temp"] = temp
                self.live_data["hum"] = hum
                self._log_data(temp, hum)


            # Temp
            if temp < (self.target_temp - self.margin_temp):
                self.hw.set_heat(True)
                self.live_data["heat"] = True
        
            elif temp > (self.target_temp):
                self.hw.set_heat(False)
                self.live_data["heat"] = False

            # Humidity
            if hum < (self.target_hum - self.margin_hum):
                self.hw.set_mist(True)
                self.live_data["mist"] = True

            elif hum > (self.target_hum - (self.margin_hum/2)):
                self.hw.set_mist(False)
                self.live_data["mist"] = False
                self.live_data["fan"] = True

            now = datetime.now().strftime("%H:%M")

            # Cycle Day/Night
            if self.day_duration and self.night_duration and self.cycle_start:
                cycle = self.day_duration + self.night_duration
                elapsed_min = (datetime.now() - self.cycle_start).total_seconds() / 60
                pos_in_cycle = elapsed_min % cycle
    
                if self.start_with == "day":
                    is_day = pos_in_cycle < self.day_duration
                else:
                    is_day = pos_in_cycle >= self.night_duration

                if is_day:
                    self.hw.set_light(True)#self.day_intensity
                    self.live_data["light"] = True
                else:
                    self.hw.set_light(False)
                    self.live_data["light"] = False

            time.sleep(5)
