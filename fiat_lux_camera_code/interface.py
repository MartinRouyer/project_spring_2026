éé#!/usr/bin/env python3
"""
Author : MATHIEU Theo
github : https://github.com/tzebre
"""

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from PIL import Image
from picamera2 import Picamera2, Preview
import time
from datetime import datetime, timedelta
import shutil
import os
import time
from matrix11x7 import Matrix11x7
import board
import adafruit_dht
import subprocess


def set_led(percent):
    """
    Set led brightness at percent value
    :param percent:
    :return:
    """
    matrix11x7.fill(percent / 100, 0, 0, 12, 7)
    matrix11x7.show()


def take_pict(par, dir):
    """
    Take a pict with par class parameters and put it in directory dir
    :param par:
    :param dir:
    :return:
    """
    print(par.name + " ...")
    print(par.get_all())
    set_led(par.light)
    speed = par.time_exp
    iso = par.iso
    if par.what == True:
        cmd = ["libcamera-still", "-o", dir + par.name, "--shutter", str(speed), "--gain", str(iso), "--awbgain",
               "1,1", "--immediate",
               "-n", "--denoise", "cdn_hq"]
    else:
        cmd = ["libcamera-still", "-o", dir + par.name, "--shutter", str(speed), "--immediate", "-n", "--denoise",
               "cdn_hq"]
    print(cmd)
    subprocess.call(cmd)
    print(par.name + " taked")
    set_led(0)


# specify wich port is use by DHT captor
dev = adafruit_dht.DHT22(board.D4, use_pulseio=False)
matrix11x7 = Matrix11x7()


class Img():
    """
    Class to specify the parameters of an Image take
    """

    def __init__(self, name, iso, time_exp, light, bin):
        self.name = name
        self.iso = iso
        self.time_exp = time_exp * 1000000
        self.light = light
        self.what = bin

    def get_all(self):
        """
        return all the parameters of this class
        :return:
        """
        return {'name': self.name, 'iso': self.iso, 'exp': self.time_exp, 'light': self.light, 'what': self.what}


class Sequence():
    """
    Class to set all parameters of a sequence of image
    """

    def __init__(self, dir, name, delta, nb_total, normal, lumi, csv_name):
        self.name = name
        self.dirname = dir + "/" + name
        self.delta = delta
        self.nb_total = nb_total
        self.normal = normal
        self.lumi = lumi
        self.temp = csv_name

    def get_all(self):
        """
        return all the parameters of this class
        :return:
        """
        return {'dir': self.dirname, 'name': self.name, 'delta': self.delta, 'total': self.nb_total,
                'normale': self.normal.get_all(),
                'lumi': self.lumi.get_all(), 'csv': self.temp}

    def clean_dir(self):
        """
        Clear the directory if same name as the experience and remake it
        :return:
        """
        if os.path.exists(self.dirname):  # si le dossier existe déjà, on le supprime
            shutil.rmtree(self.dirname)
        os.makedirs(self.dirname)  # on crée le dossier

    def launch_seq(self):
        """
        Launch the image take sequence
        :return:
        """
        if self.delta < (3 * self.lumi.time_exp / 1000000):
            self.delta = 3 * self.lumi.time_exp / 1000000
        for p in range(self.nb_total):
            cur_dir = self.dirname + '/time' + str(p) + "/"
            os.makedirs(cur_dir)
            date = datetime.now()
            date_next = date + timedelta(seconds=self.delta)
            print(date)
            # prise photo #
            take_pict(self.normal, cur_dir)
            take_pict(self.lumi, cur_dir)
            with open(self.dirname + "/" + self.temp, 'w') as f:
                f.write("time" + "\t" + "temp °c" + "\t" + "humidity" + "\n")
            # prise temperature temp \t humi \t time
            succes = False
            nb_try = 1
            while succes == False and nb_try < 5:
                print("Try n° "+str(nb_try)+" ...")
                while True:
                    try:
                        temp_c = dev.temperature
                        hum = dev.humidity
                        now = datetime.now()
                        cur = now.strftime("%H:%M:%S")
                        print("Succes", str(cur), temp_c, hum)
                        with open(self.dirname + "/" + self.temp, 'a') as f:
                            f.write(str(cur) + "\t" + str(temp_c) + "\t" + str(hum) + "\n")
                        succes = True
                        break
                    except:
                        print("Fail")
                        break
                nb_try += 1

            print("continued")
            # calcul delta restant
            delta2 = date_next - datetime.now()
            time.sleep(delta2.total_seconds())
            print('ok delta :', date, date.now(), self.delta)
        print("Seq ended")


def take_pict_norm():
    """
    Caled by button preview in normal parameter part
    Take a picture with the parameter saved as normal.
    Display the picture
    :return:
    """
    test = Img('test.png', 1, exp_norm.get(), led_norm.get(), False)
    print(test.get_all())
    take_pict(test, '')
    img = Image.open('test.png')
    img.show()
    print("normal preview picture done")


