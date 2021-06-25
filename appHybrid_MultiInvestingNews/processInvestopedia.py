import utils as tool
import threading

"""
processInvestopedia() fires the process to read :

https://www.investopedia.com/markets-news-4427704
https://www.investopedia.com/trading-news-4689736

The urls already have the steps to read news

"""
def processInvestopedia():
    try:  
        threading.Thread(target=main_thread,args=[site]).start()
        tool.readFromInvestopedia()
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processInvestopedia()