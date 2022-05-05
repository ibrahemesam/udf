#imports
import psutil, shutil, subprocess, io, sqlite3, gc, numpy, time, signal, threading, configparser, os, sys, PyQt5, random
from PyQt5.QtCore import *
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets, QtWebChannel, uic, QtGui, QtNetwork
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestJob, QWebEngineUrlRequestInterceptor, QWebEngineUrlSchemeHandler, QWebEngineUrlScheme
from PyQt5.QtTest import QTest
from PIL import ImageQt
from datetime import datetime
import cv2, sip, g
my = g.my
from my import *
global alert, mPath, js, func; alert=js=None
def init_var(value, var_name): globals()[var_name] = value

def get_ui_state(ui):
    if ui.container.isMinimized(): return 'minimized'
    elif ui.container.isMaximized(): return 'maximized'
    elif ui.container.isHidden(): return 'hidden'
    else: return 'shown'

def set_ui_state(ui, state):
    if state == 'minimized': ui.showMinimized()
    elif state == 'maximized': ui.showMaximized()
    elif state == 'hidden': ui.hide()
    else: ui.show()

def make_app_dark(app):
    # Fusion dark palette from https://gist.github.com/QuantumCD/6245215.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

def move_ui_to_center_screen(ui): # show ui on Center screen
    qtRectangle = ui.frameGeometry()
    centerPoint = QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    ui.move(qtRectangle.topLeft())

class Container(QtWidgets.QWidget):
    def __init__(self, window, parent=None):
        super(Container, self).__init__(parent)
        self.window = window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(window)
        lay.setContentsMargins(10, 10, 10, 10)
        # inherit container behavior into the widget (window)
        window.setWindowIcon = self.setWindowIcon
        window.hide = self.hide
        window.show = self.show
        window.showNormal = self.showNormal
        window.showMinimized = self.showMinimized
        window.showMaximized = self.showMaximized
        window.move = self.move
        window.old_x = window.x
        window.old_y = window.y
        window.x = self.x
        window.y = self.y
        window.old_show = window.show
        def show():
            try: g.gif_process.terminate()
            except: pass
            window.setWindowIcon(g.ui_icon)
            window.old_show()
        window.show = show

    def paintEvent(self, event):
        nShadowsWidth = 10; nRadius = 5
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        color = QColor(99, 255, 255, 10)
        for i in range(nShadowsWidth):
            path = QPainterPath()
            path.setFillRule(Qt.WindingFill)
            path.addRoundedRect(nShadowsWidth - i, nShadowsWidth - i, self.width() - (nShadowsWidth - i) * 2, self.height() - (nShadowsWidth - i) * 2, nRadius +i, nRadius +i)
            color.setAlpha(round(150 - math.sqrt(i) * 50))
            painter.setPen(color)
            painter.drawPath(path)



class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        return
        url = info.requestUrl().url()
        if 'game.jsp?' in url:
            #print(url)
            self.parentElement.loginUrl = url
        my.p(url)

class HtmlViewPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, webView, profile=None, ignoredMsgs=[]):
        self.ignoredMsgs = ignoredMsgs
        self.parent_webView = webView
        if profile==None: super(HtmlViewPage, self).__init__(webView)
        else: super(HtmlViewPage, self).__init__(profile, webView)

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        ignoredSourceIDs = ['chrome-error://chromewebdata/']
        for isi in ignoredSourceIDs:
            if isi in sourceID: return
            if sourceID in isi: return
        for im in self.ignoredMsgs:
            if im in msg: return
            if msg in im: return
        if msg.startswith('ajaxReturn'):
            self.parentElement.ajaxReturn = eval(msg.replace('ajaxReturn', '').replace('true', 'True').replace('false', 'False'))
            return
        # if 'redist/FB-login.html' in sourceID: return
        # if msg == "Uncaught TypeError: Cannot set property 'width' of undefined" and ".com/client/scripts/shenqu.js" in sourceID: return
        print(f'JS {level}:{line}:{sourceID}: {msg}')
        if 'DEV' in g.version:
            if str(level) == "2": self.parent_webView.view_dev_tools()

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        #my.p('acceptNavigationRequest', url, _type, isMainFrame)
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)

    def javaScriptAlert(self, *args, **kwargs):
        if args[1] in self.ignoredMsgs: pass
        else:
            print(f'unHandled JS Alert: {args[1]}') #caused by any webView other than self.webUI

    def javaScriptConfirm(self, *args, **kwargs):
        msg = args[1]
        for im in self.ignoredMsgs:
            if im in msg: return True
            if msg in im: return True
        else :
            print(f'unHandled JS Confirm: {args[1]}') #caused by any webView other than self.webUI
            return True

