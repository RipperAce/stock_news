import nsetools
from pprint import pprint
from dotenv import load_dotenv
import os
import requests
from twilio.rest import Client

load_dotenv("./.env")

API_KEY = os.environ.get("NEWS_API_KEY")
ACCOUNT_SID = "AC6f06d4b0637f1dc296d7bd49c759ae6e"
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_KEY")
FROM=os.environ.get("FROM")
TO=os.environ.get("TO")

DRREDDY_STOCK = "DRREDDY"
RELIANCE_STOCK = "RELIANCE"
GODREJCP_STOCK = "GODREJCP"

WATCHLIST = [DRREDDY_STOCK, RELIANCE_STOCK, GODREJCP_STOCK]

def getStockdata(share_name):
    nse = nsetools.Nse()
    stock = nse.get_quote(share_name)
    
    previous_data = stock["open"] - stock["previousClose"]
    today_data = stock["closePrice"] - stock["open"]
    total_diff = stock["closePrice"] - stock["previousClose"]
    company_name = stock["companyName"]
    perc_drop = stock["closePrice"] * 5 / 100

    return (previous_data, today_data, total_diff, company_name, perc_drop)


def sendMessage(send_msg):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    message = client.messages \
                    .create(
                        body=send_msg,
                        from_=FROM,
                        to=TO
                    )
    print(message.status)


def getNews(share_name, previous_data, today_data, total_diff, company_name, perc_drop):
    if ((previous_data < 0 and today_data < 0) or 
        (previous_data > 0 and today_data > 0) and 
        (abs(total_diff) - 5 <= perc_drop <= abs(total_diff) + 5)):

        parameters = {"q":company_name, "sortBy": "relevancy", "apiKey": API_KEY}
        articles = requests.get(url="https://newsapi.org/v2/everything", params=parameters)
        data = articles.json()["articles"]

        news_title = []
        news_url = []
        published_date = []
        for news in data:
            news_title.append(news["title"])
            news_url.append(news["url"])
            published_date.append(news["publishedAt"])
        
        send_msg = ""
        if total_diff > 0:
            send_msg += f"{share_name}:  {round(abs(total_diff), 2)} ⬆\n\n"
        else:
            send_msg += f"{share_name}:  {round(abs(total_diff), 2)} ⬇\n\n"

        for i in range(3):
            send_msg += "Title: "+news_title[i]+"\n"+"URL: "+news_url[i]+"\n"+"Dated: "+published_date[i][0:10]+"\n\n"

        sendMessage(send_msg = send_msg)


for share in WATCHLIST:
    previous_data, today_data, total_diff, company_name, perc_drop = getStockdata(share)
    getNews(share_name = share, previous_data=previous_data, today_data=today_data, total_diff=total_diff, company_name=company_name, perc_drop=perc_drop)