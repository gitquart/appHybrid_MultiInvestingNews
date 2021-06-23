from time import time
from utils import *


def main_thread_2(msg):
    print(msg)
    BROWSER=returnChromeSettings()
    BROWSER.get('https://makina-corpus.com/blog/metier/2014/python-tutorial-understanding-python-threading')
    time.sleep(6)
    print('Thread 2 done') 



if __name__ == "__main__":
    main_thread_2()  