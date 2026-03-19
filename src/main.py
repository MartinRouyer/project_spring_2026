from hardware import MockHardware, RealHardware
from regulation import Regulation
from interface import Interface

mode_simu = True

if mode_simu :
    hardware = MockHardware()
else : 
    hardware = RealHardware()

regul = Regulation(hardware)

app = Interface(regul) 
regul.start()
app.mainloop()