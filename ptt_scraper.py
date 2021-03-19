# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import urllib
import re
import os
import pandas as pd
from datetime import datetime
import csv
from pytube import YouTube

PTT_URL = 'https://www.ptt.cc'
base64_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
script_path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(script_path, 'configFile', 'config.txt'), encoding='utf-8') as f:
    config = f.readlines()
    config = {i.split("=")[0]: i.split("=")[1].replace("\n", "") for i in config if '#' not in i and i != '\n'}

try:
    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
except:
    start_date = None

# Default is set to today
try:
    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
except:
    end_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

board_name = config['board_name']

try:
    keyword = config['keyword']
except:
    keyword = None

try:
    author_ID = config['author_ID']
except:
    author_ID = None

API_KEY = config['API_KEY']

today_datetime = datetime.today().strftime('%Y%m%d-%H%M%S')
output_path = os.path.join(script_path, 'outputs_'+board_name+'_'+today_datetime)
if not os.path.exists(output_path):
    os.makedirs(output_path)
image_path = os.path.join(output_path, 'images')
if not os.path.exists(image_path):
    os.makedirs(image_path)
content_path = os.path.join(output_path, 'contents')
if not os.path.exists(content_path):
    os.makedirs(content_path)


# Get source code of the web page
def get_web_page(url):
    resp = requests.get(
        url=url,
        cookies={'over18': '1'}
    )
    if resp.status_code != 200:
        print('Invalid URL:', resp.url)
        return None
    else:
        return resp.text


# Convert to base64
def base64(n, carry):
    # Decimal to binary
    if carry == 'decimal':
        s = bin(n)[2:][::-1]
    # Hexadecimal to binary
    elif carry == 'hexadecimal':
        s = bin(int(n, 16))[2:][::-1]
    # Binary to base64
    return ''.join([base64_table[int(s[i:i+6][::-1], 2)] for i in range(0, len(s), 6)][::-1])


# Get article URLs and basic info from index page
def get_articles(dom, start_date):
    soup = BeautifulSoup(dom, 'html5lib')

    try:
        paging_div = soup.find('div', 'btn-group btn-group-paging')
        prev_url = paging_div.find_all('a')[1]['href']
    except:
        prev_url = None

    articles = []
    divs = soup.find_all('div', 'r-ent')

    for d in divs:
        if d.find('a'):  # Deleted article will not be collected
            href = d.find('a')['href']
            code1 = href.split('.')[-4]
            code2 = href.split('.')[-2]
            article_code = base64(int(code1), 'decimal') + base64(code2, 'hexadecimal')
            # code1 represents posting timestamp
            dt = datetime.fromtimestamp(int(code1))
            # Ignore the article if it is posted before start_date
            if start_date and dt < start_date:
                continue
            else:
                author = d.find('div', 'author').text if d.find('div', 'author') else ''
                # Ignore the article if author is not the specified one
                if author_ID and author != author_ID:
                    continue
                else:
                    title = d.find('a').text
                    articles.append({
                        'title': title,
                        'href': href,
                        'author': author,
                        'dt': dt.strftime('%Y/%m/%d %H:%M:%S'),
                        'code1': code1,
                        'code2': code2,
                        'article_code': article_code
                    })
    return articles, prev_url


# Get image URL from imgur album link
def get_album(dom):
    soup = BeautifulSoup(dom, 'html5lib')

    src = ''
    divs = soup.find_all('div', {'class': 'image post-image'})
    for d in divs:
        if d.find('img'):
            src = 'https:' + d.find('img')['src']
    return src


# Get all image URLs in the article
def parse(soup):
    links = soup.find(id='main-content').find_all('a')
    img_urls = []
    img_urls_2 = []
    img_urls_3 = []
    img_urls_4 = []
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com', link['href']):
            img_urls.append(link['href'])
        elif re.match(r'^https?://s1.imgs.cc', link['href']):
            img_urls_2.append(link['href'])
        elif re.match(r'^https?://i.ytimg.com', link['href']):
            img_urls_3.append(link['href'])
        elif re.match(r'^https?://(www.)?youtu(be)?(.be)?(.com)?', link['href']):
            img_urls_4.append(link['href'])
    return img_urls, img_urls_2, img_urls_3, img_urls_4


# Download image and video
def save(img_urls, img_urls_2, img_urls_3, img_urls_4, title):
    count = 1
    if img_urls:
        try:
            dname = title.strip()
            filepath = os.path.join(image_path, dname)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            # Modify image URLs to download images
            for img_url in img_urls:
                if img_url.split('/')[-2] == 'a':
                    page = get_web_page(img_url)
                    img_url = get_album(page)
                    if not img_url:
                        continue
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg') and not img_url.endswith('.png') and not img_url.endswith('.gif'):
                    img_url += '.jpg'
                #fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(filepath, dname+'_'+str(count)+'.jpg'))
                count += 1
        except Exception as e:
            print(e)

    if img_urls_2:
        try:
            dname = title.strip()
            filepath = os.path.join(image_path, dname)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            for img_url in img_urls_2:
                if not img_url.endswith('.jpg') and not img_url.endswith('.png') and not img_url.endswith('.gif'):
                    img_url += '.jpg'
                #fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(filepath, dname+'_'+str(count)+'.jpg'))
                count += 1
        except Exception as e:
            print(e)

    if img_urls_3:
        try:
            dname = title.strip()
            filepath = os.path.join(image_path, dname)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            for img_url in img_urls_3:
                if not img_url.endswith('.jpg') and not img_url.endswith('.png') and not img_url.endswith('.gif'):
                    img_url += '.jpg'
                #fname = img_url.split('/')[-2] + '-' + img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(filepath, dname+'_'+str(count)+'.jpg'))
                count += 1
        except Exception as e:
            print(e)

    if img_urls_4:
        try:
            dname = title.strip()
            filepath = os.path.join(image_path, dname)
            if not os.path.exists(filepath):
                os.makedirs(filepath)

            for img_url in img_urls_4:
                if img_url.split('//')[1].startswith('youtu.be'):
                    img_url = 'https://www.youtube.com/watch?v=' + img_url.split('/')[-1]
                YouTube(img_url).streams.first().download(filepath)
        except Exception as e:
            print(e)


