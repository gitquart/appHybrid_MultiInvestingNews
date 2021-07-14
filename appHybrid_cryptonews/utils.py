import json
import os
from selenium import webdriver
import chromedriver_autoinstaller
import time
from InternalControl import cInternalControl
from selenium.webdriver.chrome.options import Options
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import pandas as pd
from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk import tokenize
#Deep Google translator
from deep_translator import GoogleTranslator
from selenium.webdriver.common.keys import Keys
import base64
from datetime import date, datetime, timedelta
import postgresql as bd


BROWSER=''
formatTimeForPostgreSQL='%Y-%m-%d %H:%M'
objControl=cInternalControl()
nltk.download('stopwords')
nltk.download('punkt')
#Start of Common items
lsStopWord_English = set(stopwords.words('english'))
lsStopWord_Spanish= set(stopwords.words('spanish'))
print(f'Size of english stopwords: {str(len(lsStopWord_English))}')
print(f'Size of spanish stopwords: {str(len(lsStopWord_Spanish))}')
lsMyStopWords=['reuters','by','com','u','s','have','has','said','the','are','his','her','would','say','marketwatch',
                   'since','could','newsletters','nwe2050','nowbrokerstoolseconomic','comworldamericasperuscastilloleadselectionwith501votesafterallballotstallied20210615',
                   'etfsnysesiljsilxsinv','oilprice','ev','gm','also']
lsFinalStopWords=list(set(lsStopWord_English) | set(lsMyStopWords) | set(lsStopWord_Spanish) )
lsKeyWordsLimit=[20,30,35]
#lsContentCorpus and lsWordAllNews_WithNoSW  are elements for the TF IDF of a SET OF NEWS
lsContentCorpus=[]
lsWordAllNews_WithNoSW=[]
file_all_words='wholecorpus\\All_words_from_all_News.txt'
file_all_news='wholecorpus\\All_News.txt'
#dicWebSites sorted by importance
dicWebSite={
            
            'investing':'https://www.investing.com/news/commodities-news', #pager
            'dailyfx': 'https://www.dailyfx.com/market-news/articles', #pager
            'investopedia_market':'https://www.investopedia.com/markets-news-4427704', #no pager
            'investopedia_trading':'https://www.investopedia.com/trading-news-4689736', #no pager
            'cryptonews':'https://cryptonews.com/news/bitcoin-news/', #no pager
            'yahoofinance_market':'https://finance.yahoo.com/topic/stock-market-news', #no pager
            'yahoofinance_news':'https://finance.yahoo.com/news', #no pager
            'fxstreet':'https://www.fxstreet.com/news', #pager
            'financiero':'https://www.elfinanciero.com.mx/mercados/' #no pager
            
            
            }

dictCommodity={

    'oil':['crude oil','oil','brent','petróleo','wti','west texas intermediate','barril','opep'],
    'gold':['gold','oro','metales preciosos','xau','wgc','comex'],
    'silver':['silver','plata','metales preciosos','xag'],
    'copper':['copper','cobre','metales industriales','hg'],
    'coffee':['coffee','café','kc','arábica','ice/us']
}


#Start PostgreSQL fields for all news
fieldCommodity=None  
fieldBase64NewContent=None 
fieldTimeStamp=None
fieldListOfKeyWordsOriginal=None
fieldListOfKeyWordsTranslated=None
fieldTitle=None
fieldUrl=None
fieldSourceSite=None 
appName=None
#End PostgreSQL fields for all news

#End of Common items

#Start of Investing.com items
lsSources=['Reuters','Investing.com','Bloomberg']
lsChar=['"',"'"]
#End of Investing.com items

