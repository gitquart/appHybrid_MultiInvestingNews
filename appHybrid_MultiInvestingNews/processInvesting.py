#This file reads news from : https://www.investing.com/analysis/commodities


def processInvesting():
    tool.returnChromeSettings()
    url="https://www.investing.com/news/commodities-news"
    tool.readUrl(url)
    





if __name__ == "__main__":
    processInvesting()