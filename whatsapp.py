
if __debug__:
    from traceback import print_exc as dbg
from .webdriver import (
    Driver, TimeoutException, WebDriverException,
    time, get_path, Keys, EC, By, WebDriverWait,
    )
from selenium.common.exceptions import JavascriptException
import os, psutil
from urllib.parse import quote
emptyDef = lambda *args, **kwargs: 0

# DEFAULT_CHROME_BINARY = (
#     # get_path('./app/asset/electron/electron'),
#     # get_path('./app/asset/electron/chromedriver')
#     '/home/ibrahem/Desktop/Linux/Apps/chrome/chrome',
#     '/home/ibrahem/Desktop/Linux/Apps/chrome/chromedriver'
# )
userAgent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) whatsapp-desktop/2.22.5 Chrome/100.0.3029.110 Electron/21.3.3 Safari/537.36'
class Whatsapp:
    contact_eye = """
    (()=>{
        var a = document.createElement('a');
        a.href = "https://api.whatsapp.com/send?phone={num}&text={msg}";
        document.body.appendChild(a);
        window.get_contact = (phone, msg="")=>{
            a.href = `https://api.whatsapp.com/send?phone=${phone}&text=${msg}`;
            a.click();
        }
    })();
    """
    not_whatsapp_user_js = '''
        var el = document.querySelector('div[role="dialog"]');
        if (!el){ return false; }
        return el.innerHTML.includes("Phone number shared via url is invalid.");
      '''.strip()
    whatsapp_web = 'https://web.whatsapp.com/'
    current_chat = None
    def __init__(self, profile="./data/chrome_profile", headless=False, userAgent=None, profile_directory=None, is_electron=False) -> None:
        # g.wa = self
        my_chrome_driver = Driver(profile=profile, headless=headless, userAgent=userAgent, chrome_app_url=self.whatsapp_web, profile_directory=profile_directory, is_electron=is_electron)
        self.driver = my_chrome_driver.get_driver()
        # inherit
        self.quit = my_chrome_driver.quit
        self.cleanup = my_chrome_driver.cleanup
        self.suspend = my_chrome_driver.suspend
        self.resume = my_chrome_driver.resume
        self.sleep = my_chrome_driver.sleep
        self.js = self.driver.js
        self.wait = self.driver.wait
        self.wait4 = self.driver.wait4
        
    def login(self, login_required_callback=emptyDef, login_done_callback=emptyDef, on_qr_prompt=emptyDef, on_qr_scanned=emptyDef):
        while True:
            try:
                self.driver.get(self.whatsapp_web)
                break
            except WebDriverException as e:
                if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                    print('TODO no internet error') #TODO
                    # try:
                    #     if g.quit_now: exit()
                    # except: pass
                    time.sleep(2.5)
        # if off_screen:
            # self.driver.set_window_position(-5000,0)
        #check if QR code exists (if user not logged in)
        while True:
            try:
                self.driver.wait(1, EC.presence_of_element_located, By.XPATH, '//div[@role="textbox"]')
                # print('messages load done')
                break
            except TimeoutException:
                try:
                    # QR_code = self.driver.find_elements(By.CLASS_NAME, 'landing-title')
                    QR_code = self.driver.find_elements(By.XPATH, '//div[@data-testid="qrcode"]')
                    if QR_code:
                        ## ask the user to log in [: ##
                        # print('WA login required, waiting for login')
                        login_required_callback()
                        # wait for QR to be scanned
                        old_qr = QR_code[0].get_attribute("data-ref")
                        on_qr_prompt(old_qr)
                        while True:
                            # print('start:', time.time())
                            try:
                                self.wait(
                                    1.5,
                                    EC.presence_of_element_located,
                                    By.XPATH, '//span[@data-testid="refresh-large"]'
                                ).click()
                                # print('on exception')
                                time.sleep(1)
                                # print('regenerate pressed')
                            except TimeoutException as e:
                                pass
                            try:
                                new_qr = self.js('return document.querySelector(`div[data-testid="qrcode"]`).getAttribute("data-ref");')
                                if new_qr == old_qr:
                                    continue
                                else:
                                    old_qr = new_qr
                                    on_qr_prompt(old_qr)
                            except JavascriptException:
                                # Message: javascript error: Cannot read properties of null (reading 'getAttribute')
                                try:
                                    self.wait(1, EC.invisibility_of_element_located, By.CLASS_NAME, "landing-title")
                                    ## when qr_code dissappear (ie: login process started) ##
                                    break
                                except TimeoutException:
                                    pass
                        
                        # unsafe(self.driver.wait, (999999, EC.invisibility_of_element_located, By.CLASS_NAME, "landing-title"))
                        # self.driver.wait4(EC.invisibility_of_element_located, By.CLASS_NAME, "landing-title")
                        # print('login successful, waiting for messages to load')
                        on_qr_scanned()
                        self.driver.wait4(EC.invisibility_of_element_located, By.ID, "main")
                        self.driver.wait(1, EC.presence_of_element_located, By.XPATH, '//div[@role="textbox"]')
                        # print('messages load done')
                        break
                    else:
                        raise TimeoutException()
                except TimeoutException:
                    pass
            time.sleep(2) # while loop truce
        self.js(Driver.jQuery)
        self.js(Whatsapp.contact_eye)
        # print('method end')
        login_done_callback()

    def open_chat(self, num, msg='', on_not_whatsapp_user=emptyDef, on_whatsapp_user=emptyDef):
        # if self.current_chat not in {num, None}:
        #     #close current chat
        #     chat_exists = self.driver.find_elements(By.XPATH, '//div[@id="main"]') != []
        #     if chat_exists:
        #         self.driver.js('''$("#main").find('span[data-icon="menu"]')[0].click();''')
        #         time.sleep(1) #fixme => untill dropdown menu open
        #         #btn_close_chat = driver.js('''window.btn_close_chat = $('div[aria-label="Close chat"]')[0]; return btn_close_chat;''')
        #         self.driver.js('''$('div[aria-label="Close chat"]')[0].click()''')
        #         #driver.js('''window.btn_close_chat.id = "btn_close_chat";''')
        #         #WebDriverWait(driver, 999999).until(EC.element_to_be_clickable((By.ID, "btn_close_chat")))
        #         #WebDriverWait(driver, 999999).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "btn_close_chat")))
        #         #btn_close_chat.click()
        #         self.driver.wait4(EC.invisibility_of_element_located, By.ID, "main")
        # if msg: # if this is a txt msg. or you just wanna open the chat
        #     msg = msg.replace('\n', '%0A')
        self.driver.js(f'get_contact("{num}", "{quote(msg)}");')
        # self.driver.js(f'get_contact("{num}", "{quote(msg)}");')
        #FIXME: correct country code [modify num according to country]
        not_whatsapp_user = False
        while True: #time.sleep(0.5)
            try:
                print('in loop')
                inp_text = self.wait(1, EC.presence_of_element_located, By.XPATH, '//div[@data-testid="conversation-compose-box-input"]')
                break
            except TimeoutException:
                not_whatsapp_user = self.driver.js(Whatsapp.not_whatsapp_user_js)
                self.driver.find_element_by_xpath('//div[@role="dialog"]')
                print(f'{not_whatsapp_user = }')
                if not_whatsapp_user: break
        if not_whatsapp_user:
            # close the "Phone number shared via url is invalid." dialog
            while True:
                try:
                    print('finding btn_ok')
                    self.driver.find_element(By.XPATH, '//div[@data-testid="popup-controls-ok"]').click()
                    time.sleep(0.25) # wait untill dialog closes
                    break
                except: pass
            # time.sleep(0.5)
            # self.driver.find_element_by_xpath('//div[@role="dialog"]').send_keys(Keys.ESCAPE)
            # try: #check _starting_chat_bug
            #     WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located((By.XPATH, '//div[@role="dialog"]')))
            # except TimeoutException:
            #     _starting_chat_bug = self.driver.js('''return $('div[data-animate-modal-body="true"]')[0].innerHTML.includes("Starting chat");''')
            #     if _starting_chat_bug:
            #         self.driver.find_element(By.XPATH, '//div[@data-testid="popup-controls-ok"]').click()

            #         #document.querySelector('')
                    
            # time.sleep(0.25) # wait untill current chat is closed
            
            # self.current_chat = None
            on_not_whatsapp_user()
            # print(f'{on_not_whatsapp_user=}')
            return 0 #not_whatsapp_user
        else:
            on_whatsapp_user()
            # print(f'{on_not_whatsapp_user=}')
            self.current_chat = num
            return inp_text

    def send_msg(self, num, msg, wait4sent=True, send_keys=False, on_not_whatsapp_user=emptyDef, on_whatsapp_user=emptyDef) -> int:
        # @send_keys => send msg by typing it, not from url_query
        if send_keys:
            inp_text = self.open_chat(num, on_not_whatsapp_user=on_not_whatsapp_user, on_whatsapp_user=on_whatsapp_user)
        else:
            inp_text = self.open_chat(num, msg, on_not_whatsapp_user=on_not_whatsapp_user, on_whatsapp_user=on_whatsapp_user)
        print('after open_chat')
        # inp_text = self.driver.wait4(EC.presence_of_element_located, By.XPATH, '//div[@title="Type a message"]')
        if inp_text:
            # inp_text.send_keys(Keys.ENTER)
            if send_keys:
                from time import sleep
                from random import uniform
                for char in msg:
                    inp_text.send_keys(char)
                    sleep(uniform(0.05, 0.1))
                self.driver.wait4(EC.presence_of_element_located, By.XPATH, '//button[@data-testid="compose-btn-send"]').click()
            else:
                while True:
                    try:
                        self.driver.wait(0.5, EC.presence_of_element_located, By.XPATH, '//button[@data-testid="compose-btn-send"]').click()
                        break
                    except TimeoutException:
                        print('trying to re-open chat')
                        if self.open_chat(num, msg, on_not_whatsapp_user=on_not_whatsapp_user, on_whatsapp_user=on_whatsapp_user):
                            return 0
            ## wait for msg to be sent ##
            if wait4sent:
                time.sleep(0.8)
                try:
                    self.wait(3, EC.invisibility_of_element_located, By.XPATH, '//span[@data-testid="msg-time"]')
                except TimeoutException:
                    pass
            return 1
        else:
            return 0

    def send_img(self, num, img_path, wait4sent=True, on_sent=emptyDef):
        # from code import InteractiveConsole
        # vars = {}
        # vars.update(locals())
        # vars.update(globals())
        # InteractiveConsole(locals=vars).interact()
        # return
        # img_path = '/home/ibrahem/Pictures/IMG_0065.JPG'
        if not os.path.isfile(img_path):
            raise Exception('img_path: file not found')
        self.open_chat(num)
        self.driver.wait4(EC.presence_of_element_located, By.XPATH, '//div[@aria-label="Attach"]').click()
        self.driver.wait4(EC.presence_of_element_located, By.XPATH, '//input[contains(@accept,"image/")]')\
            .send_keys(os.path.abspath(img_path))
        self.driver.wait4(EC.presence_of_element_located, By.XPATH, '//div[@aria-label="Send"]').click()
        ## wait for msg to be sent ##
        if wait4sent:
            # wait for inp_text to appear
            self.wait4(EC.presence_of_element_located, By.XPATH, '//div[@title="Type a message"]')
            # extra wait for ensurance
            time.sleep(1.1)
            # print(1)
            self.wait4(EC.invisibility_of_element_located, By.XPATH, '//svg[@role="status"]/circle')
            # print(2)
            # self.wait4(EC.invisibility_of_element_located, By.XPATH, '//svg[@role="status"]/circle')
            # print(3)
            on_sent()

        

        


