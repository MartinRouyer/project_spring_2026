import threading
import time

class Regulation:
    def __init__(self, hardware):
        self.hw = hardware
        self.running = False
        
        # Targets values
        self.target_temp = 22.0
        self.target_hum = 70.0
        self.margin = 1
        
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
        self.hw.set_fan(False)
        self.hw.set_light(0)

    def _control_loop(self):
        self.live_data["status"] = "Running"
        
        while self.running:

            print(' -- new control loop -- ')
            temp = self.hw.get_temperature()
            hum = self.hw.get_humidity()

            self.live_data["temp"] = temp
            self.live_data["hum"] = hum
                
            # Temp
            if temp < (self.target_temp - self.margin):
                self.hw.set_heat(True)
                self.hw.set_fan(False)
                self.live_data["heat"] = True
                self.live_data["fan"] = False
            elif temp > (self.target_temp + self.margin):
                self.hw.set_heat(False)
                self.hw.set_fan(True)
                self.live_data["heat"] = False
                self.live_data["fan"] = True

            # Humidity
            if hum < (self.target_hum - 5.0):
                self.hw.set_mist(True)
                self.hw.set_fan(False)
                self.live_data["mist"] = True
                self.live_data["fan"] = False
            elif hum > self.target_hum:
                self.hw.set_mist(False)
                self.hw.set_fan(True)
                self.live_data["mist"] = False
                self.live_data["fan"] = True

            time.sleep(5)