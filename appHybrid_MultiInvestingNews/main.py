import utils as tool


def main():
    try:
        mainOption='Financiero'
        print(f'-------Reading from {mainOption}-------')
        if mainOption == 'Investing':
            tool.readFromInvesting()
        if mainOption == 'DailyFX':
            #For demo
            tool.readFromDailyFX()
        if mainOption == 'Investopedia':
            #options: market, trading
            tool.readFromInvestopedia('market') 
        if mainOption == 'Cryptonews':
            tool.readFromCryptonews()
        if mainOption == 'Yahoo':
            #Options : market, new
            tool.readFromYahoo('market')
        if mainOption == 'FXNews':
            tool.readFromFXNews() 
        if mainOption == 'Financiero':
            #For demo
            tool.readFromElFinanciero()                      
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    main()