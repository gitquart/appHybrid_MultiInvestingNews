import utils as tool
"""
processDailyFX() fires the process to read https://www.dailyfx.com/market-news/articles

"""
def processDailyFX():
    try:
        tool.readFromDailyFX()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processDailyFX()