import utils as tool

def processDailyFX():
    try:
        print('-------Daily FX-------')
        tool.readFromDailyFX()
    except NameError as err:
        print(str(err))    
    

if __name__ == "__main__":
    processDailyFX()