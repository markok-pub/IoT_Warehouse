from machine import Pin, Timer
from time import sleep
import network
import urequests

SERVER_ADDRESS = 'http://192.168.0.101:5000'

greenLED = Pin(10, Pin.OUT)

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

# slot number is same as the pin number (ugly af but simple)
def get_slot(pin):
  return str(pin)[4:-1]
  
def is_occupied(slot):
  request_url = SERVER_ADDRESS + '/slot_check/' + str(slot)
  print(request_url)
  response = urequests.get(request_url)
  sleep(0.5)
  response_json = response.json()
  response.close()
  return response_json['occupied']
  
# statuses should be OCCUPIED and FREE, but they aren't checked (yet)
def set_slot_status(slot, status):
  response = urequests.post(SERVER_ADDRESS + '/slot_update', json={"slot":slot, "status":status})
  sleep(0.5)
  response_json = response.json()
  response.close()
  return response_json['success'] # i imagine this be a boolean field or sth

# detects free spaces on bootup
def detect_slot(Pin):
  global greenLED
  slot = get_slot(Pin)
  if is_occupied(slot):
    greenLED.on()
    set_slot_status(slot, 'FREE')
  else:
    greenLED.off()
    set_slot_status(slot, 'OCCUPIED')
    
    
do_connect()
move = machine.Pin(9, machine.Pin.IN, machine.Pin.PULL_UP)
move.irq(trigger = machine.Pin.IRQ_RISING, handler = detect_slot)