#R stands for READY
#R      
def readFromInvesting():
    returnChromeSettings()
    iam='Investing.com'
    print(f'Starting reading {iam}...')
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
            lsContentOriginal=list()
            lsContentTranslated=list()
            strTitle=None
            strSource=None
            txtDateFilter=None
            strDateFilter=None
            txtSource=None
            linkArticle=None
            strDate=None
            #Start - PostgreSQL fields
            global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
            global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName
            fieldTimeStamp=None
            fieldBase64NewContent=None
            fieldCommodity=None
            fieldListOfKeyWordsOriginal=None
            fieldListOfKeyWordsTranslated=None
            fieldTitle=None
            fieldUrl=None
            fieldSourceSite=None
            appName=iam
            #End -  PostgreSQL Fields
            time.sleep(4)
            #For source: Those from "lsSource" list have "span", the rest have "div"
            #DO  NOT use "devuelveElemento" on "txtSource" because it can be an Ad, if it's an Ad then it would be
            #forever looping
            try:
                txtSource=BROWSER.find_element_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/span/span[1]')
                txtDateFilter=BROWSER.find_element_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/span/span[2]')
            except:
                try:
                    txtSource=BROWSER.find_element_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/div/span[1]')
                    txtDateFilter=BROWSER.find_element_by_xpath(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/div/span[2]')
                except:
                    print(f'----------End of Page {str(page)} New {str(idx+1)} (Most probable an ad or No content)-------------')
                    continue
            #To know if the new is from today, we got to check if the word "ago" is in the date string
            # If not, continue to next new...    
            if txtDateFilter:
                strDateFilter=txtDateFilter.text
                if 'ago' not in strDateFilter:
                    continue

            if txtSource:
                strSource=txtSource.text  
                strSource=str(strSource.replace('By','')).strip() 
                fieldSourceSite= strSource
                print(f'Source :{strSource}')
                
            linkArticle=devuelveElemento(f'/html/body/div[5]/section/div[4]/article[{str(idx+1)}]/div[1]/a')
            fieldUrl=linkArticle.get_attribute('href')
            BROWSER.execute_script("arguments[0].click();",linkArticle)
            #Start of field Time setting
            #If the code reaches so far, then the date is TODAY for both cases of Source
            # And I will always substract the hours or minutes from the current Date
            # Format code : %d , %m , %Y %H:%M:%S
            #For timestamp in PostgreSQL I need it as "YYYY-M-D HH:MM pm/am"
            #Get the time of the new by substracting "hrs or mins ago" to Current Central Time
            #strDate example : '- 1 hour ago, - 23 minutes ago'
            strDate=strDateFilter.strip() 
            date_time_new=None
            #Get hours or minutes to substract from current time
            chunks=strDate.split(' ')
            intAmountToSubstract=int(chunks[1])
            if 'hour' in strDate:
                date_time_new=datetime.now() - timedelta(hours=intAmountToSubstract)
            if 'minute' in strDate:
                date_time_new=datetime.now() - timedelta(minutes=intAmountToSubstract)  

            # https://strftime.org/ : This format %Y-%m-%d %H:%M gets 24 hour based.
            fieldTimeStamp = date_time_new.strftime(formatTimeForPostgreSQL)   
              
            #End of field Time setting
            if strSource in lsSources:
                articleContent=None
                articleTitle=None
                #Case: Sources which news open in Investing.com platform
                articleContent=devuelveElemento('/html/body/div[5]/section/div[3]')
                articleTitle=BROWSER.find_element_by_class_name('articleHeader')
                strTitle=getTitleClean(articleTitle.text)
                fieldCommodity=getCommodity(strTitle.lower(),dictCommodity)
                fieldTitle=strTitle
                time.sleep(3)
                if articleContent:
                    sourceText=None
                    sourceText=articleContent.text
                    lsResult=list()
                    lsResult=getSourceAndTranslatedText(sourceText,'es')
                    if lsResult:
                        lsContentOriginal.append(lsResult[0])
                        lsContentTranslated.append(lsResult[1])
                    else:
                        print(f'New already in database. App: {appName}')
                        BROWSER.execute_script("window.history.go(-1)")
                        continue    
            else:
                #---To know how many windows are open----
                time.sleep(4)
                linkPopUp=None
                linkPopUp=BROWSER.find_element_by_partial_link_text('Continue Reading')
                fieldUrl=linkPopUp.get_attribute('href')
                time.sleep(3)
                if linkPopUp:
                    BROWSER.execute_script("arguments[0].click();",linkPopUp)
                time.sleep(3)
                res=None
                res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body','es')
                btnPopUpClose=None
                btnPopUpClose=BROWSER.find_element_by_class_name('closeIconBlack')
                time.sleep(3)
                if btnPopUpClose:
                    BROWSER.execute_script("arguments[0].click();",btnPopUpClose)

                if not res:
                    print(f'New already in database. App: {appName}')
                    continue    
                 
            #START OF TF-IDF - keyword process
            df_tfidf_original=None
            df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
            fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
            del df_tfidf_original
            
            df_tfidf_translated=None
            df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
            fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
            del df_tfidf_translated
            #End of TF IDF - Keyword process

            #Start of PostgreSQL New Insertion
            insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
            #End of PostgreSQL New Insertion
            
            print(f'----------End of New {str(idx+1)} on Page {str(page)}-------------')
            if strSource in lsSources:
                BROWSER.execute_script("window.history.go(-1)")      
            time.sleep(5)

        #For Loop : Pages    
        print(f'-End of page {str(page)}-')
    #When all the pages in the loop are done    
    BROWSER.quit()
#R 
def readFromDailyFX():
    returnChromeSettings()
    iam='DailyFx'
    print(f'Starting reading {iam}...')
    for page in range(1,4):
        BROWSER.get(dicWebSite['dailyfx']+'/'+str(page))
        time.sleep(3)
        lsNews=None
        lsNews=devuelveListaElementos('/html/body/div[5]/div/div[3]/div/div[1]/div[1]/a')
        #Get the news
        for objNew in lsNews:
            #Start - PostgreSQL fields
            global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
            global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName
            fieldTimeStamp=None
            fieldBase64NewContent=None
            fieldCommodity=None
            fieldListOfKeyWordsOriginal=None
            fieldListOfKeyWordsTranslated=None
            fieldTitle=None
            fieldUrl=None
            fieldSourceSite=None
            appName=iam
            fieldSourceSite=appName
            #End -  PostgreSQL Fields
            #Start local variables
            lsContentOriginal=list()
            lsContentTranslated=list()
            txtDateTime=None
            #End local variables
            idx=lsNews.index(objNew)
            #Filter by todays' news
            txtDateTime=BROWSER.find_element_by_xpath(f'/html/body/div[5]/div/div[3]/div/div[1]/div[1]/a[{str(idx+1)}]/div/div[1]/span')
            txtDateTime=txtDateTime.get_attribute('data-time')
            today=None
            today=datetime.now().strftime('%Y-%m-%d')
            #If not todays' news, go to next new
            if today != str(txtDateTime).split('T')[0]:
                continue
            #If code reaches this line, therefore is a today's new, keep going with process
            fieldTimeStamp=str(txtDateTime[0:16]).replace('T',' ')
            #Get Title & Commodity     
            hrefLink=objNew.get_attribute('href')
            fieldUrl=hrefLink
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/div[5]/div/main/article/section/div/div[1]/div[1]/div','es')  

            if not res:
                print(f'New already in database. App: {appName}')
                continue  
             
            #START OF TF-IDF - keyword process
            df_tfidf_original=None
            df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
            fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
            del df_tfidf_original

            df_tfidf_translated=None
            df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
            fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
            del df_tfidf_translated
            #End of TF IDF - Keyword process

            #Start of PostgreSQL New Insertion
            insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
            #End of PostgreSQL New Insertion
                            
        print(f'End of page {str(page)}')  
        
    BROWSER.quit()

#R
def readFromInvestopedia(option):
    returnChromeSettings()
    iam=f'Investopedia {option}'
    print(f'Starting reading {iam}...')
    time.sleep(4)
    if option=='market':
        BROWSER.get(dicWebSite['investopedia_market'])
    else:
        BROWSER.get(dicWebSite['investopedia_trading'])

    global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
    global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName  
    #Start - PostgreSQL fields
    fieldBase64NewContent=None
    fieldCommodity=None
    fieldListOfKeyWordsOriginal=None
    fieldListOfKeyWordsTranslated=None
    fieldTitle=None
    fieldUrl=None
    fieldSourceSite=None
    fieldTimeStamp=None
    appName=None
    #End -  PostgreSQL Fields  
    appName=iam
    fieldSourceSite=appName
    #Investopedia, for Market & trading , news don't have DATE or TIME, hence add current DateTime
    today=None
    today=datetime.now().strftime(formatTimeForPostgreSQL)
    fieldTimeStamp=today
    #Get the first Main New
    #Start local variables
    lsContentOriginal=list()
    lsContentTranslated=list()
    #End local variables
    linkNew=None
    linkNew=BROWSER.find_element_by_xpath('/html/body/main/div[1]/div[2]/section/a')
    hrefLink=linkNew.get_attribute('href')
    fieldUrl=hrefLink
    BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
    res=None
    res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/main/div[2]/article/div[2]/div[1]','es')
    if not res:
        print(f'New already in database. App: {appName}')
    else:
        #START OF TF-IDF - keyword process
        df_tfidf_original=None
        df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
        fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
        del df_tfidf_original
        
        df_tfidf_translated=None
        df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
        fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
        del df_tfidf_translated
        #End of TF IDF - Keyword process

        #Start of PostgreSQL New Insertion
        insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
        #End of PostgreSQL New Insertion


    lsFirstCard=devuelveListaElementos('/html/body/main/div[1]/div[2]/section/ul/li')
    if lsFirstCard:
        for card in lsFirstCard:
            #Start - PostgreSQL fields
            fieldBase64NewContent=None
            fieldCommodity=None
            fieldListOfKeyWordsOriginal=None
            fieldListOfKeyWordsTranslated=None
            fieldTitle=None
            fieldUrl=None
            fieldSourceSite=None
            fieldSourceSite=appName
            #End -  PostgreSQL Fields
            #Start local variables
            lsContentOriginal=list()
            lsContentTranslated=list()
            #End local variables
            linkNew=None
            linkNew=card.find_element_by_xpath('.//a')
            hrefLink=linkNew.get_attribute('href')
            fieldUrl=hrefLink
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            res=None
            res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/main/div[2]/article/div[2]/div[1]','es')
            if not res:
                print(f'New already in database. App: {appName}')
            else:
                #START OF TF-IDF - keyword process
                df_tfidf_original=None
                df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
                fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
                del df_tfidf_original
                
                df_tfidf_translated=None
                df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
                fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
                del df_tfidf_translated

                #End of TF IDF - Keyword process
                #Start of PostgreSQL New Insertion
                insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
                #End of PostgreSQL New Insertion
             
    lsSecondCard=devuelveListaElementos('/html/body/main/div[2]/div[2]/ul/li')          
    if lsSecondCard:
        for card in lsSecondCard:
            #Start - PostgreSQL fields
            fieldBase64NewContent=None
            fieldCommodity=None
            fieldListOfKeyWordsOriginal=None
            fieldListOfKeyWordsTranslated=None
            fieldTitle=None
            fieldUrl=None
            fieldSourceSite=None
            fieldSourceSite=appName
            #End -  PostgreSQL Fields
            #Start local variables
            lsContentOriginal=list()
            lsContentTranslated=list()
            #End local variables
            linkNew=None
            linkNew=card.find_element_by_xpath('.//a')
            hrefLink=linkNew.get_attribute('href')
            fieldUrl=hrefLink
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            res=None
            res=secondWindowMechanism(lsContentOriginal,'/html/body/main/div[2]/article/div[2]/div[1]','es')
            if not res:
                print(f'New already in database. App: {appName}')
            else:
                #START OF TF-IDF - keyword process
                
                df_tfidf_original=None
                df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
                fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
                del df_tfidf_original
                
                df_tfidf_translated=None
                df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
                fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
                del df_tfidf_translated

                #End of TF IDF - Keyword process
                #Start of PostgreSQL New Insertion
                insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
                #End of PostgreSQL New Insertion

    BROWSER.quit()

#R    
def readFromCryptonews():
    returnChromeSettings()
    iam='Cryptonews'
    print(f'Starting reading {iam}...')
    BROWSER.get(dicWebSite['cryptonews'])
    print('Browser ready...')
    #Wait for publishing to appear, they stop the reading
    time.sleep(10)
    btnLater= devuelveElemento('/html/body/div[5]/div/div/div[2]/button[2]')
    if btnLater:
        btnLater.click()
    BROWSER.switch_to.default_content()
    print('Reading the main window...')
    global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
    global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName  
    #Start - PostgreSQL fields
    fieldBase64NewContent=None
    fieldCommodity=None
    fieldListOfKeyWordsOriginal=None
    fieldListOfKeyWordsTranslated=None
    fieldTitle=None
    fieldUrl=None
    fieldSourceSite=None
    fieldTimeStamp=None
    appName=None
    #End -  PostgreSQL Fields  
    appName=iam
    fieldSourceSite=appName
    #First Section of News
    lsFirstSection=devuelveListaElementos('/html/body/div[2]/section[1]/div/div')
    for objNew in lsFirstSection:
        lsContentOriginal=list()
        lsContentTranslated=list()
        idx=lsFirstSection.index(objNew)
        #Get time
        txtDate=None
        strDate=None
        try:
            txtDate=BROWSER.find_element_by_xpath(f'/html/body/div[2]/section[1]/div/div[{str(idx+1)}]/div/span/i/time')
            strDate=txtDate.get_attribute('datetime')
            print(f'DateTime of current new: {strDate}')
            today=None
            today=datetime.now().strftime('%Y-%m-%d')
            #If not todays' news, go to next new
            if today != str(strDate).split('T')[0]:
                print('Current new is not from today, next...')
                continue
            strDate=str(strDate[0:16]).replace('T',' ')
        except:
            strDate=datetime.now().strftime(formatTimeForPostgreSQL)

        fieldTimeStamp=strDate    
        linkNew=None
        linkNew=objNew.find_element_by_xpath('.//a')
        hrefLink=linkNew.get_attribute('href')
        fieldUrl=hrefLink
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        res=None
        res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/div[2]/article/div/div[2]','es')
        if not res:
            print(f'New already in database. App: {appName}')
        else:
            #START OF TF-IDF - keyword process

            df_tfidf_original=None
            df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
            fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
            del df_tfidf_original

            df_tfidf_translated=None
            df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
            fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
            del df_tfidf_translated

            #End of TF IDF - Keyword process
            #Start of PostgreSQL New Insertion
            insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
            #End of PostgreSQL New Insertion
        

    #Second Section of News
    lsSecondSection=devuelveListaElementos('/html/body/div[2]/section[2]/div[1]/div')
    for objNew in lsSecondSection:
        lsContentOriginal=list()
        lsContentTranslated=list()
        idx=lsFirstSection.index(objNew)
        #Get time
        txtDate=None
        strDate=None
        try:
            txtDate=BROWSER.find_element_by_xpath(f'/html/body/div[2]/section[1]/div/div[{str(idx+1)}]/div/span/i/time')
            strDate=txtDate.get_attribute('datetime')
            today=None
            today=datetime.now().strftime('%Y-%m-%d')
            #If not todays' news, go to next new
            if today != str(strDate).split('T')[0]:
                continue
            strDate=str(strDate[0:16]).replace('T',' ')
        except:
            strDate=datetime.now().strftime(formatTimeForPostgreSQL)

        fieldTimeStamp=strDate    
        linkNew=None
        linkNew=objNew.find_element_by_xpath('.//a')
        hrefLink=linkNew.get_attribute('href')
        fieldUrl=hrefLink
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        res=None
        res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/div[2]/article/div/div[2]','es')
        if not res:
            print(f'New already in database. App: {appName}')
        else:
            #START OF TF-IDF - keyword process

            df_tfidf_original=None
            df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
            fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
            del df_tfidf_original

            df_tfidf_translated=None
            df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
            fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
            del df_tfidf_translated

            #End of TF IDF - Keyword process
            #Start of PostgreSQL New Insertion
            insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
            #End of PostgreSQL New Insertion  

    #End of all sections        
    BROWSER.quit()        

#R
def readFromYahoo(option):
    returnChromeSettings()
    iam=f'Yahoo {option}'
    print(f'Starting reading {iam}...')
    time.sleep(4)
    strPathMainSection=None
    strWebSite=None
    lsTime=list()
    lsLink=list()
    if option=='market':
        strWebSite=dicWebSite['yahoofinance_market']
        strPathMainSection='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li'
        lsLink.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li[idx]/div/div/div[1]/h3/a')
        lsLink.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li[idx]/div/div/div[2]/h3/a')
        lsTime.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li[idx]/div/div/div[1]/div[2]/span[2]')
        lsTime.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[3]/div/div/div/ul/li[idx]/div/div/div[2]/div[2]/span[2]')
    else:
        strWebSite=dicWebSite['yahoofinance_news'] 
        strPathMainSection='/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li'
        lsLink.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[2]/h3/a')
        lsLink.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[1]/h3/a')
        lsTime.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[1]/div[2]/span[2]')
        lsTime.append('/html/body/div[1]/div/div/div[1]/div/div[3]/div[1]/div/div[2]/div/div/div/ul/li[idx]/div/div/div[2]/div[2]/span[2]')
        
    BROWSER.get(strWebSite)
    #Scroll down infinite loading page
    for x in range(1,200):
        BROWSER.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    #Main section of news
    time.sleep(5)  
    global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
    global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName  
    #Start - PostgreSQL fields
    fieldBase64NewContent=None
    fieldCommodity=None
    fieldListOfKeyWordsOriginal=None
    fieldListOfKeyWordsTranslated=None
    fieldTitle=None
    fieldUrl=None
    fieldSourceSite=None
    fieldTimeStamp=None
    appName=None
    #End -  PostgreSQL Fields  
    appName=iam
    fieldSourceSite=appName                                    
    lsMainSection=devuelveListaElementos(strPathMainSection)
    for objNew in lsMainSection:
        strLinkTime=None
        lsContentOriginal=list()
        lsContentTranslated=list()
        linkNew=None
        linkTime=None
        idx= lsMainSection.index(objNew)
        #Try -catch for  the time
        for strTime in lsTime:
            try:
                linkTime=BROWSER.find_element_by_xpath(str(strTime).replace('idx',str(idx+1)))
                if linkTime:
                    strLinkTime=linkTime.text  
                    break  
            except:    
                continue

        #Try -catch for the link  
        for strLink in lsLink:             
            try:
                linkNew=BROWSER.find_element_by_xpath(str(strLink).replace('idx',str(idx+1)))
            except:
                continue

        if (linkTime is None) and (linkNew is None):
            print('This is high probable and ADVERTISEMENT...')
            continue        

        #Check if it's today new, if not continue with the next new...
        if 'ago' not in strLinkTime:
            continue

        strMeasure=None
        strMeasure=strLinkTime.split(' ')[1]
        intQuantity=None
        intQuantity=int(strLinkTime.split(' ')[0])
        date_time_new=None
        if 'minute' in strMeasure:
            #Case: minutes
            date_time_new=datetime.now() - timedelta(minutes=intQuantity)
        else:
            #Case: hours  
            date_time_new=datetime.now() - timedelta(hours=intQuantity)  

        fieldTimeStamp=date_time_new.strftime(formatTimeForPostgreSQL)    
        hrefLink=linkNew.get_attribute('href')
        fieldUrl=hrefLink
        BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
        res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'html/body','es')
        if not res:
            print(f'New already in database. App: {appName}')
        else:
            #START OF TF-IDF - keyword process

            df_tfidf_original=None
            df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
            fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
            del df_tfidf_original

            df_tfidf_translated=None
            df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
            fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
            del df_tfidf_translated

            #End of TF IDF - Keyword process
            #Start of PostgreSQL New Insertion
            insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
            #End of PostgreSQL New Insertion

