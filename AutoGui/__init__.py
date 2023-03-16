import os
import atexit

if os.name != 'nt':
    from Xlib.X import NONE, ZPixmap
    from Xlib.display import Display
    display = Display()
    # root = display.screen().root
    # window = display.get_input_focus().focus
    def get_window_by_id(id):
        return display.create_resource_object('window', id)
    # cleanup functions
    atexit.register(display.close)
    
# NB: this library uses XLib on linux, so: it works only on X11 (not on Wayland)