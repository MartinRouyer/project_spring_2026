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



class RealHardware(HardwareInterface):
    def __init__(self):
        import board
        import adafruit_dht
        from matrix11x7 import Matrix11x7
        import RPi.GPIO as GPIO
        
        self.dev = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        self.matrix11x7 = Matrix11x7()

        self.picam2 = Picamera2()

        self.PIN_FAN = 1
        self.PIN_MIST = 2
        self.PIN_HEAT = 3

        self.GPIO = GPIO # Save GPIO in object for in class use
        self.GPIO.setmode(self.GPIO.BCM) # For universal naming of pins
 
        out_pins = [self.PIN_FAN, self.PIN_MIST, self.PIN_HEAT]
        self.GPIO.setup(out_pins, self.GPIO.OUT) # Set pin as an out pin, default is neutral
        self.GPIO.output(self.PIN_FAN, self.GPIO.LOW) # Shut down on startup

        self.heat_state = False
        self.fan_state = False
        self.mist_state = False
        self.light_state = 0


    def get_temperature(self):
        try:
            return self.dev.temperature
        except Exception as error:
            print(f"Error temp sensing: {error}")
            return None
        
    def get_humidity(self):
        try:
            return self.dev.humidity
        except Exception as error:
            print(f"Error humidity sensing: {error}")
            return None
        
    def set_fan(self, state: bool):
        if state != self.fan_state:
            self.fan_state = state

            if state:
                self.GPIO.output(self.PIN_FAN, self.GPIO.HIGH)
                print("Fan ON")
            else:
                self.GPIO.output(self.PIN_FAN, self.GPIO.LOW)
                print("Fan OFF")

    def set_light(self, percent: int):
        if percent != self.light_state:
            self.light_state = percent

            matrix11x7.fill(percent / 100, 0, 0, 11, 7)
            matrix11x7.show()

    def set_mist(self, state: bool):
        if state != self.mist_state:
            self.mist_state = state

            if state:
                self.GPIO.output(self.PIN_MIST, self.GPIO.HIGH)
                print("Mist ON")
            else:
                self.GPIO.output(self.PIN_MIST, self.GPIO.LOW)
                print("Mist OFF")

    def set_heat(self, state: bool):
        if state != self.heat_state:
            self.heat_state = state

            if state:
                self.GPIO.output(self.PIN_HEAT, self.GPIO.HIGH)
                print("Heat ON")
            else:
                self.GPIO.output(self.PIN_HEAT, self.GPIO.LOW)
                print("Heat OFF")

    '''
    def take_pict(self, filename: str, params: dict):

        # A definir
        self.set_light(50)
        speed = 1000000
        iso = 100

        cmd = ["libcamera-still", "-o", filename, "--shutter", str(speed), "--gain", str(iso), "--immediate", "-n", "--denoise",
            "cdn_hq"]
        print(f"Running :{cmd}")
        subprocess.call(cmd)
        print(filename + " saved")
        self.set_light(0)
    '''
    def take_pict(self, filename: str, params: dict):
        # ? Params
        self.set_light(50)
        self.picam2.capture_file(filename)
        self.set_light(0)
        print(f"Pict saved in : {filename}")

    def take_pict(self, filename: str, params: dict):
        
        
        self.set_light(50)
        
        self.picam2.start() # Can be set in the init if we want the camera up during all the timelapse without starting it for each picture
        time.sleep(2)

        controls = {
            "AeEnable": False,
            "AwbEnable": True, # If True use AwbMode if False use manual 
        }

        # Expo
        shutter_ms = float(params.get('shutter', 10))
        controls["ExposureTime"] = int(shutter_ms * 1000)
        
        # Iso
        iso_val = float(params.get('iso', 100))
        controls["AnalogueGain"] = iso_val / 100.0

        # Other settings
        controls["Brightness"] = float(params.get('brightness', 0.0))
        controls["Contrast"] = float(params.get('contrast', 1.0))
        controls["Saturation"] = float(params.get('saturation', 1.0))
        
        # White balance
        controls["AwbMode"] = int(params.get('awb_mode', 5))


        self.picam2.set_controls(controls)

        self.picam2.capture_file(filename)
        
        self.picam2.stop()
        self.set_light(0)

        print(f"Picture saved in : {filename}")

    def live_preview(self, state: bool):
        if state:
            self.picam2.start()
            self.picam2.start_preview(Preview.QTGL)
        else:
            self.picam2.stop_preview()
            self.picam2.stop()


class MockHardware(HardwareInterface):
    def __init__(self):
        self.temp = 20.0
        self.hum = 50.0
        
        self.heat_state = False
        self.fan_state = False
        self.mist_state = False
        self.light_state = 0
        
        print("Mock hardware loaded")

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

    def live_preview(self, state: bool):
        print(f"Live Preview : {'ON' if state else 'OFF'}")