#R              
def readFromFXNews():
    returnChromeSettings()
    iam='FXNews'
    print(f'Starting reading {iam}...')
    BROWSER.get(dicWebSite['fxstreet'])
    lsMonth=['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dic']
    for page in range(1,7):
        #7h page is enough to get the news of TODAY
        secs=15
        print(f'Waiting banner to disappear...{str(secs)} secs')
        time.sleep(secs)      
        global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
        global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName  
        #Start - PostgreSQL fields
        fieldBase64NewContent=None
        fieldCommodity=None
        fieldListOfKeyWordsOriginal=None
        fieldListOfKeyWordsTranslated=None
        fieldTitle=None
        fieldUrl=None
        fieldSourceSite=None
        fieldTimeStamp=None
        appName=None
        #End -  PostgreSQL Fields  
        appName=iam
        fieldSourceSite=appName
        #Main section of News
        lsMainSection=devuelveListaElementos('/html/body/div[4]/div[2]/div/div/div/main/div/div[2]/div[1]/div/div[2]/div/div[2]/section/div/div/div/main/div/div')
        for objNew in lsMainSection:
            idx=lsMainSection.index(objNew)
            lsContentOriginal=list()
            lsContentTranslated=list()
            hrefLink=None
            #Get date
            txtDate=None
            strDate=None
            bFailTimeLink=False
            try:
                txtDate=BROWSER.find_element_by_xpath(f'/html/body/div[4]/div[2]/div/div/div/main/div/div[2]/div[1]/div/div[2]/div/div[2]/section/div/div/div/main/div/div[{str(idx+1)}]/div/div/article/div[2]/address/time')  
                if txtDate:
                    strDate=txtDate.text  
            except:    
                #Set the current system time
                strDate=datetime.now().strftime(formatTimeForPostgreSQL)
                bFailTimeLink=True

            #Cases for setting time and date
            try:
                if not bFailTimeLink:
                    measureTime=None
                    intQuantity=None
                    #Case: When 'ago' in in the sentence
                    if 'ago' in strDate:
                        measureTime=strDate.split(' ')[1] 
                        intQuantity=int(strDate.split(' ')[0])
                        date_time_new=None
                        if 'minute' in measureTime:
                            date_time_new=datetime.now() - timedelta(minutes=intQuantity)
                        else:
                            date_time_new=datetime.now() - timedelta(hours=intQuantity)

                        strDate=date_time_new 
                    else:
                        dateOfNew=None
                        monthOfNew_Number=None
                        dateOfNew=str(strDate.split(',')[0]).lower()
                        monthOfNew=dateOfNew.split(' ')[0]
                        monthOfNew_Number=lsMonth.index(monthOfNew)+1
                        if date.today().month==monthOfNew_Number:
                            dayOfNew=int(dateOfNew.split(' ')[1])
                            if date.today().day==dayOfNew:
                                strDate=datetime.now().strftime(formatTimeForPostgreSQL)
                            else:
                                #If not current date, continue with next new
                                continue    
                        else:
                            #If not current month, continue with next new
                            continue 
            except:
                #If whatever fails on the process, continue with next new
                #I decide to "continue" because it exists a high risk of reading past news
                continue


            fieldTimeStamp=strDate    
            linkNew=objNew.find_element_by_xpath('.//a')  
            hrefLink=linkNew.get_attribute('href')
            fieldUrl=hrefLink
            BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
            res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/div[4]/div[2]/div/div/main/div/div[3]/div[1]/div/section/article/div[1]/div','es')
            if not res:
                print(f'New already in database. App: {appName}')
            else:
                #START OF TF-IDF - keyword process

                df_tfidf_original=None
                df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
                fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
                del df_tfidf_original

                df_tfidf_translated=None
                df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
                fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
                del df_tfidf_translated

                #End of TF IDF - Keyword process
                #Start of PostgreSQL New Insertion
                insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
                #End of PostgreSQL New Insertion  
            
        linkNext=devuelveElemento('/html/body/div[4]/div[2]/div/div/div/main/div/div[2]/div[1]/div/div[2]/div/div[2]/section/div/div/div/section[2]/div/ul/li[9]/a') 
        BROWSER.execute_script('arguments[0].click();',linkNext)  

