from .. import get_window_by_id, ZPixmap
from . import frombytes, frombuffer, uint8

class WinCap:
    def __init__(self, hwnd) -> None:
        self.window = get_window_by_id(hwnd)
        self.renew_size()
        
    def grab(self):
        return frombuffer(
            self.grap_raw(), uint8
            ).reshape(self.height, self.width, 4)
    
    def grab_pil(self):
        return frombytes("RGB", (self.width, self.height), self.grap_raw(), "raw", "BGRX")
    
    def grap_raw(self):
        return self.window.get_image(0, 0, self.width, self.height, ZPixmap, 0xffffffff).data
    
    def renew_size(self):
        gm = self.window.get_geometry()
        self.width, self.height = gm.width, gm.height
        