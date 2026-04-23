# src/app/main.py
from .hardware import MockHardware, RealHardware
from .regulation import Regulation
from .interface import Interface
from .timelapse import TimelapseManager

def main():
    mode_simu = True
    if mode_simu:
        hardware = MockHardware()
    else:
        hardware = RealHardware()
    
    regul = Regulation(hardware)
    timelapse = TimelapseManager(None)
    app = Interface(regul, timelapse)
    
    timelapse.gui = app
    regul.start()
    app.mainloop()

if __name__ == "__main__":
    main()