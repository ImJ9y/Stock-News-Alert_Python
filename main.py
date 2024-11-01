import requests
import datetime
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient
import os

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

stock_API_KEY = "CDXX5FNLL07P94NM"
stock_price_parameter = {
    "function":"TIME_SERIES_DAILY",
    "symbol":STOCK,
    "apikey": stock_API_KEY
}
stock_response = requests.get("https://www.alphavantage.co/query?",params=stock_price_parameter)
stock_response.raise_for_status()
stock_data = stock_response.json()

#data_list = [value for (key, value) in stock_data.items()]

yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
day_before_yesterday = str(datetime.date.today() - datetime.timedelta(days=2))

day_before_close_stock = float(stock_data["Time Series (Daily)"][day_before_yesterday]['4. close'])
yesterday_close_stock = float(stock_data["Time Series (Daily)"][yesterday]['4. close'])

percentage = ((day_before_close_stock - yesterday_close_stock)/yesterday_close_stock) * 100

if percentage >= 5:
    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    news_parameters = {
        "from":yesterday,
        "sortBy":"publishedAt",
        "apiKey":"9997d561e6a84786a15003982811fb04",
        "qInTitle": COMPANY_NAME
    }

    news_response = requests.get("https://newsapi.org/v2/everything?",params=news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()['articles']

    three_articles = news_data[:3]

    formatted_articles = [f"Headline: {article['title']}. \n Brief: {article['description']}" for article in three_articles]

    ## STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number.
    twilio_account_sid = os.environ.get("OWM_ACCT_SID")
    twilio_auth_token = os.environ.get("OWM_AUTH")

    proxy_client = TwilioHttpClient()
    proxy = None
    if 'https_proxy' in os.environ:
           proxy = os.environ['https_proxy']

    proxy_client.session.proxies = {'https':proxy}

    for article in formatted_articles:
        client = Client(twilio_account_sid, twilio_auth_token, http_client=proxy_client)
        message = client.messages.create(
            body=f"{STOCK}: {"🔺" if percentage > 0 else "🔻"} {int(percentage if percentage > 0 else percentage * -1)}%"
                 f"{article}",
            from_="+18888671995",
            to= "+16786752287")

        print(message.status)
        print(message.sid)