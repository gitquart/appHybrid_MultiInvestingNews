import utils as tool
import threading

"""
processInvestopedia() fires the process to read :

https://www.investopedia.com/trading-news-4689736

The urls already have the steps to read news

"""
def processInvestopediaTrading():
    try:
        tool.readFromInvestopedia_Trading()   
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processInvestopediaTrading()