class HtmlView(QtWebEngineWidgets.QWebEngineView):
    sigFbLoginFinished = pyqtSignal()
    fb_login_finished = False
    def __init__(self, windows=[], URL2go=None, parentElement=None, inPrivate=False, inPrivate_dir=None, showCreatedWindows=True, is_account_type_fb=False, msToWaitBeforeReloadOnConnFail=3000, custom_profile_dir=None, loadJsHelper=True, dontCreateSubWindow=False, ignoredMsgs=[],
     *args, **kwargs):
        super(HtmlView, self).__init__(*args, **kwargs)
        self.URL2go = URL2go; self.parentElement = parentElement; self.inPrivate = inPrivate
        self.inPrivate_dir = inPrivate_dir; self.showCreatedWindows = showCreatedWindows
        self.is_account_type_fb = is_account_type_fb; self.msToWaitBeforeReloadOnConnFail = msToWaitBeforeReloadOnConnFail
        self.custom_profile_dir = custom_profile_dir; self.loadJsHelper = loadJsHelper; self.dontCreateSubWindow = dontCreateSubWindow
        self.loadFinished.connect(self.onLoadFinished)
        #NO# QWebEngineProfile.defaultProfile().setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        if inPrivate: self.setPage(HtmlViewPage(self, QtWebEngineWidgets.QWebEngineProfile()))
        else: self.setPage(HtmlViewPage(self))

        self.page().featurePermissionRequested.connect(self.onFeaturePermissionRequested)
        # Signal slot to which cookie is added
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.interceptor = WebEngineUrlRequestInterceptor()
        self.interceptor.parentElement = self
        self.page().profile().setUrlRequestInterceptor(self.interceptor)
        self.page().profile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.cookies = {} # store cookie dictionary
        self._windows = windows
        self._windows.append(self)
        global mPath
        if inPrivate: self.page().profile().setPersistentStoragePath( f'{mPath}/Data/Temp/{inPrivate_dir}')
        else: self.page().profile().setPersistentStoragePath(f'{mPath}/{custom_profile_dir}' if custom_profile_dir else f'{mPath}/Data/Browser Profile')
        self.inPrivate = inPrivate
        self.showCreatedWindows = showCreatedWindows
        self.is_account_type_fb = is_account_type_fb
        self.page().profile().setCachePath(f'{mPath}/Data/Browsers Cache')
        #custom_profile_dir
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        #self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        #self.page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True);
        #self.page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True);

        if parentElement != None:
            self.parentElement = parentElement
            self.page().parentElement = parentElement
        self.oldReload=self.reload
        if msToWaitBeforeReloadOnConnFail != None:
            def reload_on_conn_fail(result):
                if not result:
                    wait(msToWaitBeforeReloadOnConnFail)
                    if g.bh.is_connected(): self.reload()
            self.loadFinished.connect(reload_on_conn_fail)

        if not inPrivate:
            self.page().profile().setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self.page().profile().cookieStore().loadAllCookies()
        if URL2go != None: self.setUrl(QUrl(URL2go))
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(lambda request: request.accept())
        self.def_on_close = self.def_on_close_attempt = my.emptyDef
        self.page().ignoredMsgs = ignoredMsgs

    @QtCore.pyqtSlot(bool)
    def onLoadFinished(self, ok):
        #print("Finished loading: ", ok)
        if ok and not self.inPrivate and self.loadJsHelper:
            self.load_qwebchannel()

    def load_qwebchannel(self):
        oBackEnd = BackEnd(self)
        oBackEnd.browser = self
        file = QtCore.QFile(":/qtwebchannel/qwebchannel.js")
        if file.open(QtCore.QIODevice.ReadOnly):
            content = file.readAll()
            file.close()
            self.page().runJavaScript(content.data().decode())
        if self.page().webChannel() is None:
            channel = QtWebChannel.QWebChannel(oBackEnd)
            self.page().setWebChannel(channel)
        self.add_objects({"jshelper": oBackEnd})

    def add_objects(self, objects):
        if self.page().webChannel() is not None:
            initial_script = ""
            end_script = ""
            self.page().webChannel().registerObjects(objects)
            for name, obj in objects.items():
                initial_script += f"{name}=null;"
                end_script += f"{name} = channel.objects.{name};"
            self.js(initial_script+"new QWebChannel(qt.webChannelTransport, function (channel) {"+end_script+"} );")

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QtWebEngineWidgets.QWebEnginePage.NavigationTypeLinkClicked:
            return True
        return super(HtmlView.page(), self.page()).acceptNavigationRequest(url, _type, isMainFrame)

    def createWindow(self, _type):
        if self.dontCreateSubWindow: return
        if QtWebEngineWidgets.QWebEnginePage.WebBrowserTab:
            v = HtmlView(self._windows, URL2go=self.URL2go, parentElement=self.parentElement, inPrivate=self.inPrivate, inPrivate_dir=self.inPrivate_dir, showCreatedWindows=self.showCreatedWindows, is_account_type_fb=self.is_account_type_fb, msToWaitBeforeReloadOnConnFail=self.msToWaitBeforeReloadOnConnFail, custom_profile_dir=self.custom_profile_dir, loadJsHelper=False)
            if self.showCreatedWindows:
                v.resize(640, 480)
                v.show()
                v.ignoreClose = False
            return v

    def view_dev_tools(self):
        dev_view = HtmlView(self._windows, msToWaitBeforeReloadOnConnFail=None)
        dev_view.resize(640, 480)
        self.page().setDevToolsPage(dev_view.page())
        dev_view.show()

    def onCookieAdd(self, cookie): # Handle the event of cookie addition
        name = cookie.name().data().decode('utf-8') # First obtain the name of the cookie, then process the encoding
        value = cookie.value().data().decode('utf-8') # Get the cookie value first, then process the encoding
        self.cookies[name] = value # save the cookie in the dictionary
        self.page().profile().cookieStore().deleteCookie(QNetworkCookie()) #delete a non-existent cookie from the cookiestore to force it to be flushed to disk right away

    def js(self, js, _return=None):
        if _return == None: self.page().runJavaScript(js)
        else: self.page().runJavaScript(js, _return)

    def js_eval(self, js): #fixme: not working
        tmp = tempClass()
        tmp.loop = QEventLoop()
        tmp.done = False
        def _(result):
            tmp.result = result
            tmp.done = True
            tmp.loop.quit()
        self.page().runJavaScript(js, _)
        if not tmp.done: tmp.loop.exec_()
        return tmp.result

    def alert(self, s):self.page().runJavaScript(f'''alert(`{str(s)}`)''')

    @QtCore.pyqtSlot(QtCore.QUrl, QtWebEngineWidgets.QWebEnginePage.Feature)
    def onFeaturePermissionRequested(self, url, feature):
        if feature in (QtWebEngineWidgets.QWebEnginePage.MediaAudioCapture,
                       QtWebEngineWidgets.QWebEnginePage.MediaVideoCapture,
                       QtWebEngineWidgets.QWebEnginePage.MediaAudioVideoCapture):
            self.page().setFeaturePermission(url, feature, QtWebEngineWidgets.QWebEnginePage.PermissionGrantedByUser)
        else:
            #return
            my.p(f'freature revoked: {feature}')
            self.page().setFeaturePermission(url, feature, QtWebEngineWidgets.WebEnginePage.PermissionDeniedByUser)

    def closeEvent(self, QCloseEvent):
        try:
            self.ignoreClose
            if self.self.ignoreClose:
                self.def_on_close_attempt()
                QCloseEvent.ignore()
            else:
                self.def_on_close()
                QCloseEvent.accept()
                self.deleteLater()
        except:
            self.def_on_close()
            QCloseEvent.accept()
            self.deleteLater()

    def loadUrlWait(self, str_url):
        loop = QEventLoop()
        loop.loadFinished = False
        def _(*args, loop=loop):
            loop.loadFinished = True
            loop.quit()
        self.loadFinished.connect(_)
        self.load(QUrl(str_url))
        if not loop.loadFinished: loop.exec_()
        self.loadFinished.disconnect(_)

    def waitLoad(self):
        loop = QEventLoop()
        self.loadFinished.connect(loop.quit)
        loop.exec_()
        self.loadFinished.disconnect(loop.quit)

