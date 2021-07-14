import os

class cInternalControl(object):
    idControl=1
    timeout=70
    hfolder='appHybrid_MultiInvestingNews' 
    heroku=True
    rutaHeroku='/app/'+hfolder+'/'
    rutaLocal=os.getcwd()+'\\'+hfolder+'\\'
    download_dir=''
    
      