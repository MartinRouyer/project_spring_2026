# project_spring_2026

Control software for automated time-lapse imaging of *Arabidopsis thaliana* leaves infected with *Dickeya dadantii*, with real-time monitoring and regulation of temperature, humidity and lighting in a controlled atmosphere.

Built on top of the [FIAT LUX Camera Control](https://2022.igem.wiki/insa-lyon1/software) open-source project (iGEM 2022, INSA Lyon).

## Hardware

The setup is built around a Raspberry Pi 5. The following components are connected to it:

| Category | Component | Model | GPIO pin |
|---|---|---|---|
| SBC | Single Board Computer | Raspberry Pi 5 4GB | — |
| Camera | Camera module | — | CSI |
| Sensing | Temp. & Humidity sensor | DHT22 module | 4 |
| Lighting | LED strip | CCT 24V IP65 60LED/m, driven via MOSFET module | 23 |
| Actuators | Ultrasonic fogger | 5V 20mm USB atomizer module | 17 |
| | Heating mat | TRU COMPONENTS 12V/AC 32W polyester | 27 |
| Power | Main PSU | ALITOVE 12V 5A 60W | — |
| | DC-DC step-down | Greluma 12V→5V 5A 25W | — |
| | MOSFET driver | 5V-36V 15A 400W PWM switch module | — |
| | Fuse box | Vaskula 4-way 12V | — |
| Display | Touchscreen | Freenove 7" 800x480 IPS MIPI DSI | DSI |

## Installation

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/)

### 1. System dependencies

On the Raspberry Pi, install the following system packages first:

```bash
sudo apt-get install python3-tk
sudo apt-get install libcap-dev
```

### 2. Clone and install

```bash
git clone https://github.com/MartinRouyer/project_spring_2026
cd project_spring_2026
uv sync
```

### 3. Run

```bash
uv run start-app
```

### Simulation mode

To run without physical hardware (e.g. for development on a laptop), set the following flag in `app/main.py`:

```python
mode_simu = True
```

`MockHardware` will be used instead of `RealHardware`, simulating sensor readings and generating placeholder images via Pillow. No GPIO or camera libraries are required in this mode.

## Project structure
 
```
app/
├── main.py        Entry point — hardware selection and object wiring
├── hardware.py    RealHardware and MockHardware classes
├── regulation.py  Sensor reading loop, actuator control, CSV logging
├── timelapse.py   Image capture scheduling and EXIF metadata embedding
└── interface.py   Tkinter GUI
 
docs/
└── fiat_lux_camera_code/   # Original iGEM 2022 source, kept for reference
```
 
The three main objects (`Interface`, `Regulation`, `TimelapseManager`) are instantiated in `main.py` and reference each other as `interface.regul.hw`.


## Adapting the project

### Regulation

The regulation loop runs every 5 seconds in a background thread. The target temperature and humidity are set directly in the interface before starting a timelapse.

The control logic is a simple on/off mechanism:

- **Heating mat** — turns on when temperature drops below `target_temp - margin_temp`, turns off when it exceeds `target_temp`
- **Fogger** — turns on when humidity drops below `target_hum - margin_hum`, turns off when it exceeds `target_hum - margin_hum/2`
- **LED strip** — switches on/off according to the position in the day/night cycle, calculated from the cycle start time

Margins are defined in `regulation.py` (`margin_temp`, `margin_hum`).

### Adding a sensor

1. Add a reading method in `RealHardware` in `hardware.py`
2. Call it in `_control_loop` in `regulation.py` and store the value in `self.live_data`
3. Display the value in `update_gui` in `interface.py`

**Example : adding a second temperature sensor:**

In `hardware.py`, in `RealHardware.__init__`:
```python
self.dht_dev2 = adafruit_dht.DHT11(board.D17, use_pulseio=False)
```

In `RealHardware`:
```python
def get_temp2(self):
    try:
        return self.dht_dev2.temperature
    except RuntimeError as error:
        print(f"Error reading sensor 2: {error.args[0]}")
        return None
```

In `regulation.py`, in `_control_loop`:
```python
temp2 = self.hw.get_temp2()
if temp2 is not None:
    self.live_data["temp2"] = temp2
```

---

### Adding an actuator

1. Add the GPIO pin and the on/off method in `RealHardware` in `hardware.py`
2. Add the cleanup calls in `RealHardware.shutdown` in `hardware.py` to ensure the component is properly turned off and the GPIO resource is released when the application closes.
3. Add the trigger logic in `_control_loop` in `regulation.py` and a state entry in `self.live_data`
3. Display the state in `update_gui` in `interface.py`


**Regarding dependencies:**

- If the component is controlled via a MOSFET module, no new library is needed — `gpiozero` and `OutputDevice` are already used in `hardware.py` for the existing actuators.
- If the component is powered directly by the Raspberry Pi GPIO and requires a dedicated library, add it to `pyproject.toml` and run `uv sync`, or install it as a system package with `sudo apt-get install`.

**Example — adding a fan controlled via MOSFET:**

In `hardware.py`, in `RealHardware.__init__`:
```python
self.PIN_FAN = 1
self.fan = OutputDevice(self.PIN_FAN, initial_value=False)
self.fan_state = False
```

In `RealHardware`:
```python
def set_fan(self, state: bool):
    if state != self.fan_state:
        self.fan_state = state
        if state:
            self.fan.on()
            print("Fan ON")
        else:
            self.fan.off()
            print("Fan OFF")
```


```python
def shutdown(self):
    ...
    self.fan.off()
    ...
    self.fan.close()
```

In `regulation.py`, in `_control_loop`:
```python
if temp > self.target_temp:
    self.hw.set_fan(True)
    self.live_data["fan"] = True
else:
    self.hw.set_fan(False)
    self.live_data["fan"] = False
```

### Adding a timelapse parameter

1. Add the key and default value in `self.default_values` in `interface.py`
2. Add the corresponding `tk.Entry` in the appropriate `LabelFrame` in `_build_setup_tab`
3. The parameter will be automatically included in the dict returned by `timelapse.get_timelapse_params()` and available wherever that dict is used in `timelapse.py`

### Camera configuration

Camera parameters (ISO, shutter speed, brightness, contrast, saturation, white balance) are set directly in the interface before starting a timelapse.

The system commands used to capture images and run the live preview are defined in `hardware.py` in `RealHardware.take_pict` and `RealHardware.live_preview`. The current implementations use `rpicam-still` and `rpicam-hello`, which are compatible with Raspberry Pi OS Bullseye and later. A Raspberry Pi 5 should support the same commands, but if you are using a different OS version or a different Pi model, the commands may need to be updated.

### EXIF metadata

Each image embeds the last CSV row (timestamp, temperature, humidity) and the camera parameters as EXIF metadata in the `UserComment` field. This is handled in `timelapse.py` in `_embed_exif`. Add or remove fields from the `comment` string there.

## Data outputs

For each experiment, the following are saved to `data/` by default (configurable in the interface):

| File | Content |
|---|---|
| `{exp_name}_data.csv` | Timestamped temperature and humidity readings |
| `{exp_name}_{index}_{timestamp}.jpg` | Timelapse frames with embedded EXIF metadata |

## Authors

Séverin JORRY & Martin ROUYER — Master 2 Bioinformatics, Lyon 1

**Project supervisor:** Adel Amine GANI — MAP Laboratory UMR5240, Lyon 1 / INSA Lyon / CNRS

**Acknowledgements:** Matthieu — for his help with the electrical assembly