# Data logger for Raspberry

The objective of this project is to record raw NMEA frames from a GPS receive card.  
I made the choice of a minimalist interface with a red led and a push button.  
This program deals with parallel programming in Python.  

![Overview](/img/overview.jpg)

## 1 Hardware

### 1.1 Equipments

What you will need:

Schematic ref | Description  | Value
---           | ---          | --- 
J1            | raspberry pi |
J2            | neo6m module |
SW1           | push button  |
D1            | led 5mm      |
C1            | capacitor    | 100 nF
R1            | resistor     | 10 kohm
R2            | resistor     | 1 kohm
R3            | resistor     | 330 ohm

![Knolling](/img/knolling.jpg)

### 1.2 Wiring the GPS to the RPI

You have to be careful about RX and TX connections:

* connect the TX pin of the GPS to the RX pin of the RPI.
* connect the RX pin of the GPS to the TX pin of the RPI.

![Wiring](/img/wiring.png)

### 1.3 Overview of the electronic schema

*Resistance value for LED mounting:*  
It is commonly accepted that the standard LEDs work well with a resistance 100 times higher than the supplied voltage.   
So I use in my assembly a resistance of 330ohm, for a voltage of 3.3 V  

*Mounting the push button:*  
The pull-up resistors allows to have a clear high or low voltage so that the RPI can read the input value unambiguously.  

*The capacitor:*  
When pressing the button there is a creation of interference signals induced, so we add a capacitor to improve the quality of the push button signal.  
When the button is pressed, the capacitor discharges in a controlled manner and thus the signal is filtered.  

*Protection resistors:*  
The GPIO 4 pin can be initialized in the program as an output or as an input.  
The purpose of the protection resistor is to protect the GPIO pin if it is accidentally set as an output rather than as an input.  

![Schema](/img/schema.jpg)

## 2 Software

### 2.1 Dependencies

* python 2.7
* python-serial

### 2.2 Installation

To launch the application on startup: 

* copy the file `app.py` to the directory `/home/pi/`
* create a file `raspberry-pi-gps-logger.service` to the directory `/lib/systemd/system/`
* run the following command lines: `systemctl start raspberry-pi-gps-logger` and `systemctl enable raspberry-pi-gps-logger`

File `raspberry-pi-gps-logger.service`:
```
[Unit]
Description=Data recorder
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python /home/pi/app.py

[Install]
WantedBy=multi-user.target
```

### 2.3 Usage

* when starting the program the LED flashes fast, the program waiting for an action on the push button.
* a short press on the push button:
* * triggers the recording of NMEA frames, the LED remains on
* * or pauses the recording, the LED flashes slowly
* a long press on the push button stops the program
* to restart the program you must restart the raspberry pi

To view the recorded data, you need to convert the `.nmea` to `.gpx`  
You can use the following command:  
`gpsbabel -i nmea -f file-in.nmea -o gpx -F file-out.gpx`

## Acknowledgements
Based on [martinohanlon/pelmetcam/pelmetcam.py](https://github.com/martinohanlon/pelmetcam/blob/master/pelmetcam.py). 

## License
MIT License. See the [LICENSE file](LICENSE) for details.
