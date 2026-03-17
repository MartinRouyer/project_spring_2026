class HardwareInterface:
    def get_temperature(self): raise NotImplementedError
    def get_humidity(self): raise NotImplementedError
    def set_fan(self, state: bool): raise NotImplementedError
    def set_light(self, state: bool): raise NotImplementedError
    def set_mist(self, state: bool): raise NotImplementedError
    def set_heat(self, state: bool): raise NotImplementedError
    def take_pict(self, filename: str): raise NotImplementedError



class RealHardware(HardwareInterface):
    def __init__(self):
        import board
        import adafruit_dht
        from matrix11x7 import Matrix11x7
        import RPi.GPIO as GPIO
        
        self.dev = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        self.matrix11x7 = Matrix11x7()

        self.PIN_FAN = 1
        self.PIN_MIST = 2
        self.PIN_HEAT = 3

        self.GPIO = GPIO # Save GPIO in object for in class use
        self.GPIO.setmode(self.GPIO.BCM) # For universal naming of pins
 
        out_pins = [self.PIN_FAN, self.PIN_MIST, self.PIN_HEAT]
        self.GPIO.setup(out_pins, self.GPIO.OUT) # Set pin as an out pin, default is neutral
        self.GPIO.output(self.PIN_FAN, self.GPIO.LOW) # Shut down on startup


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
        if state:
            self.GPIO.output(self.PIN_FAN, self.GPIO.HIGH)
            print("Fan ON")
        else:
            self.GPIO.output(self.PIN_FAN, self.GPIO.LOW)
            print("Fan OFF")

    def set_light(self, percent: int):
        """
        original name : set_led
        Set led brightness at percent value
        :param percent:
        :return:
        """
        matrix11x7.fill(percent / 100, 0, 0, 11, 7)
        matrix11x7.show()

    def set_mist(self, state: bool):
        if state:
            self.GPIO.output(self.PIN_MIST, self.GPIO.HIGH)
            print("Mist ON")
        else:
            self.GPIO.output(self.PIN_MIST, self.GPIO.LOW)
            print("Mist OFF")

    def set_heat(self, state: bool):
        if state:
            self.GPIO.output(self.PIN_HEAT, self.GPIO.HIGH)
            print("Heat ON")
        else:
            self.GPIO.output(self.PIN_HEAT, self.GPIO.LOW)
            print("Heat OFF")

    def take_pict(self, filename: str, params: dict):
        """
        """

        set_led(par.light)
        speed = par.time_exp
        iso = par.iso
        cmd = ["libcamera-still", "-o", dir + par.name, "--shutter", str(speed), "--immediate", "-n", "--denoise",
            "cdn_hq"]
        print(cmd)
        subprocess.call(cmd)
        print(par.name + " taked")
        set_led(0)



class MockHardware(HardwareInterface):
    def get_temperature(self):
        return 1
    def get_humidity(self):
        return 1
    def set_fan(self, state: bool):
        print(f"Fan : {'ON' if state else 'OFF'}")
    def set_light(self, state: bool):
        print(f"Light : {'ON' if state else 'OFF'}")
    def take_pict(self, filename: str):
        print(f"Photo stored in : {filename}")





# In interface.py :
mode_simu = True

if mode_simu :
    hardware = MockHardware(HardwareInterface)
else : 
    hardware = RealHardware(HardwareInterface)

hardware.set_fan(True)
