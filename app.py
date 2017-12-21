#!/usr/bin/python

import RPi.GPIO as GPIO
from serial import Serial
import time
import threading
import os
import sys

# BUTTON
BUTTON_GPIO_PIN = 4
SHORT_PRESS_TICKS = 5
LONG_PRESS_TICKS = 200
TICK_TIME = 0.01
DOWN = 0

# LED
LED_GPIO_PIN = 18
SLOW_FLASH_TIMES = [1,1]
FAST_FLASH_TIMES = [0.2,0.2]

# Global Navigation Satellite System (GNSS): GPS, GLONASS, Galileo, ... 
BAUDRATE = 9600
PORT = '/dev/ttyAMA0'

class ButtonControl(threading.Thread):
	class ButtonPressStates():
		NOTPRESSED = 0
		SHORTPRESS = 1
		LONGPRESS = 2
		
	def __init__(self, gpio_pin):
		threading.Thread.__init__(self)
		self.gpio_pin = gpio_pin
		self.__current_state = self.ButtonPressStates.NOTPRESSED
		self.shortPressTicks = SHORT_PRESS_TICKS
		self.longPressTicks = LONG_PRESS_TICKS
		self.tickTime = TICK_TIME
		GPIO.setup(self.gpio_pin, GPIO.IN)
		
	def get(self):
		return GPIO.input(self.gpio_pin)
	
	def is_pressed(self):
		buttonPressed = False
		if GPIO.input(self.gpio_pin) == DOWN: 
			buttonPressed = True
		return buttonPressed
	
	def run(self):
		self.__running = True
		self.__current_state = self.ButtonPressStates.NOTPRESSED
		
		while self.is_pressed(): 
			time.sleep(self.tickTime)
		
		while self.__running:
			while self.is_pressed() == False and self.__running:
				time.sleep(self.tickTime)
			ticks = 0
			while self.is_pressed() == True and self.__running:
				ticks += 1
				time.sleep(self.tickTime)
			if ticks > self.shortPressTicks and ticks < self.longPressTicks:
				self.__current_state = self.ButtonPressStates.SHORTPRESS
			if ticks >= self.longPressTicks:
				self.__current_state = self.ButtonPressStates.LONGPRESS
			time.sleep(0.5)
			
	def get_state(self):
		return self.__current_state
	
	def set_not_pressed(self):
		self.__current_state = self.ButtonPressStates.NOTPRESSED
		
	def stopController(self):
		self.__running = False
		
class GnssControl(threading.Thread):
	class GnssStates():
		STOP = 0
		PAUSE = 1 
		RECORD = 2

	def __init__(self):
		threading.Thread.__init__(self)
		self.__running = False
		self.__current_state = self.GnssStates.STOP
		self.serialGnss = Serial()
		self.serialGnss.baudrate = BAUDRATE
		self.serialGnss.port = PORT
		self.serialGnss.timeout = 4
		self.serialGnss.open()
		self.fileDescriptor = open('/home/pi/track-%s.nmea' %time.strftime('%Y%m%d%H%M%S'), 'a')

	def set_stopped(self):
		self.__current_state = self.GnssStates.STOP
		self.__running = False
		self.fileDescriptor.close()

	def set_paused(self):
		self.__current_state = self.GnssStates.PAUSE
		
	def run(self):
		self.__running = True
		while self.__running:
			sentence = self.serialGnss.readline()
			sentenceStr = str(sentence)
			if self.__current_state == self.GnssStates.RECORD:
				if(sentence.find('$GP') > 0):
					self.fileDescriptor.write('{0:}'.format(sentenceStr))

	def set_recording(self):
		self.__current_state = self.GnssStates.RECORD
		
	def get_state(self):
		return self.__current_state
		
class LedControl():           
	class LedStates():
		OFF = 0
		ON = 1
		SLOW_FLASH = 2
		FAST_FLASH = 3

	def __init__(self, gpio_pin):
		self.__current_state = self.LedStates.OFF
		self.__current_led_state = False
		self.gpio_pin = gpio_pin
		GPIO.setup(self.gpio_pin, GPIO.OUT)
		self.__set_off()
		
	def __set_off(self):
		self.__current_led_state = False
		GPIO.output(self.gpio_pin, False)
		
	def __set_on(self):
		self.__current_led_state = True
		GPIO.output(self.gpio_pin, True)
		
	def __flash(self, time_on, time_off):       
		while ((self.get_state() == self.LedStates.SLOW_FLASH) or (self.get_state() == self.LedStates.FAST_FLASH)) :
			if self.__current_led_state == True:
				self.__set_off()
				time.sleep(time_off)
			else:
				self.__set_on()
				time.sleep(time_on)
	
	def set_on(self):
		self.__current_state = self.LedStates.ON
		self.__set_on()
		
	def set_off(self):
		self.__current_state = self.LedStates.OFF
		self.__set_off()
	   
	def set_slow_flash(self):
		self.__current_state = self.LedStates.SLOW_FLASH
		self.__time_on = SLOW_FLASH_TIMES[0]
		self.__time_off = SLOW_FLASH_TIMES[1]
		self.__flashthread = threading.Thread(target=self.__flash, args=(self.__time_on, self.__time_off))
		self.__flashthread.start()
	
	def set_fast_flash(self):
		self.__current_state = self.LedStates.FAST_FLASH
		self.__time_on = FAST_FLASH_TIMES[0]
		self.__time_off = FAST_FLASH_TIMES[1]
		self.__flashthread = threading.Thread(target=self.__flash, args=(self.__time_on, self.__time_off))
		self.__flashthread.start()
		
	def get_state(self):
		return self.__current_state
	
if __name__ == "__main__":
	try:
		GPIO.setmode(GPIO.BCM)
		
		button = ButtonControl(BUTTON_GPIO_PIN)
		button.start()
		
		gnss = GnssControl()
		gnss.start()
		
		led = LedControl(LED_GPIO_PIN)
		led.set_fast_flash()
		
		while(button.get_state() != button.ButtonPressStates.LONGPRESS):
			if (button.get_state() == button.ButtonPressStates.SHORTPRESS):
				if(gnss.get_state() == gnss.GnssStates.STOP):
					led.set_on()
					gnss.set_recording()
				elif (gnss.get_state() == gnss.GnssStates.RECORD):
					led.set_slow_flash()
					gnss.set_paused()
				elif (gnss.get_state() == gnss.GnssStates.PAUSE):
					led.set_on()
					gnss.set_recording()
				button.set_not_pressed()
				
	except KeyboardInterrupt:
		print "User Cancelled (Ctrl C)"
			
	except:
		print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
		raise
		
	finally:
		button.stopController()
		button.join()
		led.set_off()
		gnss.set_stopped()
		gnss.join()
		GPIO.cleanup()
