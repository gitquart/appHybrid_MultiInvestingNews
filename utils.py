import os
from selenium import webdriver
import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from InternalControl import *

lsWebSite=['https://cryptonews.com/',
           'https://finance.yahoo.com/',
            'https://www.cnbc.com/',
            'https://www.dailyfx.com/',
            'https://www.fxstreet.com/',
            'https://www.elfinanciero.com.mx/',
            'https://www.advisorperspectives.com/',
             'https://www.investopedia.com/']

objControl= cInternalControl()

def returnChromeSettings():
    BROWSER=None
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")

    if objControl.heroku:
        #Chrome configuration for heroku
        options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
        BROWSER=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=options)
    else:
        BROWSER=webdriver.Chrome(options=options) 

    return BROWSER     