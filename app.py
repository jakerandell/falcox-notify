import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import markdown
import hashlib
import sqlite3
import twilio.rest
import os


db = sqlite3.connect('database.sqlite')
cursor = db.cursor()

cursor.execute('create table if not exists version_headers (value text, date_added datetime)')
cursor.execute('create table if not exists links (href text, date_added datetime)')

twilio_client = twilio.rest.Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
twilio_message = ''

url = 'https://flightone.com/alpha'

page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
url_parts = urlparse(url)

latest_bin_link = soup.select('.container .toptop .top_content h5 a', href=True)[0]['href']
cached_links = cursor.execute('select * from links').fetchall()

if latest_bin_link not in dict(cached_links):
    cursor.execute("insert into links (href, date_added) values (?, datetime('now'))", (latest_bin_link,))
    twilio_message = twilio_message + 'New bin %s \n' % latest_bin_link

changelog_text = soup.find('div', id='changelog').text
changelog_html = markdown.markdown(changelog_text)
changelog_hash = hashlib.md5(bytes(changelog_text, encoding='utf-8')).hexdigest()
changelog_soup = BeautifulSoup(changelog_html, 'html.parser')

cached_versions = cursor.execute('select * from version_headers').fetchall()

for header in changelog_soup.find_all('h3'):
    if header.text not in dict(cached_versions):
        cursor.execute("insert into version_headers (value, date_added) values (?, datetime('now'))", (header.text,))
        twilio_message = twilio_message + 'New version %s \n' % header.text

db.commit()
db.close()

if twilio_message:
    print('has message')
    twilio_message = ('\n' + twilio_message[:1500] + '...') if len(twilio_message) > 1600 else '\n' + twilio_message
    message = twilio_client.messages.create(body=twilio_message, from_=os.environ['TWILIO_FROM'], to=os.environ['TWILIO_TO'])
