
import os, g, sys
sys.path.append(os.getcwd())
def get_udf_path(path):
    # print(sys.path)
    for _path in sys.path:
        _ = _path+path
        if os.path.exists(_): return _
    raise FileNotFoundError(path)
if os.name == "nt":  # Windows
    import ctypes
    g.startup_time = ctypes.windll.kernel32.GetTickCount64()
else: g.startup_time = int(os.popen('uptime -p').read()[:-1].split(' ')[1]) * 60 * 1000

if __name__ == "__main__":
    import PyQt5, sys, ctypes
    from PyQt5 import QtWidgets, QtCore
    def _exit(*args, **kwargs):
        print("exit")
        os._exit(0)
    def get_windows_bit_length():
        size = ctypes.sizeof(ctypes.c_voidp)
        if size == 4: return 32
        elif size == 8: return 64
        else: raise Exception("Windows is not 32 or 64. Fuck!")

    class startup_gif_setup(QtWidgets.QLabel):
        def __init__(self):
            super().__init__()
            # show ui on Center screen
            qtRectangle = self.frameGeometry()
            qtRectangle.moveCenter(QtWidgets.QDesktopWidget().availableGeometry().center())
            #------------------------------------------#
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.setWindowIcon(self.windowIcon())
            self.resize(500, 500)
            rect = qtRectangle.topLeft()
            self.move(QtCore.QPoint(rect.x()+100, rect.y()))
            self.activateWindow()
            # Loading the GIF
            self._movie = PyQt5.QtGui.QMovie(get_udf_path("/app/asset/sword.gif"))
            self.setMovie(self._movie)
            try:
                get_udf_path("/Data/license_ok.txt")
                self._movie.setSpeed(145)
            except: self._movie.setSpeed(60)
            if g.startup_time > 50*1000:
                self._movie.start()
                self.setWindowIcon(PyQt5.QtGui.QIcon(get_udf_path("/app/asset/icon.png")))
                self.show()
            else: _exit()
    global app
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, False)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, False)
    app = QtWidgets.QApplication([])
    gif = startup_gif_setup()
    gif.ui_icon = PyQt5.QtGui.QIcon(get_udf_path("/app/asset/icon.png"))
    gif.setWindowIcon(gif.ui_icon)
    app.setWindowIcon(gif.ui_icon)
    sys.exit(app.exec_())
    try: _exit(app.exec_())
    except KeyboardInterrupt: _exit()
    finally: _exit()
else:
    import sys, subprocess as sp
    try: loading_py = get_udf_path("/loading.pyc")
    except FileNotFoundError: loading_py = get_udf_path("/loading.py")
    g.gif_process = sp.Popen([sys.executable, loading_py], cwd=os.getcwd())#, stdout=sp.PIPE, stderr=sp.STDOUT)


