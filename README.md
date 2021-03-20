# PTT Web Scraper

Crawl article information from PTT - one of the largest internet forums in Taiwan

## Features
* Crawl article information from specified board
* Customized filters such as board name, time period, keyword and author ID
* Output formats: .csv, .txt, .jpg

## Directory Structure
    .
    ├── configFile                                  # Contains all the configuration files required in the scripts
    │   ├── config.txt                              # Configuration parameters required in the scripts
    │   └── requirements.txt                        # Required Python packages
    ├── outputs_<BOARD_NAME>_YYYYmmdd-HHMMSS        # Output folder (automatically generated, attached with execution timestamp)
    │   ├── contents                                # Article content text files (use unique article ID as file name)
    │   ├── images                                  # Image and video files (sorted by articles, use unique article ID as folder name)
    │   └── Article List.csv                        # List of article information
    └── ptt_scraper.py                              # Main Python script

## Configuration Parameters
<table>
    <tr>
        <td><strong>Parameter Name</strong></td>
        <td><strong>Description</strong></td>
        <td><strong>Required</strong></td>
        <td><strong>Example</strong></td>
    </tr>
    <tr>
        <td>board_name</td>
        <td>The name of the board for data extraction.</td>
        <td>Yes</td>
        <td>Stock</td>
    </tr>
    <tr>
        <td>API_KEY</td>
        <td>The API key for identifying IP location.</td>
        <td>Yes</td>
        <td>Apply from <a href="https://ipstack.com/">ipstack</a></td>
    </tr>
    <tr>
        <td>start_date</td>
        <td>Define start date to extract the data. Specified start_date is included.</td>
        <td>No</td>
        <td>2021-01-01</td>
    </tr>
    <tr>
        <td>end_date</td>
        <td>Define end date to extract the data. Specified end_date is <strong><i>NOT</i></strong> included.</td>
        <td>No</td>
        <td>2021-01-01</td>
    </tr>
    <tr>
        <td>keyword</td>
        <td>Keyword used for searching title.</td>
        <td>No</td>
        <td>ARKK</td>
    </tr>
    <tr>
        <td>author_ID</td>
        <td>Search for articles published by specified author.</td>
        <td>No</td>
        <td>test1234</td>
    </tr>
</table>

## Outputs
### Article List Content
* ___Title___
* ___Author___
* ___DateTime___: Posting time of the article
* ___IP___
* ___Country___
* ___URL___
* ___TimeStamp___: Timestamp of posting time
* ___RandomCode___: Hexadecimal number for each article
* ___ArticleCode___: Unique code for each article, generated from [TimeStamp and RandomCode](https://www.ptt.cc/bbs/PttEarnMoney/M.1566319802.A.35E.html)
* ___UpvoteCount___: Number of upvotes
* ___NeutralCount___: Number of neutral comments
* ___DownvoteCount___: Number of downvotes

## Logic Flow
1.	Execute ```ptt_scraper.py```
2.	Read configuration from ```config.txt```
3.	Capture data from specified board with specified filters
4.	Save data as CSV, text, image and video files

## How to Execute
### Install packages
```
pip install -r requirements.txt
```

### Run the script
```
python ptt_scraper.py
```
***
Copyright © 2021 [Andy Lin](https://github.com/andy2167565). All rights reserved.
