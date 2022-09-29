


import urequests          # library used for making HTTP requests
from time import sleep, time, ticks_ms, ticks_diff, sleep_ms
from machine import ADC
from machine import Pin
from hcsr04 import HCSR04
import json
import network
from machine import Timer, PWM
from dcmotor import DCMotor

server_url = "http://192.168.0.101:5000"

TURN_ON_INPUT = Pin(5, Pin.IN, Pin.PULL_DOWN)

LED_RED = Pin(22, Pin.OUT)
LED_GREEN = Pin(23, Pin.OUT)

DISTANCE_TRIG = 27
DISTANCE_READ = 14

MOTOR_PIN_1 = Pin(17, Pin.OUT)
MOTOR_PIN_2 = Pin(12, Pin.OUT)
MOTOR_PIN_3 = PWM(Pin(13)) 

MOTOR_SPEED = 25
USUAL_DISTANCE = 50

motor = DCMotor(MOTOR_PIN_1, MOTOR_PIN_2, MOTOR_PIN_3)
sensor = HCSR04(trigger_pin=33, echo_pin=2)
distance = sensor.distance_cm()
print('Distance: ', distance, 'cm')


tim_get = Timer(0)
tim_sensor = Timer(1)

  
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('TP-Link_3168', '73178170')
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan.ifconfig()[0]

def get_packet_info():
  
  print("Sending a GET request to server")
  response = urequests.get(server_url + '/delivery') # make a GET request to the url
  #print([attr for attr in dir(response) if not attr.startswith('__')])
  
  response_json = response.json()
  response.close()
  print("GOT RESPONSE")
  #print(response_json)
  
  incoming_delivery = response_json['start_delivery']
  return incoming_delivery

def start_track():
  global motor
  global MOTOR_SPEED
  
  motor.forward(MOTOR_SPEED)

  
  return
  
def measure_box():
  global sensor
  global USUAL_DISTANCE
  global MOTOR_SPEED
  #print("WAITING FOR BOX")
  #wait for box
  #while sensor.distance_cm() >= USUAL_DISTANCE:
  #  print("usual distance: {0}, current distance: {1}".format(USUAL_DISTANCE, sensor.distance_cm()))
  #  sleep_ms(10)
    
  box_distance = sensor.distance_cm()
  print("MEASURING BOX")
  #measure box
  time_start = ticks_ms()
  while abs(sensor.distance_cm()) < USUAL_DISTANCE:
    print("usual distance: {0}, current distance: {1}".format(USUAL_DISTANCE, sensor.distance_cm()))
    sleep_ms(10)
    
  time_end = ticks_ms()
  box_size = (int(ticks_diff(time_end, time_start)) * 1000) * MOTOR_SPEED # s = v*t; no idea what the unit of this value is, since MOTOR_SPEED is arbitrary

  print("BOX SIZE IS {0}".format(box_size))
  
  return box_size, True

  
def send_box_size_to_server(box_id, box_size):
  
  response = urequests.post(server_url + '/box_info', json={"box_id":box_id, "size":box_size})
  response_json = response.json()
  response.close()
  if response_json['all_good'] == True:
    print("Server updated!")
  else:
    print("Error occurred!")
  
def main_work():
  global sensor
  global USUAL_DISTANCE
  global motor

  global MOTOR_SPEED

  start_track()

  LED_GREEN.value(1)

  #delivery_info = get_packet_info()
  
  start_flag = True
  while True:
    
    # READ PACKET SIZe
    if sensor.distance_cm() < USUAL_DISTANCE and start_flag:
      start_flag = False
      packet_size, flag = measure_box()
      start_flag = True

      packet_id = "123456"
      send_box_size_to_server(packet_id, packet_size)  
  
  motor.forward(0)
  return

  
do_connect()

while True:
  delivery_info = get_packet_info()
  sleep(1)
  print(delivery_info)
  if delivery_info:
    main_work()

#TURN_ON_INPUT.irq( trigger = Pin.IRQ_RISING, handler = main_work )




