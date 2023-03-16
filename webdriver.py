
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import time, os
import tempfile
import subprocess as sp
import re
import psutil
# import signal

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
from .electron_path import DEFAULT_CHROME_BINARY
ELECTRON_INDEX_JS = """
const electron = require("electron");
const { app, BrowserWindow } = electron;
process.argv.forEach(function (val, index, array) {
  val = val.replace("--", "");
  if (val.includes("=")) {
    var [arg, val] = val.split("=");
    app.commandLine.appendSwitch(arg, val);
    if (arg == "user-data-dir") {
      app.setPath("userData", val);
    }
  } else {
    app.commandLine.appendArgument(val);
  }
});
app.on("ready", () => {
  let win = new BrowserWindow({ width: 800, height: 600, show: {isShown} });
  win.loadURL(`about:blank`);
});
"""
ELECTRON_INIT_ARGS = (
    "remote-debugging-port=0",
    "enable-blink-features=ShadowDOMV0",
    "password-store=basic",
    "test-type=webdriver",
    "log-level=0",
    "allow-pre-commit-input",
    "disable-background-networking",
    "disable-client-side-phishing-detection",
    "disable-default-apps",
    "disable-hang-monitor",
    "disable-popup-blocking",
    "disable-prompt-on-repost",
    "disable-sync",
    "enable-automation",
    "enable-logging",
    "no-first-run",
    "no-service-autorun",
    "use-mock-keychain"
    "no-sandbox"
    )

class Driver:
    # IMPORTANT NOTE: classes of this Driver must me saved to a var,
    #       otherwise: it will silently destroies when garbage collector deletes its reference
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
    optimization_cmdline_list = (
        '--no-default-browser-check',
        '--no-first-run', '--disable-gpu', '--disable-extensions',
        '--disable-default-apps', '--force-dark-mode',
        '--allow-outdated-plugins', '--disable-logging',
        '--disable-breakpad', '--enable-experimental-web-platform-features',
        '--new-canvas-2d-api', '--no-sandbox'
        )
    # timeout = TimeoutException
    chrome_bin = None
    chrome_driver = None
    chromedriver_service = None
    def __init__(self, incognito=False, profile=None, profile_directory=None, full_screen=False, disable_web_security=False, headless=False, chrome_app_url=None,  userAgent=userAgent, oem_manifest=None, grant_medial_access=False, chrome_binary=DEFAULT_CHROME_BINARY, is_electron=False, disable_http_cache=False) -> None:
        # chrome_binary is a tuple: (chrome_bin, chrome_driver)
        self.set_chrome_bin(chrome_binary)
        ##
        options = webdriver.ChromeOptions()
        self.temp_user_data_dir = False
        if incognito:
            options.add_argument("--incognito")
        elif profile:
            #NOTE: profile path must be absolute
            profile = os.path.abspath(profile)
            options.add_argument(f'--user-data-dir={profile}')
        else: #create new profile
            self.temp_user_data_dir = tempfile.TemporaryDirectory()
            options.add_argument(f'--user-data-dir={self.temp_user_data_dir.name}')
            if os.name == "nt": #if windows
                #TODO: pass
                pass
            else: #if os.name=="posix" (ie: linux)
                #TODO: pass
                pass
        if profile_directory:
            #options.add_argument(f'profile-directory="{os.getcwd()}/profile"')
            options.add_argument(f'--profile-directory=={profile_directory}')

        self.is_electron = is_electron
        if headless and not is_electron:
            options.add_argument("--headless")
        elif is_electron:
            self.temp_electron_index_js = tempfile.NamedTemporaryFile(prefix='electron.headless.', suffix='.index.js')
            self.temp_electron_index_js.write(ELECTRON_INDEX_JS.replace('{isShown}', ('false' if headless else 'true')).encode('utf-8'))
            self.temp_electron_index_js.flush()
            
        
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
        if userAgent:
            options.add_argument(f'user-agent={userAgent}')
        options.add_argument("--disable-notifications") # disable notifications
        if disable_http_cache:
            options.add_argument("--disable-http-cache")
            
            
        for i in Driver.optimization_cmdline_list:
            options.add_argument(i)
        options.add_argument("--start-maximized")
        
        chrome_binary = self.get_chrome_bin()
        if not is_electron:
            options.binary_location = chrome_binary[0]

        if Driver.chromedriver_service is None:
            Driver.chromedriver_service = Service(chrome_binary[1])
            if os.name == 'nt':
                Driver.chromedriver_service.creationflags = Driver.chromedriver_service.creation_flags = 0x08000000 # CREATE_NO_WINDOW = 0x08000000
        if is_electron:
            # get electron DevTools listening port
            electron_process = psutil.Popen((chrome_binary[0], self.temp_electron_index_js.name)+ELECTRON_INIT_ARGS+tuple(options.arguments), stdout=sp.PIPE, stderr=sp.STDOUT)
            while 1:
                line = electron_process.stdout.readline().decode()
                if '://' in line:
                    dev_tools_port = re.search(r':([0-9]+)/', line).group(1)
                    break
            electron_options = webdriver.ChromeOptions()
            electron_options.add_experimental_option("debuggerAddress", "127.0.0.1:"+dev_tools_port)
            driver = webdriver.Chrome(service=Driver.chromedriver_service, options=electron_options)
            # getting chrome process
            self.chrome_process = electron_process
            # self.chrome_process_psutil = psutil.P(electron_process.pid)
        else:
            driver = webdriver.Chrome(options=options, service=Driver.chromedriver_service)
            # getting chrome process
            self.chrome_process = psutil.Process(pid=driver.service.process.pid).children()[0]
        # inherit methods
        driver.js = driver.execute_script
        driver.wait = self.wait
        driver.wait4 = self.wait4
        self.driver = driver
        self.waiter = WebDriverWait(self.driver, 999999999, poll_frequency=1.0)

    def set_chrome_bin(self, chrome_binary):
        self.chrome_binary = chrome_binary

    def get_chrome_bin(self=None):
        if self:
            return self.chrome_binary
        else:
            return DEFAULT_CHROME_BINARY

    def get_driver(self):
        return self.driver
        
    def wait(self, timeout, EC, By, val):
        return WebDriverWait(self.driver, timeout).until(EC((By, val)))

    def wait4(self, EC, By, val): # wait without timeout for a condition
        while True:
            try:
                return self.waiter.until(EC((By, val)))
            except TimeoutException as e: 
                import traceback
                traceback.print_exc()

    def quit(self):
        self.driver.quit()
        self.cleanup()
        
    def cleanup(self):
        if self.temp_user_data_dir:
            self.temp_user_data_dir.cleanup()
        if self.is_electron:
            self.temp_electron_index_js.close()
        self.chrome_process.terminate()
        for p in self.chrome_process.children(recursive=True):
            try: p.kill()
            except psutil.NoSuchProcess: pass
        
        # os.kill(self.chrome_process.pid, signal.SIGKILL)

    def suspend(self):
        # os.kill(self.chrome_process.pid, signal.SIGSTOP)
        self.chrome_process.suspend()

    def resume(self):
        # os.kill(self.chrome_process.pid, signal.SIGCONT)
        self.chrome_process.resume()

    def sleep(self, seconds):
        time.sleep(seconds)

