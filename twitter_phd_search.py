#!/usr/bin/env python3

from datetime import datetime, timezone, timedelta
from twarc.client2 import Twarc2
from twarc.expansions import ensure_flattened
import smtplib, ssl
import API_info
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def main():
    pages = get_tweets()
    tweets_info = get_tweets_info(pages)
    html_mail = format_email(tweets_info)
    send_email(html_mail)
    
def get_tweets():
    print("Getting tweets")
    t = Twarc2(bearer_token="AAAAAAAAAAAAAAAAAAAAAOtUawEAAAAAeQ%2FQIKly77Vi%2B2mTpoiI0L9avOk%3DMTfdQUDdJb4Zu0a6RvwqKyKEtwKeB3CpcXg65Kt75ZGKD8qBUc")
    # Start and end times must be in UTC
    #start_time = datetime.now(timezone.utc) + timedelta(hours=-2)
    # end_time cannot be immediately now, has to be at least 30 seconds ago.
    #end_time = datetime.now(timezone.utc) + timedelta(minutes=-1)

    # search_results is a generator, max_results is max tweets per page, 100 max for full archive search with all expansions.
    pages = []
    query_p1 = "(position OR positions OR opportunity OR opportunities OR fellowship OR fellowships OR fellow)"
    query_p2 = "(bioinformatics OR genomics OR transcriptomics OR DNA OR RNA)"
    query = f"phd {query_p1} {query_p2} -is:retweet"
    search_results = t.search_recent(query=query, start_time=None, end_time=None,)
    for page in search_results:
        pages.append(page)
    
    return pages

def get_tweets_info(pages):
    print("Sortting tweets")
    tweets_info = []
    for page in pages:
        for tweet in ensure_flattened(page):
            created_at_brt = datetime.strptime(tweet["created_at"], "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%d/%m/%Y, %H:%M:%S")
            infos = {"name": tweet["author"]["name"],
                "username": tweet["author"]["username"],
                "text": tweet["text"],
                "site": f"https://twitter.com/{tweet['author']['username']}/status/{tweet['id']}",
                "created_at": created_at_brt}
            tweets_info.append(infos)
    
    return tweets_info

def format_email(tweets_info):
    print("Formatig email")
    html_tweets = f"""
            <h4>{len(tweets_info)} tweets found this week</h4>"""

    for tweet in tweets_info:
        formater = f"""
            <div style="border: 2px solid #008080">
            <p><strong>{tweet["name"]} <a href="https://twitter.com/{tweet["username"]}">@{tweet["username"]}</a></strong></p>
                <p style="padding-left: 40px;">{tweet["text"]}<br />
                {tweet["created_at"]} <a href="{tweet["site"]}">Twitter Link</a></p>
            </div>"""
        html_tweets += formater

    html_mail = f"""\
    <html>
        <body>
            {html_tweets}
        </body>
    </html>
    """
    
    return html_mail

def send_email(html_mail):
    print("Sending email")
    sender_email = "gabrielamorimsilva@gmail.com"
    receiver_email = "gabrielamorimsilva@gmail.com"
    password = API_info.GMAIL_PASSWORD

    message = MIMEMultipart("alternative")
    message["Subject"] = "Twitter Bot PhD Searcher"
    message["From"] = sender_email
    message["To"] = receiver_email

    html_part = MIMEText(html_mail, "html")

    message.attach(html_part)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

if __name__ == '__main__':
    main()
