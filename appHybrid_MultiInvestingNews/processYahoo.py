import utils as tool

def processYahoo():
    #Options : market, new
    try:
        print('-------Yahoo-------')
        tool.readFromYahoo('market')
    except NameError as err:
        print(str(err))    
    
    
if __name__ == "__main__":
    processYahoo()