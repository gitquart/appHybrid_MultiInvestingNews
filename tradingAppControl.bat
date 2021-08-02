@ECHO OFF
if %1%==1 (ECHO Starting to Turn On Services...) else (ECHO Shutting down all Services...)

ECHO ---------------------------------------------------------------------

ECHO app-quart-cryptonews
call heroku ps:scale worker=%1 -a app-quart-cryptonews
ECHO app-quart-dailyfx
call heroku ps:scale worker=%1 -a app-quart-dailyfx
ECHO app-quart-financiero
call heroku ps:scale worker=%1 -a app-quart-financiero
ECHO app-quart-fxnews
call heroku ps:scale worker=%1 -a app-quart-fxnews
ECHO app-quart-investing
call heroku ps:scale worker=%1 -a app-quart-investing
ECHO app-quart-investopedia-market
call heroku ps:scale worker=%1 -a app-quart-investopedia-market
ECHO app-quart-investopedia-trading
call heroku ps:scale worker=%1 -a app-quart-investopedia-trading
ECHO app-quart-yahoo-market
call heroku ps:scale worker=%1 -a app-quart-yahoo-market
ECHO app-quart-yahoo-new 
call heroku ps:scale worker=%1 -a app-quart-yahoo-new  

ECHO ---------------------------------------------------------------------

if %1%==1 (ECHO All services ON...) else (ECHO All services OFF...)


PAUSE