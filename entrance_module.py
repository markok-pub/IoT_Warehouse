


from mfrc522 import MFRC522
from machine import Pin, SoftSPI, Timer, PWM
import urequests
from hcsr04 import HCSR04
import network
from time import sleep, sleep_ms
import ujson

SERVER_ADDRESS = 'http://192.168.0.101:5000'

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

redLed = Pin(33, Pin.OUT)
greenLed = Pin(12, Pin.OUT)
redLedSmall = Pin(32, Pin.OUT)

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)

sda = Pin(5, Pin.OUT)

spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
spi.init()
rdr = MFRC522(spi=spi, gpioRst=22, gpioCs=5)

sensor = HCSR04(trigger_pin=13, echo_pin=17)
#switch = Pin(5, Pin.IN, Pin.PULL_UP)
tim0 = Timer(0)
motor = Pin(2, Pin.OUT)
door = PWM(motor)
door.freq(50)
door.duty(20)

usual_distance = 100 # cm

redLed.on()
  
def open_door():
  door.duty(20)
  sleep_ms(333)
  door.duty(0)
  print("opening door...")
  
def close_door():
  door.duty(20)
  sleep_ms(333)
  door.duty(0)
  print("closing door...")

def start_sorting():
  response = urequests.post(SERVER_ADDRESS + '/delivery', json={"start_working":True})
  response.close()
  redLedSmall.on()
  print("starting sorting...")
  sleep(1)
  redLedSmall.off()
  redLed.on()
  
def dummy_response_json():
  dummy_set = {"delivery_people": ["123", "asd", "dummy", "yeet", "0x9952e7b9"]}

  return ujson.loads(ujson.dumps(dummy_set))

  
def stop():
  response = urequests.post(SERVER_ADDRESS + '/delivery', json={"start_working":False})
  response.close()
  
  redLed.off()
  greenLed.off()
  redLedSmall.off()
  

def do_read():
  print("Place card")
  while True:
      
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
      (stat, raw_uid) = rdr.anticoll()
      if stat == rdr.OK:
        card_id = "0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
        print(card_id)
        return card_id
  
def check_distance(Pin):
  distance = sensor.distance_cm()
  print("Distance is {}".format(distance))
  if distance < usual_distance:
    print("Getting delivery people RFIDs...")
    response = urequests.get(SERVER_ADDRESS + '/delivery_people')
    #sleep(1)
    print("GOT DELIVERY PEOPLE: {0}".format(response))
    response_json = response.json()
    
    response.close()
    #response_json = dummy_response_json()
    
    rfid_read = do_read()
    
    if rfid_read in response_json['delivery_people']:
      greenLed.on()
      redLed.off()
      open_door()
      start_sorting()
    sleep(2)
    stop()

do_connect()
# switch.irq(trigger = Pin.IRQ_RISING, handler = check_distance)
tim0.init(period = 5000, mode = Timer.PERIODIC, callback = check_distance)


