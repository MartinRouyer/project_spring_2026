import random
import time

class HardwareInterface:
    def get_temperature(self): raise NotImplementedError
    def get_humidity(self): raise NotImplementedError
    def set_fan(self, state: bool): raise NotImplementedError
    def set_light(self, state: bool): raise NotImplementedError
    def set_mist(self, state: bool): raise NotImplementedError
    def set_heat(self, state: bool): raise NotImplementedError
    def take_pict(self, filename: str, params: dict): raise NotImplementedError
    def live_preview(self,state: bool): raise NotImplementedError



class RealHardware():
    def __init__(self):
        """
        Init all modules connected to the Pi : 
        - MOSFET actuators for all electrical component
        - temparature/humidity sensor
        """
        import board
        import adafruit_dht
        from gpiozero import PWMOutputDevice
        from gpiozero import OutputDevice
        import os
        import subprocess
        
        self.dht_dev = adafruit_dht.DHT11(board.D4, use_pulseio=False)

        #self.picam2 = Picamera2()
        
        self.PIN_MIST = 17
        self.PIN_HEAT = 27
        self.PIN_LIGHT = 23
        #self.PIN_FAN = 1

        self.heat = OutputDevice(self.PIN_HEAT, initial_value=False)
        self.mist = OutputDevice(self.PIN_MIST, initial_value=False)
        self.light = OutputDevice(self.PIN_LIGHT, initial_value=False)


        self.heat_state = False
        self.mist_state = False
        self.light_state = False
        # self.fan_state = False

    def get_temp_hum(self):
        """
        Get temperature and humidity data from the sensor.
        Sensor can return a lot of RuntineError.
        """
        try:
            temp = self.dht_dev.temperature
            hum = self.dht_dev.humidity
            if temp is not None and hum is not None:
                return temp, hum
            return None, None
            
        except RuntimeError as error:
            print(f"Error sensing temp or hum : {error.args[0]}")
            return None, None

        except Exception as error:
            self.dht_dev.exit()
            raise error
    
    
    # Functions to pilot MOSFET

    def set_light(self, state: bool):
        if state != self.light_state:
            self.light_state = state

            if state:
                self.light.on()
                print("Light ON")
            else:
                self.light.off()
                print("Light OFF")        
        

    def set_mist(self, state: bool):
        if state != self.mist_state:
            self.mist_state = state

            if state:
                self.mist.on()
                print("Mist ON")
            else:
                self.mist.off()
                print("Mist OFF")

    def set_heat(self, state: bool):
        if state != self.heat_state:
            self.heat_state = state

            if state:
                self.heat.on()
                print("Heat ON")
            else:
                self.heat.off()
                print("Heat OFF")

    '''
    # For futur use, if fan is mounted on the hardware
    def set_fan(self, state: bool):
        if state != self.fan_state:
            self.fan_state = state

            if state:
                self.fan.on()
                print("Fan ON")
            else:
                self.fan.off()
                print("Fan OFF")
    '''

    # Mock take pict because camera not mounted in the hardware for now
    def take_pict(self, filename: str, params: dict):
        import os
        from PIL import Image, ImageDraw

        self.set_light(True)
    
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        img = Image.new("RGB", (640, 480), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), filename, fill=(255, 255, 255))
        img.save(filename)
        print(f"Picture saved -> {filename}")
    


    '''
    # For future use, when the camera is connected to the hardware
    def take_pict(self, filename: str, params: dict):

        self.set_light(50) #a definir 

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        cmd = [
            "rpicam-still", "-o", filename, "--nopreview",
            "--gain",       str(float(params.get('iso', 100)) / 100.0),
            "--shutter",    str(int(float(params.get('shutter', 10)) * 1000)),
            "--brightness", str(params.get('brightness', '0.0')),
            "--contrast",   str(params.get('contrast', '1.0')),
            "--saturation", str(params.get('saturation', '1.0')),
            "--awb", params.get('awb_mode', 'auto')
        ]

        print(f"Running: {cmd}")
        subprocess.run(cmd)
        print(f"Picture saved -> {filename}")
    '''
    
    # Mock live preview because camera not mounted in the hardware for now
    def live_preview(self, state: bool, params: dict = {}):
        print(params)
        print(f"Live Preview : {'ON' if state else 'OFF'}")

    '''
    # For future use, when the camera is connected to the hardware
    def live_preview(self, state: bool, params: dict = {}):
        import subprocess
        if state:
            AWB_MAP = {
                "0": "auto", "1": "incandescent", "2": "tungsten",
                "3": "fluorescent", "4": "indoor", "5": "daylight", "6": "cloudy"
            }
            cmd = [
                "rpicam-hello", "-t", "0",
                "--gain",       str(float(params.get('iso', 100)) / 100.0),
                "--shutter",    str(int(float(params.get('shutter', 10)) * 1000)),
                "--brightness", str(params.get('brightness', '0.0')),
                "--contrast",   str(params.get('contrast', '1.0')),
                "--saturation", str(params.get('saturation', '1.0')),
                "--awb",        AWB_MAP.get(str(params.get('awb_mode', '0')), 'auto'),
            ]
            self._preview_proc = subprocess.Popen(cmd)
            print("Live Preview : ON")
        else:
            if hasattr(self, '_preview_proc') and self._preview_proc:
                self._preview_proc.terminate()
                self._preview_proc = None
            print("Live Preview : OFF")
    '''

    def shutdown(self):
        """
        Stop and shutdown (free the pin) all electrical modules
        """

        self.mist.off()
        self.light.off()
        self.heat.off()
        #self.fan.off()


        self.mist.close()
        self.light.close()
        self.heat.close()
        #self.fan.close()

        self.dht_dev.exit()

