import time
from utils import *



def main_thread_8(msg):
    BROWSER=returnChromeSettings()
    BROWSER.get(lsWebSite[7])
    for x in range(1,10):
        print(msg)
        time.sleep(2)
    print('Thread 1 done')   
    BROWSER.quit() 



if __name__ == "__main__":
    main_thread_8()    