# Get IP country
# Source: https://ipstack.com/
def get_country_ipstack(ip):
    if ip:
        url = 'http://api.ipstack.com/{}?access_key={}'.format(ip, API_KEY)
        data = requests.get(url).json()
        country_name = data['country_name'] if data['country_name'] else None
        return data, country_name
    return None


def main():
    start_time = datetime.now()
    # Get HTML of index page
    if keyword:
        # Search for keyword first if specified
        current_page = get_web_page(PTT_URL + '/bbs/' + board_name + '/search?q=' + keyword)
    else:
        current_page = get_web_page(PTT_URL + '/bbs/' + board_name + '/index.html')

    if current_page:
        print('Start crawling articles...')
        current_articles, prev_url = get_articles(current_page, start_date)

        header = ['Title', 'Author', 'DateTime', 'IP', 'Country', 'URL', 'TimeStamp',
                  'RandomCode', 'ArticleCode', 'UpvoteCount', 'NeutralCount', 'DownvoteCount']
        article_df = pd.DataFrame(columns=header)
        invalid_header = ['Title', 'Author', 'DateTime', 'URL']
        invalid_df = pd.DataFrame(columns=invalid_header)

        article_count = 0
        invalid_count = 0
        while current_articles or prev_url:
            for article in current_articles:
                # Ignore the article if it is posted after end_date
                if end_date and datetime.strptime(article['dt'], '%Y/%m/%d %H:%M:%S') > end_date:
                    continue

                page = get_web_page(PTT_URL + article['href'])
                if page:
                    soup = BeautifulSoup(page, 'html.parser')

                    print('Crawling:', article['title'])

                    # Get IP
                    pattern = '來自: \d+\.\d+\.\d+\.\d+'
                    match = re.search(pattern, page)
                    if match:
                        ip = match.group(0).replace('來自: ', '')
                    else:
                        ip = None

                    # Get IP country
                    _, country = get_country_ipstack(ip)

                    # Get upvote, downvote and neutral count
                    neutral_count = 0
                    downvote_count = 0
                    upvote_count = len(soup.find_all('span', {'class': 'hl push-tag'}))
                    for message in soup.find_all('span', {'class': 'f1 hl push-tag'}):
                        if message.text.strip() == '→':
                            neutral_count += 1
                        elif message.text.strip() == '噓':
                            downvote_count += 1

                    # Save article info to DataFrame
                    article_df.loc[article_count] = [article['title'], article['author'], article['dt'], ip, country, PTT_URL+article['href'],
                                                     article['code1'], '"'+article['code2']+'"', article['article_code'], upvote_count, neutral_count, downvote_count]
                    article_count += 1

                    # Save contents and messages to text file
                    all_text = soup.find(id='main-content').text
                    content = '\n'.join(list(filter(None, all_text.split('\n')[1:])))
                    with open(os.path.join(content_path, article['code1']+'_'+article['code2']+'.txt'), 'w', encoding='utf-8') as text:
                        text.write(content)

                    # Get image URLs and save
                    img_urls, img_urls_2, img_urls_3, img_urls_4 = parse(soup)
                    save(img_urls, img_urls_2, img_urls_3, img_urls_4, str(article['code1'])+'_'+str(article['code2']))
                else:
                    # Save article info of invalid URLs
                    invalid_df.loc[invalid_count] = [article['title'], article['author'], article['dt'], PTT_URL+article['href']]
                    invalid_count += 1
            # Navigate to previous page and continue crawling
            if prev_url:
                current_page = get_web_page(PTT_URL + prev_url)
                current_articles, prev_url = get_articles(current_page, start_date)
            else:
                break
    # Cannot retrieve index page
    else:
        # Terminate the whole process
        return

    # Write article info to CSV sorted by timestamp
    article_df.drop_duplicates(inplace=True)
    article_df.sort_values(by=['DateTime'], ascending=False, inplace=True)
    article_df.to_csv(os.path.join(output_path, 'Article List.csv'), encoding='utf_8_sig', index=False)

    # Write invalid article info to CSV sorted by timestamp if any
    if not invalid_df.empty:
        invalid_df.drop_duplicates(inplace=True)
        invalid_df.sort_values(by=['DateTime'], ascending=False, inplace=True)
        invalid_df.to_csv(os.path.join(output_path, 'Invalid Article List.csv'), encoding='utf_8_sig', index=False)

    print('===================================')
    print('Crawling finished.')
    print('Number of articles retrieved: %d' % (len(article_df.index)))
    print('Number of invalid articles: %d' % (len(invalid_df.index)))
    end_time = datetime.now()
    time_diff = end_time - start_time
    print('Execution time:', str(time_diff))


if __name__ == '__main__':
    main()
