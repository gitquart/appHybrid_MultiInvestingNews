import utils as tool

def processInvesting():
    try:
        print('-------Investing-------')
        tool.readFromInvesting()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processInvesting()