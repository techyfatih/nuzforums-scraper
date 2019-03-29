# nuzforums-scraper
Scraper for Nuzlocke Forums implemented in Python 3 using Scrapy\
This project is inspired from https://github.com/Dascienz/phpBB-forum-scraper.

## Prerequisites
* [Python 3](https://www.python.org/downloads/)
* [Scrapy](https://scrapy.org/)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
* [SQLite](https://www.sqlite.org/index.html)

## Instructions
1. Set the username and password in `nuzforums_scraper/spiders/nuzforums.py`
2. Run the following command in the root directory:
```
scrapy crawl nuzforums
```
The program will generate a SQLite database file (`nuzforums.db`) containing all of the posts under a table called 'Posts'. You can then view the data using SQLite in the command line (e.g. `sqlite3 nuzforums-posts.db`, then `SELECT * FROM Posts;`).
