import utils as tool
"""
processInvesting() fires the process to read https://www.investing.com/analysis/commodities
"""
def processInvesting():
    try:
        tool.readFromInvesting()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processInvesting()