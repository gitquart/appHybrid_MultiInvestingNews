import utils as tool
"""
processInvesting() fires the process to read https://cryptonews.com/news/bitcoin-news/
"""
def processCryptonews():
    try:
        tool.readFromCryptonews()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processCryptonews()