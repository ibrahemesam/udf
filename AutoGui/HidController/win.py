from win32con import (
    WM_LBUTTONDOWN, MK_LBUTTON, WM_LBUTTONUP,
    WM_MBUTTONDOWN, MK_MBUTTON, WM_MBUTTONUP,
    WM_RBUTTONDOWN, MK_RBUTTON, WM_RBUTTONUP,
    WM_KEYDOWN, WM_KEYUP
    )
from win32api import MAKELONG, PostMessage, SendMessage

def mouse_click_left(hwnd, x, y):
    x = int(x); y = int(y)
    lParam = MAKELONG(x, y)
    PostMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lParam)
    PostMessage(hwnd, WM_LBUTTONUP, None, lParam)
    
def mouse_click_middle(hwnd, x, y):
    x = int(x); y = int(y)
    lParam = MAKELONG(x, y)
    PostMessage(hwnd, WM_MBUTTONDOWN, MK_MBUTTON, lParam)
    PostMessage(hwnd, WM_MBUTTONUP, None, lParam)
    
def mouse_click_right(hwnd, x, y):
    x = int(x); y = int(y)
    lParam = MAKELONG(x, y)
    PostMessage(hwnd, WM_RBUTTONDOWN, MK_RBUTTON, lParam)
    PostMessage(hwnd, WM_RBUTTONUP, None, lParam)

def send_key(hwnd, key):
    key = ord(key.lower())
    SendMessage(hwnd, WM_KEYDOWN, key, 0)
    SendMessage(hwnd, WM_KEYUP, key, 0)
    
def send_string(hwnd, string):
    for char in string:
        send_key(hwnd, char)
        
class Controller:
    def __init__(self, hwnd) -> None:
        self.hwnd = hwnd
        
    def send_key(self, key):
        send_key(self.hwnd, key)
        
    def send_string(self, string):
        send_string(self.hwnd, string)
        
    def mouse_click_left(self, x = 0, y = 0):
        mouse_click_left(self.hwnd, x, y)
        
    def mouse_click_middle(self, x = 0, y = 0):
        mouse_click_middle(self.hwnd, x, y)
        
    def mouse_click_right(self, x = 0, y = 0):
        mouse_click_right(self.hwnd, x, y)