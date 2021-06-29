import utils as tool

def processFXNews():
    try:
        print('-------FX News-------')
        tool.readFromFXNews()
    except NameError as err:
        print(str(err))    
    
    

if __name__ == "__main__":
    processFXNews()