class HardwareInterface:
    def get_temperature(self): raise NotImplementedError
    def set_fan(self, state): raise NotImplementedError

class RealHardware(HardwareInterface):
    def get_temperature(self):
        return
    def  set_fan(self, state):
        return

class MockHardware(HardwareInterface):
    def get_temperature(self):
        return 80
    def set_fan(self, state):
        print(f"Ventilateur : {'ON' if state else 'OFF'}")



# In interface.py :
mode_simu = True

if mode_simu :
    hardware = MockHardware(HardwareInterface)
else : 
    hardware = RealHardware(HardwareInterface)

hardware.set_fan(True)
