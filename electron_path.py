import os
if os.name == "nt": #if windows
    if __debug__:
        DEFAULT_CHROME_BINARY = (
            # get_path('./app/asset/electron-win/electron.exe'),
            # get_path('./app/asset/electron-win/chromedriver.exe')
            os.path.abspath(r'C:\Users\ibrahem\Desktop\electron-win\electron'),
            os.path.abspath(r'C:\Users\ibrahem\Desktop\electron-win\chromedriver')
        )
    else:
        DEFAULT_CHROME_BINARY = (
            # get_path('./app/asset/electron-win/electron.exe'),
            # get_path('./app/asset/electron-win/chromedriver.exe')
            os.path.abspath('./electron/electron'),
            os.path.abspath('./electron/chromedriver')
        )
else: #if os.name=="posix" (ie: linux)
    DEFAULT_CHROME_BINARY = (
        os.path.abspath('./electron/electron'),
        os.path.abspath('./electron/chromedriver')
    )