#R       
def readFromElFinanciero():
    returnChromeSettings()
    iam='El financiero'
    print(f'Starting reading {iam}...')
    BROWSER.get(dicWebSite['financiero'])
    strDivNews='list-container layout-section'
    global fieldTimeStamp,fieldBase64NewContent,fieldCommodity,fieldListOfKeyWordsOriginal
    global fieldListOfKeyWordsTranslated,fieldTitle,fieldUrl,fieldSourceSite,appName  
    #Start - PostgreSQL fields
    fieldBase64NewContent=None
    fieldCommodity=None
    fieldListOfKeyWordsOriginal=None
    fieldListOfKeyWordsTranslated=None
    fieldTitle=None
    fieldUrl=None
    fieldSourceSite=None
    fieldTimeStamp=None
    appName=None
    #End -  PostgreSQL Fields  
    appName=iam
    fieldSourceSite=appName
    lsNewSection=devuelveListaElementos('/html/body/div[1]/section/div/div[2]/aside/div')
    for div in lsNewSection:
        className=div.get_attribute('class')
        if className == strDivNews:
            lsArticle=div.find_elements_by_xpath('.//article') 
            for article in lsArticle:  
                lsContentOriginal=list()
                lsContentTranslated=list()
                hrefLink=None
                linkNew=article.find_element_by_xpath('.//a')  
                hrefLink=linkNew.get_attribute('href')
                #Get date
                txtDate=None
                txtDate=hrefLink
                txtDate=txtDate.split('www.elfinanciero.com.mx/mercados')[1]
                txtDate=txtDate.split('/')
                today=date.today().strftime('%Y/%m/%d')
                #Date position [1]:Year, [2]:Month, [3]:day
                new_date=F'{txtDate[1]}/{txtDate[2]}/{txtDate[3]}'
                if today != new_date:
                    continue

                fieldTimeStamp=datetime.now().strftime(formatTimeForPostgreSQL)
                fieldUrl=hrefLink
                BROWSER.execute_script('window.open("'+hrefLink+'")','_blank')
                res=secondWindowMechanism(lsContentOriginal,lsContentTranslated,'/html/body/div[1]/section/div/div[2]/div/article','en')
                if not res:
                    print(f'New already in database. App: {appName}')
                else:
                    #START OF TF-IDF - keyword process

                    df_tfidf_original=None
                    df_tfidf_original=getCompleteListOfKeyWords(lsContentOriginal) 
                    fieldListOfKeyWordsOriginal=getKeyWordsPairListFromDataFrame(df_tfidf_original[0:40])
                    del df_tfidf_original

                    df_tfidf_translated=None
                    df_tfidf_translated=getCompleteListOfKeyWords(lsContentTranslated) 
                    fieldListOfKeyWordsTranslated=getKeyWordsPairListFromDataFrame(df_tfidf_translated[0:40])
                    del df_tfidf_translated

                    #End of TF IDF - Keyword process
                    #Start of PostgreSQL New Insertion
                    insertNewInTable(fieldTitle,lsContentOriginal[0],lsContentTranslated[0],fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName)  
                    #End of PostgreSQL New Insertion  
                
              
                

