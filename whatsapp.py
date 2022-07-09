
from faulthandler import disable
from lib2to3.pgen2 import driver
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time, os, g

userAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
__path = os.path.dirname(os.path.abspath(__file__))
def get_path(path):
    return os.path.join(__path, os.path.relpath(path))
def unsafe(_def, args=(), s_sleep=1):
    while True:
        try:
            return _def(*args)
        except:
            time.sleep(s_sleep)

class Driver:
    jQuery = """
    (function (){
        function l(u, i) {
            var d = document;
            if (!d.getElementById(i)) {
                var s = d.createElement('script');
                s.src = u;
                s.id = i;
                d.body.appendChild(s);
            }
        } l('//ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js', 'jquery')
    })();
    """
    timeout = selenium.common.exceptions.TimeoutException
    chrome_bin = None
    chrome_driver = None
    def __init__(self, incognito=False, profile=None, full_screen=False, disable_web_security=False, headless=False, chrome_app_url=None,  userAgent=userAgent, oem_manifest=None, grant_medial_access=False) -> None:
        options = webdriver.ChromeOptions()
        if incognito:
            options.add_argument("--incognito")
        elif profile:
            #NOTE: profile path must be absolute
            options.add_argument(f'user-data-dir={profile}')
        else: #create new profile
            if os.name == "nt": #if windows
                #TODO: pass
                pass
            else: #if os.name=="posix" (ie: linux)
                options.add_argument(f'user-data-dir={get_path("./data/chrome_profile")}')
                pass
        if headless: options.add_argument("--headless")
        if chrome_app_url:
            options.add_argument(f'--app={chrome_app_url}')
            if oem_manifest:
                options.add_argument(f"--app-mode-oem-manifest={oem_manifest}")
                options.add_argument(f"high-dpi-support=1")
                options.add_argument(f"force-device-scale-factor=1")
                # options.add_argument(f"--app-id=keknlipmpjbiecnnjjfloceplbfedjam")
        if disable_web_security:
            # options.add_argument("test-type")
            # options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--allow-insecure-localhost")
            options.add_argument("--allow-file-access-from-files")
            options.add_argument("--disable-login-animations")
        if full_screen: options.add_argument("--start-maximized")
        if grant_medial_access:
            options.add_argument("--use-fake-ui-for-media-stream=1")
        options.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent={userAgent}')
        options.add_argument('--no-sandbox')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-default-apps')
        options.add_argument('--force-dark-mode')
        #options.add_argument("--start-maximized")
        #options.add_argument(f'profile-directory="{os.getcwd()}/profile"')
        options.binary_location, executable_path = Driver.get_chrome_bin()

        driver = webdriver.Chrome(options=options, executable_path=executable_path)

        driver.js = driver.execute_script
        driver.wait = self.wait
        driver.timeout = self.timeout
        self.driver = driver

    @staticmethod
    def get_chrome_bin():
        if not Driver.chrome_driver:
            if os.name == "nt": #if windows
                Driver.chrome_bin = get_path('./app/asset/Chrome/Application/chrome.exe')
                Driver.chrome_driver = get_path('./app/asset/Chrome/Application/chromedriver.exe')
            else: #if os.name=="posix" (ie: linux)
                Driver.chrome_bin = get_path('./app/asset/chromium/chrome')
                Driver.chrome_driver = get_path('./app/asset/chromium/chromedriver')
        return [Driver.chrome_bin, Driver.chrome_driver]

    @staticmethod
    def get_driver():
        return Driver().driver
        
    def wait(self, timeout, EC, By, val):
        WebDriverWait(self.driver, timeout).until(EC((By, val)))

    def quit(self): self.driver.quit()


