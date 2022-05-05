
#imports
import g
my = g.my
from Com import *
from PyQt5 import QtWidgets, QtCore, uic
import requests, os, pycrypt as crypt
import datetime
def getOnlineUTCTime():
    _time = requests.get('https://just-the-time.appspot.com/').text.strip()
    return datetime.datetime.strptime(_time, '%Y-%m-%d %H:%M:%S')

class loginUI(QtWidgets.QWidget):
    def __init__(self, password, true_code, false_code=my.emptyDef, FB=None, mPath=None):
        super().__init__()
        if password is None: return
        if FB: self.FB = FB
        else: self.FB = 'https://www.facebook.com/Auto.Legend.Online.Arabic/' #d
        self.mPath = mPath
        uic.loadUi(f"app/login.ui", self)
        self.password = password
        self.true_code = true_code
        self.false_code = false_code
        self.btn_login.clicked.connect(self.btn_login_clicked)
        self.setWindowIcon(my.ui.ui_icon)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        # show widget on Center screen #
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        ################################
        self.show()
        self.inp_password.setFocus()
        shortcut('Enter', self.inp_password, self.btn_login.click, 500)
        shortcut('Return', self.inp_password, self.btn_login.click, 500)

    def btn_login_clicked(self):
        self.btn_login.clicked.disconnect(self.btn_login_clicked)
        if self.inp_password.text() == self.password:
            self.lab_status.setText('Status: Password is Correct !')
            self.hide()
            self.true_code()
            my.settings["loginUI_on"] = False
            self.deleteLater()
        else:
            self.lab_status.setText('Status: Password is Wrong !')
            self.false_code()
        self.btn_login.clicked.connect(self.btn_login_clicked)

class license(QtWidgets.QWidget):
    license_ok = False #if license is valid or not
    license_checked = False #if checkLicence has been called or not
    license = None #carries the instanse of this class
    end_date = None #datetime.datetime object of license end_date
    order_date = None #date of registering the user
    license_type = None #type of the license (eg: 3 days, 1 week, 1 month, 3 months ...etc)
    username = None #user's username
    def __init__(self, online_txt, success_code=my.emptyDef, fail_code=my.emptyDef, code_before_shown=my.emptyDef, ui_icon=None, mPath=None):
        self.mPath = mPath
        super().__init__()
        self.online_txt = online_txt
        self.success_code = success_code
        self.fail_code = fail_code
        self.code_before_shown = code_before_shown
        self.ui_icon = ui_icon
        self.disks = unsafe(self.get_disks_serials)
        license.license = self
        self.checkLicence()

    def btn_copy_clicked(self):
        #copy hwid to system clidboard
        QtWidgets.QApplication.clipboard().setText(self.shownHwid)

    def btn_facebook_clicked(self):
        #open in web browser
        import webbrowser
        webbrowser.open(self.FB, new=2)

    def closeEvent(self, event):
        event.accept()
        open(self.mPath+'/device_id.txt', 'w').write(self.shownHwid)
        os._exit(0)

    def show_ui(self):
        uic.loadUi(self.mPath+f"/app/license.ui", self)
        self.btn_copy.clicked.connect(self.btn_copy_clicked)
        self.btn_facebook.clicked.connect(self.btn_facebook_clicked)
        self.btn_telegram.clicked.connect(lambda: QtWidgets. QApplication.clipboard().setText(self.lab_telegram.text()))
        self.shownHwid = f'[{self.realHwid2Shown(self.disks[0])}]'
        self.inp_hwid.setText(self.shownHwid)
        if self.ui_icon: self.setWindowIcon(self.ui_icon)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        # show widget on Center screen #
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        ################################
        self.code_before_shown()
        self.show()
        self.btn_copy.setFocus()

    def checkLicence(self):
        my.p('checkLicence started')
        hwid_dict = eval(crypt.HEX_crypt.decrypt(unsafe(lambda: requests.get(self.online_txt).text)))
        current_date = getOnlineUTCTime()
        for disk in self.disks:
            if disk in hwid_dict:
                license_data = hwid_dict[disk]
                license.end_date = datetime.datetime.strptime(license_data['end_date'], '%Y-%m-%d %H:%M:%S')
                license.order_date = datetime.datetime.strptime(license_data['order_date'], '%Y-%m-%d %H:%M:%S')
                license.license_type = license_data['license_type']
                license.username = license_data['username']
                if license.end_date - datetime.datetime.now() > datetime.timedelta(milliseconds=1):
                    #license is valid
                    my.p('checkLicence done: True')
                    self.license_ok = license.license_ok = True
                    if not g.license_ok_txt_exists:
                        fileWrite(self.mPath+"/Data/license_ok.txt", 'ok')
                        g.license_ok_txt_exists = True
                    self.license_checked = license.license_checked = True
                    self.success_code()
                    return
                else:
                    #license is NOT valid
                    break

        self.license_ok = license.license_ok = False
        if g.license_ok_txt_exists:
            os.remove(self.mPath+"/Data/license_ok.txt")
            g.license_ok_txt_exists = False
        self.license_checked = license.license_checked = True
        self.fail_code()
        self.show_ui()
        my.p('checkLicence done: False')

    def get_disks_serials(self):  # get list of serial numbers of connected HDDs & SSDs [as HWID obtainer]
        if os.name == 'nt':  # Windows
            a = os.popen("wmic diskdrive get serialnumber").read().strip() \
                .replace('SerialNumber', '').replace('\n\n', '\n').split('\n')
            _ = []
            for idx, i in enumerate(a):
                i = i.replace(' ', '')
                if i == '': continue
                if '-' in i: i = i.split('-')[-1]
                _.append(i)
            return list(set(_))
        else:  # Linux
            a = os.popen("lsblk --nodeps -no name,serial | grep sd").read().split('\n')
            _ = []
            for i in a:
                if i == '':
                    continue
                else:
                    _.append(i.split(' ')[-1])
            return _

    def realHwid2Shown(self, real_hwid): return real_hwid[::-1]

    def shownHwid2real(self, shown_hwid): return shown_hwid[::-1]

    @staticmethod
    def act(code):
        if license.license_checked:
            if license.license_ok: code()
        elif g.license_ok_txt_exists: code()


#todo: add ui section that display license status [ie: prochased date && license type && time left]