#SECTION - START OF COMMON METHODS

def getKeyWordsPairListFromDataFrame(dataFrame):
    """
        In this dataframe, you can get the name and its weight by iterating each row:
        Feature/word = row[1].name
        Weight   = row[1].values[0]
    """
    lsReturn=list()
    for row in dataFrame.iterrows():
        strLine=None
        strLine=f'{str(row[1].name)},{str(row[1].values[0])}'
        lsReturn.append(strLine)

    return ';'.join(lsReturn)

def insertNewInTable(fieldTitle,originalContent,translatedContent,fieldBase64NewContent,fieldTimeStamp,fieldCommodity,fieldListOfKeyWordsOriginal,fieldListOfKeyWordsTranslated,fieldUrl,fieldSourceSite,appName):
    strFields=None
    strValues=None
    strFields='(txtTitle,txtNew_content_Original,txtNew_content_Translated,txtBase64_contentOriginal,tspDateTime,commodity,lsKeywordsOriginal,lsKeyWordsTranslated,txturl,txtsitesource,appName)'
    strValues=f"('{fieldTitle}','{originalContent}','{translatedContent}','{fieldBase64NewContent}','{fieldTimeStamp}','{fieldCommodity}','{fieldListOfKeyWordsOriginal}','{fieldListOfKeyWordsTranslated}','{fieldUrl}','{fieldSourceSite}','{appName}')"
    st=f"insert into tbNew {strFields} values {strValues} "
    res=False
    res=bd.executeNonQuery(st)
    if res:
        print(f'----------------New inserted succesfully on App: {appName}----------------')
    else:
        print(f'---------------New content was not inserted on App: {appName}...please check----------')      

