# nuzforums-scraper
Scraper for Nuzlocke Forums implemented in Python 3 using Scrapy\
This project is inspired from https://github.com/Dascienz/phpBB-forum-scraper.

## Prerequisites
* [Python 3](https://www.python.org/downloads/)
* [Scrapy](https://scrapy.org/)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
* [SQLite](https://www.sqlite.org/index.html) (for viewing)

Verify you have the correct version of Python installed by typing `python --version`.

Once you have Python installed, the other libraries can be easily installed via `pip`:

```
pip install scrapy
pip install beautifulsoup4
```

The `sqlite3` module should be included with Python 3, so a `pip` install should not be necessary to run the program. However, to view the `.db` file via the command line, you would need to install the standalone executable from the link above (under Downloads).

## Instructions
1. Modify settings (username, password, URLs) in `nuzforums_scraper/user_settings.py`.
2. Run the following command in the root directory:
```
scrapy crawl nuzforums
```
The program will output:
* a SQLite database file (`nuzforums.db`) containing all Forums, Topics, and Posts
* text version of all items in `logs/items.txt`
* errors in `logs/errors.txt`

You can view data using SQLite in the command line (e.g. `sqlite3 nuzforums-posts.db`).\
There are 3 tables: `Forum`, `Topic`, and `Post`. Simply run a select query on any of them (e.g. `SELECT * FROM Forum;`).

NOTE: Running the program will overwrite previous output and log files, so if you're running this multiple times and don't want to lose data, make sure to backup the previous output files (`.db` and/or `.txt` files). 