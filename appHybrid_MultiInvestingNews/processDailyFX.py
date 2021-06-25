import utils as tool
"""
processDailyFX() fires the process to read https://www.dailyfx.com/market-news/articles,
The url already has the steps to read news

"""
def processDailyFX():
    try:
        tool.readFromDailyFX()
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processDailyFX()