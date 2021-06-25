import utils as tool
import threading

"""
processInvestopedia() fires the process to read :

https://www.investopedia.com/trading-news-4689736
https://www.investopedia.com/markets-news-4427704

The urls already have the steps to read news

"""
def processInvestopedia():
    #options: market, trading
    try:
        tool.readFromInvestopedia('trading')   
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processInvestopedia()