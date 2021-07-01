import utils as tool
import threading

def processInvestopedia():
    #options: market, trading
    try:
        tool.readFromInvestopedia('market')   
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processInvestopedia()