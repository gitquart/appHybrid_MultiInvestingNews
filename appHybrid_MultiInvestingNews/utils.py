import json
import os
from nltk import text, translate
from selenium import webdriver
import chromedriver_autoinstaller
import uuid
import time
from InternalControl import cInternalControl
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pandas as pd
from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk import tokenize
from deep_translator import GoogleTranslator
#from google_trans_new import google_translator
from translate import translator
from selenium.webdriver.common.keys import Keys
import html

BROWSER=''
objControl=cInternalControl()
nltk.download('stopwords')
#Start of Common items
lsStopWord_English = set(stopwords.words('english'))
lsStopWord_Spanish= set(stopwords.words('spanish'))
lsMyStopWords=['reuters','by','com','u','s','have','has','said','the','are','his','her','would','say','marketwatch',
                   'since','could','newsletters','nwe2050','nowbrokerstoolseconomic','comworldamericasperuscastilloleadselectionwith501votesafterallballotstallied20210615',
                   'etfsnysesiljsilxsinv','oilprice','ev','gm']
lsFinalStopWords=list(set(lsStopWord_English) | set(lsMyStopWords) | set(lsStopWord_Spanish) )
lsKeyWordsLimit=[20,30,35]
#lsContentCorpus and lsWordAllNews_WithNoSW  are elements for the TF IDF of a SET OF NEWS
lsContentCorpus=[]
lsWordAllNews_WithNoSW=[]
file_all_words='wholecorpus\\All_words_from_all_News.txt'
file_all_news='wholecorpus\\All_News.txt'
#dicWebSites sorted by importance
dicWebSite={
            #Start Ready
            'investing':'https://www.investing.com/news/commodities-news',
            'dailyfx': 'https://www.dailyfx.com/market-news/articles',
            'investopedia_market':'https://www.investopedia.com/markets-news-4427704',
            'investopedia_trading':'https://www.investopedia.com/trading-news-4689736',
            'cryptonews':'https://cryptonews.com/news/bitcoin-news/',
            #End Ready
            'yahoofinance_market':'https://finance.yahoo.com/topic/stock-market-news',
            'yahoofinance_news':'https://finance.yahoo.com/news',
            'cnbc':'https://www.cnbc.com/',
            'fxstreet':'https://www.fxstreet.com/',
            'financiero':'https://www.elfinanciero.com.mx/'
            }

#End of Common items

#Start of Investing.com items
lsSources=['Reuters','Investing.com','Bloomberg']
#End of Investing.com items


def returnChromeSettings():
    global BROWSER
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")
    prefs = {
      "translate_whitelists": {"en":"es"},
      "translate":{"enabled":"true"}
     }

    options.add_experimental_option("prefs", prefs)

    if objControl.heroku:
        #Chrome configuration for heroku
        options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
        BROWSER=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=options)
    else:
        BROWSER=webdriver.Chrome(options=options)  

        
