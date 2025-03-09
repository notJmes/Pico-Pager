'''
Author: Samuel Seah

Description:

Find ST7789 dependencies at https://github.com/russhughes/st7789py_mpy
Custom-made function wrap() for text wrap and handling of new-line (\n) characters
'''

import time
import machine
import network
import st7789py as st7789
import vga2_16x16 as font

import uasyncio as asyncio
from utelegram import TelegramBot

led = machine.Pin('LED', machine.Pin.OUT)

Token = 'YOUR TOKEN'
SSID = 'WIFI NAME'
PASSWORD = 'WIFI PASSWORD'
GMT = 8
SPI_X = 240
SPI_Y = 240

spi = machine.SPI(0, baudrate=30000000, polarity=1, sck=machine.Pin(18), mosi=machine.Pin(19))
display = st7789.ST7789(spi, SPI_X, SPI_Y, reset=machine.Pin(21, machine.Pin.OUT), dc=machine.Pin(20, machine.Pin.OUT))

def wrap(text, split=15, x=0, y=0, clear=True):
    counter = 0
    if clear:
        display.fill(0)
    for chunk in text.split('\n'):
        
        lst = []
        tmp = ''
        for word in chunk.split(' '):
            if len(tmp+' '+word) > split:
                lst.append(tmp)
                tmp = word
            else:
                tmp += word if not len(tmp) else ' '+word
            if len(tmp) > split:
                lst.append(tmp[:split-1]+'-')
                tmp = tmp[split-1:]
        lst.append(tmp)
        
        if not lst:
            counter += 1
        else:
            for line in lst:
                display.text(font, line, x, round(y+counter*20))
                counter += 1
        
        
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    counter = 0
    
    while wlan.isconnected() == False:
        wrap(f'Waiting for\nconnection ({counter}s)', clear=False)
        time.sleep(1)
        counter += 1
        led.toggle()
    ip = wlan.ifconfig()[0]
    wrap(f'Your IP is {ip}\n\nListening for new messages...')

def display_message(bot,msg_type,chat_name,sender_name,chat_id,text,entry):
    
    date = time.localtime(entry['message']['date'])
    fname = entry['message']['chat']['first_name']
    year, month, day, hour, minute, second, *others = date
    hour += GMT
    wrap(f"{day:02d}/{month:02d}/{year-2000:02d} {hour:02d}:{minute:02d}\n{fname}:\n\n{text}")
    bot.send(chat_id, "Sending your message to Sam! - Sam's pager 👾")
    for i in range(10):
        led.toggle()
        time.sleep(0.1)
    led.off()
    
led.off()
connect()
bot = TelegramBot(Token,display_message)
asyncio.create_task(bot.run())
loop = asyncio.get_event_loop()
loop.run_forever()


