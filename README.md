# Stackoverflow Crawler

To fetch information on stackoverflow for a specified tag.
This module calls StackExchange API https://api.stackexchange.com/docs instead of webpages.


## Usage
```
import logging
import stackoverflow_crawler

logging.basicConfig(level=logging.INFO)
logging.getLogger('notebook').setLevel(logging.INFO)


tag = "python"
db_url = f"sqlite:///crawl_results_{tag}.db"
crawler = stackoverflow_crawler.StackoverflowCrawler(db_url, tag)
crawler.crawl()
```

