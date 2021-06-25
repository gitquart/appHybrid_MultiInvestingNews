import utils as tool
import threading

"""
processInvestopediaMarket() fires the process to read :

https://www.investopedia.com/markets-news-4427704

The urls already have the steps to read news

"""
def processInvestopediaMarket():
    try:
        tool.readFromInvestopedia_Market()   
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processInvestopediaMarket()