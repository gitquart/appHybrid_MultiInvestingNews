from main_thread import *
import threading
from utils import *

lsThreads=list()

for site in lsWebSite:
    threading.Thread(target=main_thread,args=[site]).start()


      
    