def getCommodity(titleInLowerCase,dicToSearch):
    global fieldCommodity
    for key in dicToSearch:
        lsCurrent=None
        lsCurrent=dictCommodity[key]
        for commodityWord in lsCurrent:
            if commodityWord in titleInLowerCase:
                return key
                   
def getSourceAndTranslatedText(sourceText,tgtLang):
    #getSourceAndTranslatedText returns both (original and translated text) clean.
    global fieldBase64NewContent
    sbytes=None
    lsRes=None
    lsTranslated=list()
    lsSourceText=list()
   
    """
    isspace is True when '__' or more, '' this would be False
    """ 
    #Start of CLEANING PROCESS      
    #Remove text that may cause troubles: No content
    #Split the text with '\n' to translate item length less than 5,000 
    lsSourceText=sourceText.split('\n')
    #Analize every character in item, if it remains "space" , wipe it out
    for item in lsSourceText:
        newString=''
        for character in str(item):
            if character.isalnum() or character.isspace() or (not character):
                newString+=character
                continue
        idx=lsSourceText.index(item)  
        lsSourceText[idx]=newString     

    #END of CLEANING PROCESS
    sourceContent_clean=' '.join(lsSourceText)
    #Once the original content is clean, convert it to base64 and check in database. 
     #Convert the original content to base64 to check if we have it already
    #Tutorial : https://base64.guru/developers/python/examples/decode-pdf
    #Convert to base64 the original text (position 0)
    sbytes = base64.b64encode(bytes(sourceContent_clean,'utf-8'))
    fieldBase64NewContent=sbytes.decode('utf-8') 
    query=f"select id from tbNew where txtBase64_contentoriginal='{fieldBase64NewContent}'"
    lsRes=bd.getQuery(query) 
    if not lsRes:
        #Case: The record does not exist, hence translate it and keep going
        for item in lsSourceText:
            try:
                lsTranslated.append(GoogleTranslator(target=tgtLang).translate(item))
            except:
                print(f'Item : {item} couldn not be translated...continue')
                continue   

        #Cleaning lsTranslated
        for item in lsTranslated:
            if item is None:
                lsTranslated.remove(item)
        global lsChar

        new_translated=None
        new_translated=' '.join(lsTranslated)
        for char in lsChar:
            new_translated=new_translated.replace(char,' ')
            
    return [sourceContent_clean,new_translated]

