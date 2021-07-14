import utils as tool


def main():
    try:
        mainOption='yahoo'.lower()
        print(f'-------Reading from {mainOption}-------')
        if mainOption == 'investing':
            tool.readFromInvesting()
        if mainOption == 'dailyfx':
            #For demo
            tool.readFromDailyFX()
        if mainOption == 'investopedia':
            #options: market, trading
            tool.readFromInvestopedia('trading') 
        if mainOption == 'cryptonews':
            tool.readFromCryptonews()
        if mainOption == 'yahoo':
            #Options : market, new
            tool.readFromYahoo('market')
        if mainOption == 'fxnews':
            tool.readFromFXNews() 
        if mainOption == 'financiero':
            #For demo
            tool.readFromElFinanciero()                      
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    main()