def readFromInvesting():
    returnChromeSettings()
    time.sleep(4)
    for page in range(1,5):
        BROWSER.get(dicWebSite['investing']+'/'+str(page))
        lsArticle=BROWSER.find_elements_by_tag_name('article')
        no_art=len(lsArticle)
        print('Total of News: ',str(no_art))
        if no_art==0:
            print('No news, shutting down...')
            os.sys.exit(0)
        #Reading articles
        for article in lsArticle:
            idx=None
            idx=lsArticle.index(article)
            print(f'----------Start of Page {str(page)} New {str(idx+1)}-------------')
            #Check Source
            lsContent=[]
            strSource=''
            txtSource=''
            time.sleep(4)
            
            #For source: Those from "lsSource" list have "span", the rest have "div"
            try:
                txtSource=BROWSER.find_elements_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/span/span[1]')[0]
            except:
                try:
                    txtSource=BROWSER.find_elements_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/div/span[1]')[0]
                except:
                    print(f'----------End of Page {str(page)} New {str(idx+1)} (Most probable an ad or No content)-------------')
                    continue


            strSource=txtSource.text    
            strSource=strSource.split(' ')[1]
            print(f'Source :{strSource}')
            linkArticle=devuelveElemento(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/a')
            BROWSER.execute_script("arguments[0].click();",linkArticle)
            if strSource in lsSources:
                #Case: Sources which news open in Investing.com
                articleContent=devuelveElemento('/html/body/div[5]/section/div[3]')
                time.sleep(3)
                if articleContent:
                    lsContent.append(articleContent.text) 
            else:
                #---To know how many windows are open----
                time.sleep(4)
                linkPopUp=None
                #Get the link with a recursive method
                linkPopUp=devuelveElementoDinamico('/html/body/div[option]/div/div/div/a',6,15)
                time.sleep(3)
                if linkPopUp:
                    BROWSER.execute_script("arguments[0].click();",linkPopUp)
                time.sleep(3)
                secondWindowMechanism(lsContent,'/html/body')
                btnPopUpClose=None
                btnPopUpClose=devuelveElementoDinamico('/html/body/div[option]/span/i',6,15)
                time.sleep(3)
                if btnPopUpClose:
                    BROWSER.execute_script("arguments[0].click();",btnPopUpClose)
                 
            #START OF TF-IDF AND WORD CLOUD PROCESS
            generateKeyWordsAndWordCloudFromTFDIF(lsContent,page,idx+1,'news_analysis','images_wordcloud',False)
            #End of TF IDF - Keyword process
            

            print(f'----------End of Page {str(page)} New {str(idx+1)}-------------')
            if strSource in lsSources:
                #btnCommodity= devuelveElemento('/html/body/div[5]/section/div[1]/a')
                #BROWSER.execute_script("arguments[0].click();",btnCommodity)
                BROWSER.execute_script("window.history.go(-1)")      
            time.sleep(5)

        #For Loop : Pages    
        print(f'-End of page {str(page)}-')
        
        #At the end of the page, decide where to set the stop and generate the complete TF-IDF
        if page==4:
            print(f'Generating complete TF-IDF until page {str(page)}')
            BROWSER.quit()
            #START OF TF-IDF AND WORD CLOUD PROCESS
            generateKeyWordsAndWordCloudFromTFDIF(lsContentCorpus,None,None,'wholecorpus','wholecorpus',False)
            #End of TF IDF - Keyword process
            print('All td idf done...')
            os.sys.exit(0) 

          
        #query=f'update tbControl set page={str(page+1)} where id={str(objControl.idControl)}'
        #db.executeNonQuery(query)


def readFromDailyFX():
    returnChromeSettings()
    for page in range(1,4):
        BROWSER.get(dicWebSite['dailyfx']+'/'+str(page))
        time.sleep(3)
        lsNews=None
        lsNews=devuelveListaElementos('/html/body/div[5]/div/div[3]/div/div[1]/div[1]/a')
        #Get the news
        for objNew in lsNews:
            lsContent=list()
            hrefLink=objNew.get_attribute('href')
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            secondWindowMechanism(lsContent,'/html/body/div[5]/div/main/article/section/div/div[1]/div[1]/div')        
                 
        print('End of page')  
        BROWSER.quit()


def readFromInvestopedia(option):
    returnChromeSettings()
    time.sleep(4)
    if option=='market':
        BROWSER.get(dicWebSite['investopedia_market'])
    else:
        BROWSER.get(dicWebSite['investopedia_trading'])

    lsFirstCard=devuelveListaElementos('/html/body/main/div[1]/div[2]/section/ul/li')
    if lsFirstCard:
        for card in lsFirstCard:
            lsContent=list()
            idx=None
            linkNew=None
            idx= lsFirstCard.index(card)
            linkNew=devuelveElemento(f'/html/body/main/div[1]/div[2]/section/ul/li[{str(idx+1)}]/a')
            hrefLink=linkNew.get_attribute('href')
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            secondWindowMechanism(lsContent,'/html/body/main/div[2]/article/div[2]/div[1]')
             
    lsSecondCard=devuelveListaElementos('/html/body/main/div[2]/div[2]/ul/li')          
    if lsSecondCard:
        for card in lsSecondCard:
            lsContent=list()
            idx=None
            linkNew=None
            idx= lsSecondCard.index(card)
            linkNew=devuelveElemento(f'/html/body/main/div[2]/div[2]/ul/li[{str(idx+1)}]/a')
            hrefLink=linkNew.get_attribute('href')
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            secondWindowMechanism(lsContent,'/html/body/main/div[2]/article/div[2]/div[1]')

    #BROWSER.quit()
    
def readFromCryptonews():
    returnChromeSettings()
    BROWSER.get(dicWebSite['cryptonews'])
    #Wait for publishing to appear, they stop the reading
    time.sleep(10)
    btnLater= devuelveElemento('/html/body/div[5]/div/div/div[2]/button[2]')
    if btnLater:
        btnLater.click()
    BROWSER.switch_to.default_content()
    #First Section of News
    lsFirstSection=devuelveListaElementos('/html/body/div[2]/section[1]/div/div')
    for objNew in lsFirstSection:
        lsContent=list()
        linkNew=None
        idx= lsFirstSection.index(objNew)
        linkNew=devuelveElemento(f'/html/body/div[2]/section[1]/div/div[{str(idx+1)}]/a')
        hrefLink=linkNew.get_attribute('href')
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        secondWindowMechanism(lsContent,'/html/body/div[2]/article/div/div[2]')
        print(f'FIRST SECTION Ready: {str(idx+1)} ')

    #Second Section of News
    lsSecondSection=devuelveListaElementos('/html/body/div[2]/section[2]/div[1]/div')
    for objNew in lsSecondSection:
        lsContent=list()
        linkNew=None
        idx= lsSecondSection.index(objNew)
        linkNew=devuelveElemento(f'/html/body/div[2]/section[2]/div[1]/div[{str(idx+1)}]/a')
        hrefLink=linkNew.get_attribute('href')
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        secondWindowMechanism(lsContent,'/html/body/div[2]/article/div/div[2]')    
        print(f'SECOND SECTION Ready: {str(idx+1)} ')


def readFromYahoo(option):
    returnChromeSettings()
    time.sleep(4)
    strPathMainSection=None
    strLink=None
    if option=='market':
        BROWSER.get(dicWebSite['yahoofinance_market'])
        strPathMainSection='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li'
        strLink='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li[idx]/div/div/div[2]/h3/a'
    else:
        BROWSER.get(dicWebSite['yahoofinance_news']) 
        strPathMainSection='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li'
        strLink='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[2]/h3/a'
        strLink2='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[1]/h3/a'
        

    #Scroll down infinite loading page
    for x in range(1,200):
        BROWSER.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    #Main section of news
                                          
    lsMainSection=devuelveListaElementos(strPathMainSection)
    for objNew in lsMainSection:
        lsContent=list()
        linkNew=None
        idx= lsMainSection.index(objNew)
        #Cases: Market and New
        strLink=strLink.replace('idx',str(idx+1))     
        if option=='market':                  
            try:
                linkNew=BROWSER.find_element_by_xpath(strLink)
            except:
                print(f'I AM AN AD: {str(idx+1)} ')
                continue
        else:
            strLink2=strLink2.replace('idx',str(idx+1))
            try:
                linkNew=BROWSER.find_element_by_xpath(strLink)
            except:
                try:
                    linkNew=BROWSER.find_element_by_xpath(strLink2)
                except:    
                    print(f'I AM AN AD: {str(idx+1)} ')
                    continue
    
        hrefLink=linkNew.get_attribute('href')
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        secondWindowMechanism(lsContent,'html/body')
        print(f'FIRST SECTION Ready: {str(idx+1)} ')         


     

def secondWindowMechanism(lsContent,xPathElementSecondWindow):
    if len(BROWSER.window_handles)>1:
        bAd=False
        second_window=BROWSER.window_handles[1]
        BROWSER.switch_to.window(second_window)
        #Now in the second window
        time.sleep(5)
        #Get the text from second window and append it to lsContent
        strContent=None
        try:
            strContent=BROWSER.find_element_by_xpath(xPathElementSecondWindow)
        except NameError as error:
            bAd=True   
        if strContent and (not bAd):
            textContent=strContent.text
            lsContent.append(textContent) 
           
        #Close Window 2
        BROWSER.close()
        time.sleep(4)
        #Now in First window
        first_window=BROWSER.window_handles[0]
        BROWSER.switch_to.window(first_window)

def generateKeyWordsAndWordCloudFromTFDIF(lsContent,page,no_new,folderKeyword,folderImage,bPrintReport):
    #This implementation of code is based on : 
    # https://towardsdatascience.com/tf-idf-explained-and-python-sklearn-implementation-b020c5e83275
    strTop=''
    strBottom=''
    contentSize=len(lsContent)
    if contentSize>1:
        if bPrintReport:
            file_New_Keywords=folderKeyword+'\\wholecorpus_keyword.txt'  
            strTop='--------------Start of All news---------------------\n'  
            strBottom='--------------End of All news---------------------\n'
        lsContentToRead=None
    else:
        if bPrintReport:
            file_New_Keywords=folderKeyword+'\\NewAndKeywords_For_Page_'+str(page)+'_New_'+str(no_new)+'.txt'
            strTop=f'--------Start of Page {str(page)} New {str(no_new)} ---------------\n'
            strBottom=f'--------End of News {str(no_new)} ---------------\n'
        lsContentToRead=lsContent
    
    if bPrintReport:    
        printToFile(file_New_Keywords,strTop)
        printToFile(file_New_Keywords,f' News Content :\n')        
        for content in lsContentToRead:
            printToFile(file_New_Keywords,'********************************************************\n')
            printToFile(file_New_Keywords,content+'\n')
            printToFile(file_New_Keywords,'********************************************************\n')

    #Creating TF-IDF and its dataframe
    lsRes=[]
    lsRes=getDataFrameFromTF_IDF(lsContent,contentSize)
    df=lsRes[0]
    lsFeatures=lsRes[1]    
    for keywordsLimit in lsKeyWordsLimit:
        df_Sliced=df[:keywordsLimit]
        print('-------Analysis for ',str(keywordsLimit), 'keyword---------\n')
        if keywordsLimit>len(lsFeatures):
            print('The keywords limit is greater than the feature list')
            os.sys.exit(0)

        if bPrintReport:
            printToFile(file_New_Keywords,f'-------------------First {str(keywordsLimit)} Important Keywords--------------------\n')
            printToFile(file_New_Keywords,f'-------------------Word , Tf-idf value--------------------\n')
            
        dictWord_TF_IDF={}
        for row in df_Sliced.iterrows():
            line=str(row[1].name)+' , '+str(row[1].values[0])
            dictWord_TF_IDF[str(row[1].name)]=float(str(row[1].values[0]))
            if bPrintReport:
                printToFile(file_New_Keywords,line+'\n')
                
        #Create WorldCloud from any dictionary (Ex: Word, Freq; Word, TF-IDF,....{Word, AnyValue})
        if contentSize==1:
            image_file=folderImage+'\\image_page_'+str(page)+'_new_'+str(no_new)+'_'+str(keywordsLimit)+'_keyword.jpeg'
        else:
            image_file=folderImage+'\\wholecorpusImage_'+str(keywordsLimit)+'keyword.jpeg'    
        createWordCloud(image_file,dictWord_TF_IDF)
        #END OF TF-IDF AND WORD CLOUD PROCESS
            
        del dictWord_TF_IDF
        del df_Sliced
    del df    

    if bPrintReport:    
        printToFile(file_New_Keywords,strBottom)
                         
def pre_process_data(content):
    content = content.replace('.',' ')
    content = re.sub(r'\s+',' ',re.sub(r'[^\w \s]','',content)).lower()

    return content

def devuelveElementoDinamico(xPath,option,limit):
    try:
        if option==limit:
            print(f'Element was not find from {str(option)} to {str(limit)}')
            os.sys.exit(0)
        e=None
        newXPath=xPath.replace('option',str(option))
        e=BROWSER.find_elements_by_xpath(newXPath)[0]  
        time.sleep(3)
        if e:
            return e   
    except:
        option+=1
        devuelveElementoDinamico(xPath,option,limit)
                   
def createWordCloud(imageName,dictWord_Weight):
    wordcloud = WordCloud().generate_from_frequencies(dictWord_Weight)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f'{imageName}')
    del wordcloud
    