#https://www.geeksforgeeks.org/share-whatsapp-web-without-scanning-qr-code-using-python/

# Test Email: kelgwlgwfmpvunuxkt@nthrw.com
# password: selenium
import threading, inspect
from collections import deque
class WhatsappThread(threading.Thread): pass
class WhatsappThread(WhatsappThread):
    "a Wrapper to run Whatsapp instance in a separate thread"
    def __init__(self, whatsapp=None, whatsapp_args=(), whatsapp_kwargs={}, print_errors=True, raise_errors=False, suspend_when_idle=True):
        # whatsapp:Whatsapp => Whatsapp instance to initiate this class with
        # whatsapp_args:tuple => args of newly created Whatsapp if "whatsapp" arg was None
        # whatsapp_kwargs:dict => kwargs of newly created Whatsapp if "whatsapp" arg was None
        # print_errors:bool => print Exceptions if they happend while calling a Whatsapp method (eg: send_msg)
        # raise_errors:bool => raise Exceptions if they happend while calling a Whatsapp method (eg: send_msg)
        # suspend_when_idle:bool => suspend chrome process when idle (no job in the self.queue) to save cpu
        threading.Thread.__init__(self)
        self.whatsapp = whatsapp
        self.whatsapp_args = whatsapp_args
        self.whatsapp_kwargs = whatsapp_kwargs
        self.exit_thread_flag = False
        self.queue = deque()
        self.print_errors = print_errors
        self.raise_errors = raise_errors
        self.suspend_when_idle = suspend_when_idle
        self.trigger = threading.Event()
        ## set wrapper for methods of Whatsapp class ##
        #>>> inspect.getmembers(Whatsapp, predicate=inspect.isfunction)
        #[('__init__', <function Whatsapp.__init__ at 0x7f61fcef70a0>), ('open_chat', <function Whatsapp.open_chat at 0x7f61fcef72e0>), ('quit', <function Whatsapp.quit at 0x7f61fcef7130>), ('resume', <function Whatsapp.resume at 0x7f61fcef7250>), ('send_img', <function Whatsapp.send_img at 0x7f61fcef7400>), ('send_msg', <function Whatsapp.send_msg at 0x7f61fcef7370>), ('suspend', <function Whatsapp.suspend at 0x7f61fcef71c0>)]
        self.start()
        # print(self.resume)

        
    def login(self, *args, **kwargs):
        self.queue.append((Whatsapp.login, args, kwargs))
        self.trigger.set()
        
    def open_chat(self, *args, **kwargs):
        self.queue.append((Whatsapp.open_chat, args, kwargs))
        self.trigger.set()
        
    def send_msg(self, *args, **kwargs):
        self.queue.append((Whatsapp.send_msg, args, kwargs))
        self.trigger.set()
        
    def send_img(self, *args, **kwargs):
        self.queue.append((Whatsapp.send_img, args, kwargs))
        self.trigger.set()
    # def generate_def(method):
    #     def _def(self, *args, **kwargs):
    #         self.queue.append((method[1], args, kwargs))
    #         self.trigger.set()
    #     return _def
    # for method in inspect.getmembers(Whatsapp, predicate=inspect.isfunction)[1:]: # except method Whatsapp.__init__
    #     object.__setattr__(WhatsappThread, method[0], generate_def(method))
    # del generate_def


    def run(self):
        if self.whatsapp is None:
            self.whatsapp = Whatsapp.__new__(Whatsapp)
            self.whatsapp.__init__(*self.whatsapp_args, **self.whatsapp_kwargs)
            # self.whatsapp_started.set()
        # print(self)
        if self.suspend_when_idle:
            self.whatsapp.suspend()
        while True:
            self.trigger.wait()
            if self.suspend_when_idle:
                self.whatsapp.resume()
            while self.queue:
                job = self.queue.popleft()
                # job:tuple (method_of_Whatsapp:function, args:tuple, kwargs:dict) #HERE: test + extend design: *args, **kwargs
                try:
                    # self.whatsapp.__getattribute__(job[0])(*job[1], **job[2])
                    job[0](self.whatsapp, *job[1], **job[2])
                except Exception as e:
                    if self.print_errors:
                        dbg()
                    if self.raise_errors:
                        raise e
                try:
                    if job[0] == Whatsapp.quit:
                        return
                except AttributeError: pass
            if self.suspend_when_idle:
                self.whatsapp.suspend()
            if self.exit_thread_flag:
                return
            # print('finished a thread loop')
            self.trigger.clear()

    def exit_thread(self):
        self.exit_thread_flag = True
        self.trigger.set()

    # def quit(self, *args, **kwargs):
    #     self.queue.append(('quit', args, kwargs))
    #     self.trigger.set()

    # def suspend(self, *args, **kwargs):
    #     self.queue.append(('suspend', args, kwargs))
    #     self.trigger.set()

    # def resume(self, *args, **kwargs):
    #     self.queue.append(('resume', args, kwargs))
    #     self.trigger.set()

    # def open_chat(self, *args, **kwargs):
    #     self.queue.append(('open_chat', args, kwargs))
    #     self.trigger.set()

    # def send_msg(self, *args, **kwargs):
    #     self.queue.append(('send_msg', args, kwargs))
    #     self.trigger.set()

    # def send_img(self, *args, **kwargs):
    #     self.queue.append(('send_img', args, kwargs))
    #     self.trigger.set()

        



if __name__ == '__main__':
    w = Whatsapp(**{'profile': "./data/whatsapp_profile", 'headless': False, 'is_electron':True})
    
    import time
    # time.sleep(20)
    w.login()
    w.send_img('+201061929763', 'Archive/logo.png')
    # t = WhatsappThread(whatsapp_kwargs={'headless':True})
    # t.start()
    # t.send_img('+201061929763', '/home/ibrahem/Downloads/logo.jpg')
    # t.send_msg('+201061929763', 'this is a dummy text msg')
    # t.send_msg('+201061929763', 'this is a dummy text msg 1')
    # t.send_msg('+201061929763', 'this is a dummy text msg 2')
    # t.send_msg('+201061929763', 'this is a dummy text msg 3')
    # time.sleep(30)
    # for i in range(5):
    #     t.send_msg('+201061929763', f'this is a dummy text msg {4+i}')
    #     time.sleep(3)
    # t.quit()
    # print('finished main thread jobs')
    # t.join()
    pass