def returnChromeSettings():
    global BROWSER
    chromedriver_autoinstaller.install()
    options = Options()
    if objControl.heroku:
        #START-REQUIRED FOR HEROKU
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
        BROWSER=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=options)
        #END-REQUIRED FOR HEROKU
    else:
        BROWSER=webdriver.Chrome(options=options)  

def secondWindowMechanism(lsContent,lsContentTranslated,xPathElementSecondWindow,tgtLang):
    if len(BROWSER.window_handles)>1:
        global fieldCommodity,fieldTitle
        res=None
        bAd=False
        second_window=BROWSER.window_handles[1]
        BROWSER.switch_to.window(second_window)
        #Now in the second window
        time.sleep(5)
        #Get the text from second window and append it to lsContent
        strContent=None
        strTitle=None
        try:
            strContent=BROWSER.find_element_by_xpath(xPathElementSecondWindow)
            strTitle=getTitleClean(BROWSER.title)
            fieldTitle=strTitle
        except NameError as error:
            bAd=True   
        if strContent and (not bAd):
            sourceText=None
            sourceText=strContent.text
            fieldCommodity=getCommodity(str(strTitle).lower(),dictCommodity)
            lsResult=list()
            lsResult=getSourceAndTranslatedText(sourceText,tgtLang)
            if lsResult:
                lsContent.append(lsResult[0])
                lsContentTranslated.append(lsResult[1])
                res=True
            else:
                res=False    
            
           
            #Close Window 2
            BROWSER.close()
            time.sleep(4)
            #Now in First window
            first_window=BROWSER.window_handles[0]
            BROWSER.switch_to.window(first_window)

            return res

