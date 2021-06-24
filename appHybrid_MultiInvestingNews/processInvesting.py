import utils as tool
"""
processInvesting() fires the process to read https://www.investing.com/analysis/commodities
"""
def processInvesting():
    tool.readFromInvesting()
    
    

if __name__ == "__main__":
    processInvesting()