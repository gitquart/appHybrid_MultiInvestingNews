import utils as tool

def processCryptonews():
    try:
        print('-------Cryptonews-------')
        tool.readFromCryptonews()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processCryptonews()