def getTitleClean(strTitle):
    global lsChar
    for char in lsChar:
        strTitle=strTitle.replace(char,' ')
    return strTitle

def getCompleteListOfKeyWords(lsContent):
    #This implementation of code is based on : 
    # https://towardsdatascience.com/tf-idf-explained-and-python-sklearn-implementation-b020c5e83275

    #Details: lsContent has 2 documents as default: [0] Original new and [1] translated new
    contentSize=len(lsContent)
    if contentSize>1:
        lsContentToRead=None
    else:
        lsContentToRead=lsContent
    
    #Creating TF-IDF and its dataframe
    lsRes=[]
    lsRes=getDataFrameFromTF_IDF(lsContentToRead,contentSize)
    df=lsRes[0]
    #lsFeatures may be used later, I just comment it meanwhile...
    #lsFeatures=lsRes[1] 
    
    return df
                         
def pre_process_data(content):
    content = content.replace('.',' ')
    content = re.sub(r'\s+',' ',re.sub(r'[^\w \s]','',content)).lower()

    return content

def devuelveElementoDinamico(xPath,option,limit):
    try:
        if option==limit:
            print(f'Element was not found from {str(option)} to {str(limit)}')
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
                   
def createWordCloud(imageName,df_Sliced):
    dictWord_TF_IDF={}
    for row in df_Sliced.iterrows():
        dictWord_TF_IDF[str(row[1].name)]=float(str(row[1].values[0]))
    wordcloud = WordCloud().generate_from_frequencies(dictWord_TF_IDF)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f'{imageName}')
    del wordcloud
    del dictWord_TF_IDF
    
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
    
    In this dataframe, you can get the name and its weight by iterating each row:
    Feature/word = row[1].name
        Weight   = row[1].values[0]
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


#SECTION - END OF COMMON METHODS

    