def getDataFrameFromTF_IDF(lsContent,contentSize):
    #Start of "FILTERING AND STOPWORDS"
    lsCorpus=[]
    lsVocabulary=[]
    lsVocabularyWithNoSW=[]
    if contentSize==1:
        for document in lsContent:
            data_preprocessed=pre_process_data(document)
            lsCorpus.append(data_preprocessed)
            lsContentCorpus.append(data_preprocessed)
            for word_token in tokenize.word_tokenize(data_preprocessed):
                lsVocabulary.append(word_token)
   
        #Remove Comple list of stop words 
        for word in lsVocabulary:
            if word not in lsFinalStopWords:
                lsVocabularyWithNoSW.append(word)
                #lsWordAllNews_WithNoSW si for the TF IDF with a set of NEWS
                lsWordAllNews_WithNoSW.append(word)

    #End of "FILTERING AND STOPWORDS"

    #fit_transform() returns
    #X sparse matrix of (n_samples, n_features)
    #Tf-idf-weighted document-term matrix.
    
    if contentSize>1:
        #Case: Full corpus
        if (not lsWordAllNews_WithNoSW) or (not lsContentCorpus):
            print('No vocabulary or content')
            os.sys.exit(0)
        vectorizer = TfidfVectorizer(vocabulary=list(set(lsWordAllNews_WithNoSW)))
        tf_idf_matrix = vectorizer.fit_transform(lsContentCorpus)
    else:
        #Case: Single document (New)
        if (not lsVocabularyWithNoSW) or (not lsCorpus):
            print('No vocabulary or content')
            os.sys.exit(0)
        vectorizer = TfidfVectorizer(vocabulary=list(set(lsVocabularyWithNoSW)))
        tf_idf_matrix = vectorizer.fit_transform(lsCorpus)

    
    """
    Solution for N dataset size
    Link https://towardsdatascience.com/tf-idf-explained-and-python-sklearn-implementation-b020c5e83275
    ------------------------------------------------
    tfIdfVectorizer=TfidfVectorizer(use_idf=True)
    tfIdf = tfIdfVectorizer.fit_transform(dataset)
    df = pd.DataFrame(tfIdf[0].T.todense(), index=tfIdfVectorizer.get_feature_names(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)
    """
    df=pd.DataFrame(tf_idf_matrix[0].T.todense(),index=vectorizer.get_feature_names(),columns=["TF-IDF"])
    df=df.sort_values('TF-IDF',ascending=False)
   
    
    return [df,vectorizer.get_feature_names()]      

def printToFile(completeFileName,content):
    with open(completeFileName, 'a',encoding='utf-8') as f:
        f.write(content)
    f.close()    
                                       
def devuelveJSON(jsonFile):
    with open(jsonFile) as json_file:
        jsonObj = json.load(json_file)
    
    return jsonObj 

def devuelveElemento(xPath):
    cEle=0
    while (cEle==0):
        cEle=len(BROWSER.find_elements_by_xpath(xPath))
        if cEle>0:
            ele=BROWSER.find_elements_by_xpath(xPath)[0]

    return ele  

def devuelveListaElementos(xPath):
    cEle=0
    while (cEle==0):
        cEle=len(BROWSER.find_elements_by_xpath(xPath))
        if cEle>0:
            ele=BROWSER.find_elements_by_xpath(xPath)

    return ele     




    