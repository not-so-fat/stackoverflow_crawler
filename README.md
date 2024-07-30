# Stackoverflow Crawler

To fetch information on stackoverflow for a specified tag.
-> for my purpose it would be better to use https://api.stackexchange.com/docs instead of crawling...


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