class Whatsapp:
    contact_eye = """
    (()=>{
        var a = document.createElement('a');
        a.href = "https://wa.me/{num}?text={msg}";
        document.body.appendChild(a);
        window.get_contact = (phone, msg="")=>{
            a.href = `https://wa.me/${phone}?text=${msg}`;
            a.click();
        }
    })();
    """
    whatsapp_web = 'https://web.whatsapp.com/'
    def __init__(self, profile=get_path("./data/browser_profile"), headless=False, userAgent=userAgent) -> None:
        g.wa = self
        self.driver = Driver(profile=profile, headless=headless, userAgent=userAgent, chrome_app_url=self.whatsapp_web).driver
        self.js = self.driver.js
        while True:
            try:
                self.driver.get(self.whatsapp_web)
                break
            except selenium.common.exceptions.WebDriverException as e:
                if "net::ERR_INTERNET_DISCONNECTED" in str(e):
                    print('TODO no internet error') #TODO
                    try:
                        if g.quit_now: exit()
                    except: pass
                    time.sleep(2.5)

        #check if QR code exists (if user not logged in)
        while True:
            try:
                inp_search = self.driver.wait(1, EC.presence_of_element_located, By.XPATH, '//div[@role="textbox"]')
                break
            except self.driver.timeout:
                try:
                    QR_code = self.driver.find_elements_by_class_name('landing-title')
                    if len(QR_code) == 0: raise self.driver.timeout()
                    else:
                        #TODO: ask the user to log in [:

                        #TODO: wait for qr_code to dissappear (ie: login process started)
                        unsafe(self.driver.wait, (999999, EC.invisibility_of_element_located, By.CLASS_NAME, "landing-title"))
                        self.driver.wait(999999, EC.invisibility_of_element_located, By.ID, "main")
                        inp_search = self.driver.wait(1, EC.presence_of_element_located, By.XPATH, '//div[@role="textbox"]')
                        break
                except self.driver.timeout:
                    pass
            time.sleep(2) # while loop truce
        self.js(Driver.jQuery)
        self.js(Whatsapp.contact_eye)

    def send_msg(self, num, msg) -> int:
        #close current chat
        chat_exists = self.driver.find_elements_by_xpath('//div[@id="main"]') != []
        if chat_exists:
            self.driver.js('''$("#main").find('span[data-icon="menu"]')[0].click();''')
            time.sleep(1) #fixme => untill dropdown menu open
            #btn_close_chat = driver.js('''window.btn_close_chat = $('div[aria-label="Close chat"]')[0]; return btn_close_chat;''')
            self.driver.js('''$('div[aria-label="Close chat"]')[0].click()''')
            #driver.js('''window.btn_close_chat.id = "btn_close_chat";''')
            #WebDriverWait(driver, 999999).until(EC.element_to_be_clickable((By.ID, "btn_close_chat")))
            #WebDriverWait(driver, 999999).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "btn_close_chat")))
            #btn_close_chat.click()
            self.driver.wait(999999, EC.invisibility_of_element_located, By.ID, "main")
        #print(f'get_contact("{num}", `{msg}`);') #FIXME: correct country code [modify num according to country]
        #dirver.quit()
        #exit()
        msg = msg.replace('\n', '%0A')
        self.driver.js(f'''get_contact("{num}", "{msg}");''')
        #FIXME: correct country code [modify num according to country]
        not_whatsapp_user = False
        while True: #time.sleep(0.5)
            try:
                WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]')))
                not_whatsapp_user = self.driver.js('return document.body.innerHTML.includes("Phone number shared via url is invalid.");') #False
                break
            except selenium.common.exceptions.TimeoutException:
                not_whatsapp_user = self.driver.js('return document.body.innerHTML.includes("Phone number shared via url is invalid.");')
                if not_whatsapp_user: break

        if not_whatsapp_user:
            # close the "Phone number shared via url is invalid." dialog
            time.sleep(0.5)
            self.driver.find_element_by_xpath('//div[@role="dialog"]').send_keys(Keys.ESCAPE)
            try: #check _starting_chat_bug
                WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located((By.XPATH, '//div[@role="dialog"]')))
            except selenium.common.exceptions.TimeoutException:
                _starting_chat_bug = self.driver.js('''return $('div[data-animate-modal-body="true"]')[0].innerHTML.includes("Starting chat");''')
                if _starting_chat_bug:
                    self.driver.find_element_by_xpath('//div[@role="dialog"]').send_keys(Keys.ESCAPE)
                    WebDriverWait(self.driver, 999999).until(EC.invisibility_of_element_located((By.XPATH, '//div[@role="dialog"]')))
            time.sleep(0.25) # wait untill current chat is closed
            return -1 #not_whatsapp_user
        inp_msg = WebDriverWait(self.driver, 999999).until(EC.presence_of_element_located((By.XPATH, '//div[@title="Type a message"]')))
        inp_msg.send_keys(Keys.ENTER)
        return 0
        #TODO:future: check that the correct contact has opened: $('#main').find('span[dir="auto"]')[0].innerHTML



#https://www.geeksforgeeks.org/share-whatsapp-web-without-scanning-qr-code-using-python/

# Test Email: kelgwlgwfmpvunuxkt@nthrw.com
# password: selenium
