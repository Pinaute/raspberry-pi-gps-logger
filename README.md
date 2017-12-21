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

TODO

## Acknowledgements
Based on [martinohanlon/pelmetcam/pelmetcam.py](https://github.com/martinohanlon/pelmetcam/blob/master/pelmetcam.py). 

## License
MIT License. See the [LICENSE file](LICENSE) for details.
