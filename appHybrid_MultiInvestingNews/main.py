import utils as tool


def main():
    try:
        mainOption='Investing'
        print(f'-------Reading from {mainOption}-------')
        if mainOption == 'Investing':
            tool.readFromInvesting()
        if mainOption == 'DailyFX':
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
            tool.readFromElFinanciero()                      
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    main()