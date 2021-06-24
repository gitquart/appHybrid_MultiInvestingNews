import json
import os
from numpy import fabs
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
#lsWebSites sorted by importance
lsWebSite=['https://www.investing.com/news/commodities-news',
            'https://www.dailyfx.com/',
            'https://cryptonews.com/',
           'https://finance.yahoo.com/',
            'https://www.cnbc.com/',
            'https://www.fxstreet.com/',
            'https://www.elfinanciero.com.mx/',
            'https://www.advisorperspectives.com/',
             'https://www.investopedia.com/']

#End of Common items

#Start of Investing.com items
lsSources=['Reuters','Investing.com','Bloomberg']
#End of Investing.com items


def returnChromeSettings():
    global BROWSER
    chromedriver_autoinstaller.install()
    options = Options()
    options.add_argument("--no-sandbox")

    if objControl.heroku:
        #Chrome configuration for heroku
        options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        options.add_argument("--disable-dev-shm-usage")
        BROWSER=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=options)
    else:
        BROWSER=webdriver.Chrome(options=options)  


"""
readFromInvesting
-----------------
Reads from https://www.investing.com/analysis/commodities
"""
def readFromInvesting():
    try:
        returnChromeSettings()
        BROWSER.get(lsWebSite[0])
        time.sleep(4)
        for page in range(1,5):

            if page==4:
                BROWSER.quit()
                #Print all news
                printToFile(file_all_news,f'-------------------Printing  all news--------------------\n')
                for doc in lsContentCorpus:
                    printToFile(file_all_news,'*************************************************************\n')
                    printToFile(file_all_news,f'{doc}\n')
                    printToFile(file_all_news,'*************************************************************\n')


                #Print file "All words"
                printToFile(file_all_words,f'-------------------Printing All words from all news--------------------\n')
                for word in list(set(lsWordAllNews_WithNoSW)):
                    printToFile(file_all_words,f'{str(word)}\n')
         
                #Creating TF-IDF and its dataframe
                file_All_News_KeyWords='wholecorpus\\WholeCorpus_Keywords.txt'
                #Creating TF-IDF and its dataframe
                lsRes=[]
                lsRes=getDataFrameFromTF_IDF(fullCorpus=True)
                df=lsRes[0]
                lsFeatures=lsRes[1]
            
            
                for keywordsLimit in lsKeyWordsLimit:
                    df_Sliced=df[:keywordsLimit]
                    print('-------Analysis for ',str(keywordsLimit), 'keyword---------\n')
                    if keywordsLimit>len(lsFeatures):
                        print('The keywords limit is greater than the feature list')
                        os.sys.exit(0)

                    printToFile(file_All_News_KeyWords,f'-------------------First {str(keywordsLimit)} Important Keywords--------------------\n')
                    printToFile(file_All_News_KeyWords,f'-------------------Word , Tf-idf value--------------------\n')
            
                    dictWord_TF_IDF={}
                    for row in df_Sliced.iterrows():
                        line=str(row[1].name)+' , '+str(row[1].values[0])
                        dictWord_TF_IDF[str(row[1].name)]=float(str(row[1].values[0]))
                        printToFile(file_All_News_KeyWords,line+'\n')
                
                    #Create WorldCloud from any dictionary (Ex: Word, Freq; Word, TF-IDF,....{Word, AnyValue})
                    image_file='wholecorpus\\image_page_wholeCorpus_'+str(keywordsLimit)+'_keyword.jpeg'
                    createWordCloud(image_file,dictWord_TF_IDF)
                    #END OF TF-IDF AND WORD CLOUD PROCESS
            
                    del dictWord_TF_IDF
                    del df_Sliced
                #if page condition
                del df   
                print('All td idf done...')
                os.sys.exit(0) 
        
                   
            tag_article=BROWSER.find_elements_by_tag_name('article')
            no_art=len(tag_article)
            print('Total of News: ',str(no_art))
            if no_art==0:
                print('No news, shutting down...')
                os.sys.exit(0)
            #Reading articles
            for x in range(1,no_art+1):
                print(f'----------Start of Page {str(page)} New {str(x)}-------------')
                #Check Source
                lsContent=[]
                strSource=''
                txtSource=''
                time.sleep(4)
                #For source: Those from "lsSource" list have "span", the rest have "div"
                try:
                    txtSource=BROWSER.find_elements_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(x)}]/div[1]/span/span[1]')[0]
                except:
                    try:
                       txtSource=BROWSER.find_elements_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(x)}]/div[1]/div/span[1]')[0]
                    except:
                        print(f'----------End of Page {str(page)} New {str(x)} (Most probable an ad or No content)-------------')
                        continue


                strSource=txtSource.text    
                strSource=strSource.split(' ')[1]
                print(f'Source :{strSource}')
                linkArticle=devuelveElemento(f'/html/body/div[5]/section/div[4]/article[{str(x)}]/div[1]/a')
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
                    if len(BROWSER.window_handles)>1:
                        second_window=BROWSER.window_handles[1]
                        BROWSER.switch_to.window(second_window)
                        #Now in the second window
                        time.sleep(5)
                        textPage=devuelveElemento('/html/body')
                        lsContent.append(textPage.text)
                   
                        #Close Window 2
                        BROWSER.close()
                        time.sleep(4)
                        #Now in First window
                        first_window=BROWSER.window_handles[0]
                        BROWSER.switch_to.window(first_window)
                        #BROWSER.refresh()
                        btnPopUpClose=None
                        btnPopUpClose=devuelveElementoDinamico('/html/body/div[option]/span/i',6,15)
                        time.sleep(3)
                        if btnPopUpClose:
                            BROWSER.execute_script("arguments[0].click();",btnPopUpClose)
                   
                #This implementation of code is based on : 
                # https://towardsdatascience.com/tf-idf-explained-and-python-sklearn-implementation-b020c5e83275
            
                #START OF TF-IDF AND WORD CLOUD PROCESS
                file_New_Keywords='news_analysis\\NewAndKeywords_For_Page_'+str(page)+'_New_'+str(x)+'.txt'
                printToFile(file_New_Keywords,f'--------Start of Page {str(page)} New {str(x)} ---------------\n')
                printToFile(file_New_Keywords,f' News Content :\n')
                for content in lsContent:
                    printToFile(file_New_Keywords,content+'\n')

                #Creating TF-IDF and its dataframe
                lsRes=[]
                lsRes=getDataFrameFromTF_IDF(lsContent)
                df=lsRes[0]
                lsFeatures=lsRes[1]
                
                for keywordsLimit in lsKeyWordsLimit:
                    df_Sliced=df[:keywordsLimit]
                    print('-------Analysis for ',str(keywordsLimit), 'keyword---------\n')
                    if keywordsLimit>len(lsFeatures):
                        print('The keywords limit is greater than the feature list')
                        os.sys.exit(0)

                    printToFile(file_New_Keywords,f'-------------------First {str(keywordsLimit)} Important Keywords--------------------\n')
                    printToFile(file_New_Keywords,f'-------------------Word , Tf-idf value--------------------\n')
            
                    dictWord_TF_IDF={}
                    for row in df_Sliced.iterrows():
                        line=str(row[1].name)+' , '+str(row[1].values[0])
                        dictWord_TF_IDF[str(row[1].name)]=float(str(row[1].values[0]))
                        printToFile(file_New_Keywords,line+'\n')
                
                    #Create WorldCloud from any dictionary (Ex: Word, Freq; Word, TF-IDF,....{Word, AnyValue})
                    image_file='images_wordcloud\\image_page_'+str(page)+'_new_'+str(x)+'_'+str(keywordsLimit)+'_keyword.jpeg'
                    createWordCloud(image_file,dictWord_TF_IDF)
                    #END OF TF-IDF AND WORD CLOUD PROCESS
            
                    del dictWord_TF_IDF
                    del df_Sliced
                del df    
            
                printToFile(file_New_Keywords,f'-------------------End of News {str(x)}--------------------\n')
                print(f'----------End of Page {str(page)} New {str(x)}-------------')
                if strSource in lsSources:
                    #btnCommodity= devuelveElemento('/html/body/div[5]/section/div[1]/a')
                    #BROWSER.execute_script("arguments[0].click();",btnCommodity)
                    BROWSER.execute_script("window.history.go(-1)")      
                time.sleep(5)

            #Loop for : Pages    
            print(f'-End of page {str(page)}-')

            
            #query=f'update tbControl set page={str(page+1)} where id={str(objControl.idControl)}'
            #db.executeNonQuery(query)
            btnNext=BROWSER.find_elements_by_xpath('/html/body/div[5]/section/div[5]/div[3]/a')[0]
            if btnNext:
                BROWSER.execute_script("arguments[0].click();",btnNext)
              


    except NameError as error:
        print(str(error))    

def readFromDailyFX():
    print('yupi')

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
    
def getDataFrameFromTF_IDF(lsContent=None,fullCorpus=False):
    
    #Start of "some filtering"
    #I add up the Stopwords and some cutomized Stopwords (My stop words list)
    lsCorpus=[]
    lsVocabulary=[]
    lsVocabularyWithNoSW=[]
    if lsContent is not None:
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

    #End of "some filtering"

    #fit_transform() returns
    #X sparse matrix of (n_samples, n_features)
    #Tf-idf-weighted document-term matrix.
    
    if fullCorpus:
        if (not lsWordAllNews_WithNoSW) or (not lsContentCorpus):
            print('No vocabulary or content')
            os.sys.exit(0)
        vectorizer = TfidfVectorizer(vocabulary=list(set(lsWordAllNews_WithNoSW)))
        tf_idf_matrix = vectorizer.fit_transform(lsContentCorpus)
    else:
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
    print (df.head(25))
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




    