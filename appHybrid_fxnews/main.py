import utils as tool


def main():
    try:
        mainOption='fxnews'.lower()
        print(f'-------Reading from {mainOption}-------')
        if mainOption == 'investing':
            tool.readFromInvesting()
        if mainOption == 'dailyfx':
            #For demo
            tool.readFromDailyFX()
        if mainOption == 'investopedia':
            #options: market, trading
            tool.readFromInvestopedia('market') 
        if mainOption == 'cryptonews':
            tool.readFromCryptonews()
        if mainOption == 'yahoo':
            #Options : market, new
            tool.readFromYahoo('new')
        if mainOption == 'fxnews':
            tool.readFromFXNews() 
        if mainOption == 'financiero':
            #For demo
            tool.readFromElFinanciero()                      
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    main()