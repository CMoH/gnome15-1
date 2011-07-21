#        +-----------------------------------------------------------------------------+
#        | GPL                                                                         |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) Brett Smith <tanktarta@blueyonder.co.uk>                      |
#        |                                                                             |
#        | This program is free software; you can redistribute it and/or               |
#        | modify it under the terms of the GNU General Public License                 |
#        | as published by the Free Software Foundation; either version 2              |
#        | of the License, or (at your option) any later version.                      |
#        |                                                                             |
#        | This program is distributed in the hope that it will be useful,             |
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |
#        | GNU General Public License for more details.                                |
#        |                                                                             |
#        | You should have received a copy of the GNU General Public License           |
#        | along with this program; if not, write to the Free Software                 |
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |
#        +-----------------------------------------------------------------------------+

from ctypes import *
from threading import Thread
libg15 = cdll.LoadLibrary("libg15.so.1")

G15_LCD = 1
G15_KEYS = 2
G15_DEVICE_IS_SHARED = 4
G15_DEVICE_5BYTE_RETURN = 8
G15_DEVICE_G13 = 16
G15_DEVICE_G510 = 32

G15_KEY_READ_LENGTH = 9
G510_STANDARD_KEYBOARD_INTERFACE = 0x0

# Error codes
G15_NO_ERROR = 0
G15_ERROR_OPENING_USB_DEVICE = 1
G15_ERROR_WRITING_PIXMAP = 2
G15_ERROR_TIMEOUT = 3
G15_ERROR_READING_USB_DEVICE = 4
G15_ERROR_TRY_AGAIN = 5
G15_ERROR_WRITING_BUFFER = 6
G15_ERROR_UNSUPPORTED = 7

# Debug levels
G15_LOG_INFO = 1
G15_LOG_WARN = 0

class KeyboardReceiveThread(Thread):
    def __init__(self, callback):
        Thread.__init__(self)
        self._run = True
        self.name = "KeyboardReceiveThread"
        self.callback = callback
        
    def deactivate(self):
        if self._run:
            self._run = False
        
    def run(self):      
        pressed_keys = c_int(0)
        try:
            while self._run:
                err = libg15.getPressedKeys(byref(pressed_keys), 50)
                if err == G15_NO_ERROR:
                    print "Pressed %d" % pressed_keys.value
                    self.callback(pressed_keys.value)
#                elif err != G15_ERROR_TRY_AGAIN:
#                    raise Exception("Failed waiting for key. Error code %d" % err)
        finally:
            self._run = True
        print "Thread left"

class libg15_devices_t(Structure):
    _fields_ = [ ("name", c_char_p),
                 ("vendorid", c_int),
                 ("productid", c_int),
                 ("caps", c_int) ]
    
def grab_keyboard(callback):
    """
    Start polling for keyboard events. Device must be initialised. The thread
    returned can be stopped by calling deactivate().
    """
    t = KeyboardReceiveThread(callback)
    t.start()
    return t
    
def init(init_usb = True):
    """
    This one return G15_NO_ERROR on success, something
    else otherwise (for instance G15_ERROR_OPENING_USB_DEVICE
    """
    if init_usb:
        return libg15.initLibG15()
    else:
        return libg15.initLibG15NoUSBInit()

def reinit():
    """ re-initialise a previously unplugged keyboard ie ENODEV was returned at some point """
    return libg15.re_initLibG15()
    

def exit():
    return libg15.exitLibG15()

def set_debug(level):
    """
    Keyword arguments:
    level        -- level, one of G15_LOG_INFO or G15_LOG_WARN
    """
    libg15.libg15Debug(level)
    
def write_pixmap(data):
    libg15.writePixmapToLCD(data)
    
def set_contrast(level):
    print "Setting contrast to %d" % level
    return libg15.setLCDContrast(level)
    
def set_leds(leds):
    return libg15.setLEDs(leds)
    
def set_lcd_brightness(level):
    return libg15.setLCDBrightness(level)
    
def set_keyboard_brightness(level):
    return libg15.setKBBrightness(level)
    
def set_keyboard_color(color):
    return libg15.setG510LEDColor(color[0], color[1], color[2])



def __handle_key(code):
    print "Got %d" %code

# run it in a gtk window
if __name__ == "__main__":
    set_debug(G15_LOG_INFO)
    if init() != G15_NO_ERROR:
        raise Exception("Failed to initialise libg15")
    import time
    grab_keyboard(__handle_key).run()
    while True:
        for x in range(0, 16):
            set_leds(x)
            time.sleep(1.0)
        for j in range(0, 3):
            set_keyboard_brightness(j)
            time.sleep(1.0)
