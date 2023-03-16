from Xlib.protocol.event import KeyPress, KeyRelease, ButtonPress, ButtonRelease
from .. import display, get_window_by_id, NONE

def is_shifted(ch) :
    if ch.isupper() :
        return True
    if ch in "~!@#$%^&*()_+{}|:\"<>?":
        return True
    return False

def send_string(window, string, x = 0, y = 0):
    for char in string:
        if is_shifted(char):
            send_key(window, char, x, y, shift_mask = 1)
        else:
            send_key(window, char, x, y, shift_mask = 0)

def send_key(window, key, x = 0, y = 0, shift_mask = 0):
    # NB: this function is to send a single key
    #     to send a string that contains (capital letters, arabic letters): use selenium send_keys
    # FIXME: this function can't Unicode characters. it only sends ASCII
    keycode = display.keysym_to_keycode(ord(key))
    window.send_event(KeyPress(
        time = 0,
        root = window,
        window = window,
        same_screen = 0, child = NONE,
        root_x = x, root_y = y, event_x = x, event_y = y,
        state = shift_mask,
        detail = keycode,
        ), propagate = True)
    window.send_event(KeyRelease(
        time = 0,
        root = window,
        window = window,
        same_screen = 0, child = NONE,
        root_x = x, root_y = y, event_x = x, event_y = y,
        state = shift_mask,
        detail = keycode,
        ), propagate = True)
    display.sync()

def mouse_click(window, button, x = 0, y = 0, shift_mask = 1):
    # FIXME: if window is not hidden: window will be activated
    # @button: 1 => left;   2 => middle;    3 => right
    x = int(x); y = int(y)
    window.send_event(ButtonPress(
        time = 0,
        root = window,
        window = window,
        child = NONE,
        same_screen = 0,
        root_x = x, root_y = y, event_x = x, event_y = y,
        state = shift_mask,
        detail = button,
        ))#, propagate = True)
    window.send_event(ButtonRelease(
        time = 0,
        root = window,
        window = window,
        same_screen = 0, child = NONE,
        root_x = x, root_y = y, event_x = x, event_y = y,
        state = shift_mask,
        detail = button,
        ))#, propagate = True)
    display.sync()

def mouse_click_left(window, x = 0, y = 0, shift_mask = 0):
    mouse_click(window, 1, x, y, shift_mask)
    
def mouse_click_middle(window, x = 0, y = 0, shift_mask = 0):
    mouse_click(window, 2, x, y, shift_mask)
    
def mouse_click_right(window, x = 0, y = 0, shift_mask = 0):
    mouse_click(window, 3, x, y, shift_mask)

class Controller:
    def __init__(self, hwnd) -> None:
        self.window = get_window_by_id(hwnd)
        
    def send_key(self, key):
        send_key(self.window, key)
        
    def send_string(self, string):
        send_string(self.window, string)
        
    def mouse_click_left(self, x = 0, y = 0, count = 1):
        for i in range(count):
            mouse_click(self.window, 1, x, y)
        
    def mouse_click_middle(self, x = 0, y = 0):
        mouse_click(self.window, 2, x, y)
        
    def mouse_click_right(self, x = 0, y = 0):
        mouse_click(self.window, 3, x, y)
        

if __name__ == '__main__':
    import time
    window_id = 0x400005
    window = get_window_by_id(window_id)
    # print(dir(window))
    # time.sleep(2)
    # send_key(window, arabic.XK_Arabic_sheen)
    # send_string(window, 'Ibrahem')
    # print(window.get_wm_state())
    # window.unmap()
    # while 1:
    time.sleep(3)
    # window.map()
    mouse_click(window, 1)
    # import pyautogui
    # pyautogui.write('H')      

