# PTT Web Scraper

Crawl article information from PTT - one of the largest internet forums in Taiwan

## Features
* Crawl article information from specified board
* Customized filters such as board name, time period, keyword and author ID
* Output formats: .csv, .txt, .jpg

## Outputs
### Structure
    .
    ├── ...
    ├── outputs_<BOARD_NAME>_YYYYmmdd-HHMMSS        # Output folder (automatically generated, attached with execution timestamp)
    │   ├── contents                                # Article content text files (use unique article ID as file name)
    │   ├── images                                  # Image and video files (sorted by articles, use unique article ID as folder name)
    │   └── Article List.csv                        # List of article information
    └── ...

### Article List Content
![CSV Header](https://github.com/andy2167565/PTT-Scraper/blob/493c30004d0a75fad1b14a172dfd3f7cd780a016/configFile/Article%20List%20Header.PNG)

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
