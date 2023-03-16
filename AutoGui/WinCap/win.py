from .. import atexit
from . import frombytes, frombuffer, uint8
from win32gui import FindWindow, GetClientRect, GetWindowDC, DeleteObject, ReleaseDC
from win32ui import CreateDCFromHandle, CreateBitmap
PrintWindow = __import__('ctypes').windll.user32.PrintWindow

class WinCap:
    def __init__(self, hwnd) -> None:
        self.hwnd = hwnd
        self.renew_size()
        self.__initialize()
        # cleanup functions
        atexit.register(self.__finalize)
        
    def __initialize(self):
        self.hwndDC = GetWindowDC(self.hwnd)
        self.mfcDC  = CreateDCFromHandle(self.hwndDC)
        self.saveDC = self.mfcDC.CreateCompatibleDC()
        self.saveBitMap = CreateBitmap()
        self.saveBitMap.CreateCompatibleBitmap(self.mfcDC, self.width, self.height)
        self.saveDC.SelectObject(self.saveBitMap)
        self.safeHdc = self.saveDC.GetSafeHdc()
        
    def __finalize(self):
        DeleteObject(self.saveBitMap.GetHandle())
        self.saveDC.DeleteDC()
        self.mfcDC.DeleteDC()
        ReleaseDC(hwnd, self.hwndDC)
        
    def grab(self):
        return frombuffer(
            self.grap_raw(), uint8
            ).reshape(self.height, self.width, 4)
    
    def grab_pil(self):
        return frombytes("RGB", (self.width, self.height), self.grap_raw(), "raw", "BGRX")
    
    def grap_raw(self):
        PrintWindow(hwnd, self.safeHdc, 1)
        return self.saveBitMap.GetBitmapBits(True)
    
    def renew_size(self):
        left, top, right, bottom = GetClientRect(self.hwnd)
        self.width = right - left
        self.height = bottom - top
        
if __name__ == '__main__':
    hwnd = FindWindow(None, 'Calculator')
    wc = WinCap(hwnd)
    for i in range(5):
        wc.grab_pil().show()
        input(':>')
