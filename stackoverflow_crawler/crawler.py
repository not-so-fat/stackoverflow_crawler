import logging
import time
import math

import requests
import bs4

from . import (
    parser,
    dbmodel
)


logger = logging.getLogger(__name__)


class StackoverflowCrawler:
    def __init__(self, db_url, tag, timeout_seconds=10):
        self.db_session = dbmodel.init_db(db_url)()
        self.tag = tag
        self.timeout_seconds = timeout_seconds
        self.base_url = f"https://stackoverflow.com/questions/tagged/{tag}"

    def crawl(self, max_pages=100):
        RESULTS_PER_PAGE=15
        top_result = self.get_soup(self.base_url)
        total_q = int(top_result.find("div", class_="fs-body3").get_text(strip=True).split("\n")[0])
        stop = False
        for i in range(int(math.ceil(max(total_q, max_pages) / RESULTS_PER_PAGE))):
            if stop:
                logger.info("hit existing record. stopping.")
                break
            page_id = i+1
            # with tab=active it will fetch questions updated recently, and output updated time
            page_url = f"{self.base_url}?tab=active&page={page_id}&pagesize={RESULTS_PER_PAGE}"
            stop = self.collect_questions(page_url)

    def collect_questions(self, page_url):
        stop = False
        page = self.get_soup(page_url)
        questions = parser.get_questions_from_search(page)
        for q in questions:
            db_record = self.db_session.query(dbmodel.Question).\
                    filter_by(question_id=q['question_id']).first()
            if db_record and db_record["updated"] >= q["updated"]:
                stop = True
                break
            else:
                qpage = self.get_soup(f'https://stackoverflow.com{q["url"]}')
                q, answers = parser.parse_details(qpage, q)
                self.db_session.merge(dbmodel.Question(**q))
                for a in answers:
                    self.db_session.merge(dbmodel.Answer(**a))
                self.db_session.commit()
        return stop
        
    def get_soup(self, url):
        logger.info(url)
        source_code = requests.get(url).text
        time.sleep(self.timeout_seconds)
        return bs4.BeautifulSoup(source_code, "html.parser")
