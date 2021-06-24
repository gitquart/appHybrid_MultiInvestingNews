import utils as tool
"""
processDailyFX() fires the process to read https://www.dailyfx.com/
"""
def processDailyFX():
    tool.readFromDailyFX()
    
    

if __name__ == "__main__":
    processDailyFX()