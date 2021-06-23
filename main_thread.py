import time
from utils import *



def main_thread(name):
    BROWSER=returnChromeSettings()
    BROWSER.get(name)
    for x in range(1,10):
        print(name)
        time.sleep(2)
    print(name)   
    BROWSER.quit() 



if __name__ == "__main__":
    main_thread()    