class MockHardware(HardwareInterface):
    """
    Class used to develop interface in absenc of mounted hardware.
    board adafruit_dht and gpiozero need areal Pi device to be loaded
    """
    def __init__(self):
        self.temp = 20.0
        self.hum = 50.0
        
        self.heat_state = False
        self.fan_state = False
        self.mist_state = False
        self.light_state = 0
        
        print("Mock hardware loaded")


    def get_temp_hum(self):
        if self.heat_state:
            self.temp += 0.2
        elif self.fan_state:
            self.temp -= 0.1
        else:
            self.temp += (20.0 - self.temp) * 0.05
            
        temp = round(self.temp + random.uniform(-0.1, 0.1), 2)
    
        if self.mist_state:
            self.hum += 2.0
        elif self.fan_state:
            self.hum -= 1.0
        
        self.hum = max(0, min(100, self.hum))
        hum =  round(self.hum + random.uniform(-0.5, 0.5), 2)

        return temp,hum


    def get_temperature(self):
        if self.heat_state:
            self.temp += 0.2
        elif self.fan_state:
            self.temp -= 0.1
        else:
            self.temp += (20.0 - self.temp) * 0.05
            
        return round(self.temp + random.uniform(-0.1, 0.1), 2)

    def get_humidity(self):
        if self.mist_state:
            self.hum += 2.0
        elif self.fan_state:
            self.hum -= 1.0
        
        self.hum = max(0, min(100, self.hum))
        return round(self.hum + random.uniform(-0.5, 0.5), 2)

    def set_fan(self, state: bool):
        if state != self.fan_state:
            self.fan_state = state
            print(f"Fan : {'ON' if state else 'OFF'}")

    def set_light(self, percent: int):
        if percent != self.light_state:
            self.light_state = percent
            print(f"Light : {percent}%")

    def set_mist(self, state: bool):
        if state != self.mist_state:
            self.mist_state = state
            print(f"Mist : {'ON' if state else 'OFF'}")

    def set_heat(self, state: bool):
        if state != self.heat_state:
            self.heat_state = state
            print(f"Heat : {'ON' if state else 'OFF'}")

    def take_pict(self, filename: str, params: dict):
        import os
        from PIL import Image, ImageDraw
    
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        img = Image.new("RGB", (640, 480), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), filename, fill=(255, 255, 255))
        img.save(filename)
        print(f"Picture saved -> {filename}")

    def live_preview(self, state: bool, params: dict = {}):
        print(params)
        print(f"Live Preview : {'ON' if state else 'OFF'}")
        
    def shutdown(self):
        print('Shutdown app')
