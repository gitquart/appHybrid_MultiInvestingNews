import utils as tool
"""
processDailyFX() fires the process to read https://www.dailyfx.com/market-news/articles
"""
def processDailyFX():
    tool.readFromDailyFX()
    
    

if __name__ == "__main__":
    processDailyFX()