def take_pict_lumi():
    """
    Caled by button preview in luminescence parameter part
    Take a picture with the parameter saved as luminescence.
    Display the picture
    :return:
    """
    test = Img('test.png', iso_lumi.get(), exp_lumi.get(), led_lumi.get(), True)
    print(test.get_all())
    take_pict(test, '')
    img = Image.open('test.png')
    img.show()
    print("luminescence preview picture done")


def preview():
    """
    Caled by preview button in general window.
    Set led as set in led_global slider.
    Open the preview of PiCamera.
    Close preview when keys CTRL+S are pressed
    :return:
    """
    led = led_global.get()
    cmd = ["libcamera-still", "-t", "0", ]
    print(cmd)
    set_led(led)
    subprocess.call(cmd)
    set_led(0)


def select_file():
    """
    Open filedialog to choose a destination directory for the experiment.
    :return:
    """
    dest_path.set(filedialog.askdirectory(title="Select a directory"))
    print(dest_path.get())
    label_dest.config(text="Selected folder : " + dest_path.get())


def start_seq():
    """
    Set Img object from function.py for luminescence parameters and light parameters
    Set Sequence object from function.py with parameters choose
    Launch sequence
    :return:
    """
    lumi = Img('lumi.png', iso_lumi.get(), exp_lumi.get(), led_lumi.get(), True)
    normal = Img('normal.png', 1, exp_norm.get(), led_norm.get(), False)
    Seq = Sequence(dest_path.get(), nom.get(), deltavar.get(), nb_tot.get(), normal, lumi, csvvar.get())
    print(Seq.get_all())
    Seq.launch_seq()


root = Tk()
root.geometry('800x800')
root.title("FIAT LUX camera control")

# Sequence settings
seq = Frame(root, highlightthickness=2, highlightbackground='darkgreen')
seq.pack(fill=X, padx=40, pady=20)
label = Label(seq, text="Experiment name:")
label.pack()
nom = StringVar()
nom.set("")
entree = Entry(seq, textvariable=nom, width=30)
entree.pack()
label = Label(seq, text="Time delta between 2 takes:")
label.pack()
deltavar = IntVar()
deltavar.set("")
delta = Entry(seq, textvariable=deltavar, width=30)
delta.pack()
label = Label(seq, text="CSV name for temperature and humidity:")
label.pack()
csvvar = StringVar()
csvvar.set(".csv")
csv = Entry(seq, textvariable=csvvar, width=30)
csv.pack()
nb_tot = Scale(seq, from_=1, to=50, orient=HORIZONTAL, label='Number of sequences:', length=300, tickinterval=10)
nb_tot.pack()

dest_path = StringVar()
button = Button(seq, text="Select a destination folder", command=select_file)
button.pack(ipadx=5, pady=15)
label_dest = Label(seq, text="Destination directory: ??????")
label_dest.pack()

led_global = Scale(root, from_=0, to=100, orient=HORIZONTAL, label='Light (%)', length=300, tickinterval=25)
led_global.pack()
button = Button(root, text="Livestream preview", command=preview)
button.pack()
button = Button(root, text="Launch", command=start_seq)
button.pack()

# Luminescence window
lumi = Frame(root, highlightthickness=2, highlightbackground='darkgreen')
lumi.pack(side=LEFT, padx=20, pady=20)
label_lumi = Label(lumi, text="Luminescence picture :")
label_lumi.pack()
iso_lumi = Scale(lumi, from_=1, to=500, orient=HORIZONTAL, label='ISO', length=300, tickinterval=100)
iso_lumi.pack()
exp_lumi = Scale(lumi, from_=0, to=230, orient=HORIZONTAL, label='Exposition (sec)', length=300, tickinterval=20)
exp_lumi.pack()
led_lumi = Scale(lumi, from_=0, to=100, orient=HORIZONTAL, label='Light (%)', length=300, tickinterval=25)
led_lumi.pack()
button_lumi = Button(lumi, text="Luminescence preview", command=take_pict_lumi)
button_lumi.pack()

# Light window
light = Frame(root, highlightthickness=2, highlightbackground='darkgreen')
light.pack(side=RIGHT, padx=20, pady=20)
label_norm = Label(light, text="Normal picture:")
label_norm.pack()
exp_norm = Scale(light, from_=0, to=6, orient=HORIZONTAL, label='Exposition (sec)', resolution=0.1, length=300,
                 tickinterval=20)
exp_norm.pack()
led_norm = Scale(light, from_=0, to=100, orient=HORIZONTAL, label='Light (%)', length=300, tickinterval=25)
led_norm.pack()
button_normal = Button(light, text="Normal preview", command=take_pict_norm)
button_normal.pack()



if __name__ == "__main__":
    root.mainloop()