class BackEnd(QObject): # backend for QWebChannel
    @QtCore.pyqtSlot(str, result=str)
    def eval(self, lines=""):
        return str(my.func(lines))

    @QtCore.pyqtSlot(str, str, str, str)
    def call(self, code, callback_function=None, other_callback_args=None): #just an async eval
        #code is => my.get_time()
        #browser is => g.ui.webUI
        #callback_function is => console.info
        #other_callback_args is => "arg_2", "arg_3", "arg_4"
        def _(other_callback_args=other_callback_args):
            result = str(my.func(code))
            #if other_callback_args: other_callback_args = f', {other_callback_args}'
            my.p(f'{callback_function}("{result}, {other_callback_args}");')
            if callback_function: self.browser.js(f'{callback_function}("{result}", {other_callback_args});')
        qthread_task(_).start()

    @QtCore.pyqtSlot(str)
    def exec(self, code): qthread_task(lambda: my.func_exec(code)).start()
    """@QtCore.pyqtSlot(str, result=str)
    def feval(self, lines=""):
        return requests.get(f'http://localhost:{my.flask_port}/eval', params={'code': lines}).text"""

class qthread_task(QtCore.QObject): # start a new QThread that runs a lambda def
    finished = pyqtSignal()
    grabRequested = QtCore.pyqtSignal(int)
    grabAvailable = QtCore.pyqtSignal()
    exec = QtCore.pyqtSignal(object)
    clientLoaded = QtCore.pyqtSignal()
    pause_done = QtCore.pyqtSignal()
    qthreads = [] #store QThreads to prevent their destruction by Garbadge Collector
    def __init__(self, lambdaCode):
        super(qthread_task, self).__init__()
        self.thread = QtCore.QThread()
        self.thread.setTerminationEnabled()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)
        self.start = self.thread.start
        self.finished.connect(self.thread.quit)
        self.finished.connect(self.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.lambdaCode = lambdaCode
        qthread_task.qthreads.append(self.thread)
        self.thread.finished.connect(lambda: qthread_task.qthreads.remove(self.thread))
        self.exec.connect(lambda lambdaCode: lambdaCode())

    def run(self):
        self.lambdaCode()
        self.finished.emit()

def wait(ms): QTest.qWait(ms) # pause executing code without freezing PyQt GUI

class shortcut(QShortcut): # set hotkey command
    def __init__(self, key, parent, lambda_code, await_time_ms):
        self.lambda_code = lambda_code; self.await_time_ms = await_time_ms
        super(shortcut, self).__init__(QKeySequence(key), parent)
        self.activated.connect(self.onActivated)

    def unBlockSignals(self):
        try: self.blockSignals(False)
        except RuntimeError: return

    def onActivated(self):
        self.blockSignals(True)
        threading.Timer(self.await_time_ms / 1000, self.unBlockSignals).start()
        self.lambda_code()

class shortcut_one_use(QShortcut): # a hotkey command that can be triggered once
    def __init__(self, key, parent, lambda_code):
        self.lambda_code = lambda_code
        super(shortcut_one_use, self).__init__(QKeySequence(key), parent)
        self.activated.connect(self.onActivated)

    def onActivated(self):
        self.blockSignals(True)
        self.lambda_code()
        self.deleteLater()

def setLambdaInterval(lambdaCode, interval_ms): # equivelent to js: setInterval
    interval_ms = int(interval_ms)
    wait(interval_ms)
    QtCore.QTimer.singleShot(interval_ms, lambda: multiLambda(lambdaCode, lambda: setLambdaInterval(lambdaCode, interval_ms)))

def unsafe(lambdaCode, msToWait=1000, echo_error=False):  # try the code and if error happened: try again. until it works without error
    def _unsafe():
        while True:
            try:
                tmp._return = lambdaCode()
                loop.quited = True
                loop.quit()
                break
            except:
                if echo_error: print(traceback.format_exc())
                wait(msToWait)
                my.p('err in unsafe method:-\n', traceback.format_exc())
                #except: print("err in unsafe method && Can't get the error ]:")
                #print('err in unsafe method: ', str(sys.exc_info()[1]))
    tmp = tempClass(); tmp._return = None
    loop = QEventLoop(); loop.quited = False
    qthread = qthread_task(_unsafe)
    #qthread.finished.connect(loop.quit)
    qthread.start()
    if not loop.quited: loop.exec_()
    return tmp._return


def unsafe2(lambdaCode, msToWait=1000):  # try the code and if error happened: try again. until it works without error
    #this class uses python threading.Thread instead of QThread
    def _unsafe():
        while True:
            try:
                tmp._return = lambdaCode()
                loop.quit()
                loop.quited = True
                break
            except:
                wait(msToWait)
                my.p('err in unsafe method:-\n', traceback.format_exc())
                #except: print("err in unsafe method && Can't get the error ]:")
                #print('err in unsafe method: ', str(sys.exc_info()[1]))
    tmp = tempClass(); tmp._return = None
    loop = QEventLoop(); loop.quited = False
    thread(_unsafe).start()
    if not loop.quited: loop.exec_()
    return tmp._return

class thread(threading.Thread): # old implementation of: Thread(target=blabla, args=[bla])
    def __init__(self, lambda_code):
        self.lambda_code = lambda_code
        super().__init__()
    def run(self):
        self.lambda_code()

def getListWidgetItemIndex(listWidget, listWidgetItem): # get index of QlistWidgetItem inside QlistWidget
    for i in range(listWidget.count()):
        if listWidget.item(i) is listWidgetItem: return i
    return -1

def ui_eval(lambda_code): # run code in main thread using g.ui.exec && return the result
    tmp = tempClass()
    loop = QEventLoop()
    tmp.loop = loop
    tmp.loop_finished = False
    def _(tmp=tmp):
        tmp.info_return = my.func_lambda(lambda_code)
        tmp.loop.quit()
        tmp.loop_finished = True
    g.ui.exec.emit(_)
    if not tmp.loop_finished: loop.exec_()
    return tmp.info_return

class SideGrip(QtWidgets.QWidget):
    def __init__(self, parent, edge):
        QtWidgets.QWidget.__init__(self, parent)
        if edge == QtCore.Qt.LeftEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == QtCore.Qt.TopEdge:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == QtCore.Qt.RightEdge:
            self.setCursor(QtCore.Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(QtCore.Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None

def wait4signal(sig): #wait for a signal to be emitted
    loop = QEventLoop()
    sig.connect(loop.quit)
    loop.exec_()
    sig.disconnect(loop.quit)
    del loop

def hex2QColor(c): # """Convert Hex color to QColor"""
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    print(c, (r, g, b))
    return QtGui.QColor(r, g, b)
