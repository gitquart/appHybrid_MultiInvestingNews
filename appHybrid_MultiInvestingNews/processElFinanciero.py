import utils as tool

def processElFinanciero():
    try:
        print('-------El finaciero-------')
        tool.readFromElFinanciero()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processElFinanciero()