from thread_1 import *
from thread_2 import *
import threading

lsThreads=list()

x = threading.Thread(target=main_thread_1,args=['holi'])
y = threading.Thread(target=main_thread_2,args=['holi otra vez'])

lsThreads.append(x)
lsThreads.append(y)

for thread in lsThreads:
    thread.start()


for thread in lsThreads:
    thread.join()




print('All done')