import logging
import time
import math
from datetime import datetime

import requests
import bs4

from . import (
    dbmodel,
    api_handler
)


logger = logging.getLogger(__name__)
PAGESIZE = 50


class StackoverflowCrawler:
    def __init__(self, db_url, tag, interval_seconds=1):
        self.db_session = dbmodel.init_db(db_url)()
        self.se_api = api_handler.StackExchangeAPIHandler()
        self.tag = tag
        self.interval_seconds = interval_seconds

    def crawl(self, max_pages=50):
        has_more = True
        stop = False
        page_id = 1
        num_q = 0
        num_a = 0
        while has_more:
            if stop or page_id > max_pages:
                break
            logger.info(f"Fetching questions on page {page_id} / {max_pages}")
            search_params =dict(
                page=page_id,
                pagesize=PAGESIZE,
                order="desc",
                sort="activity",
                tagged=self.tag,
                site="stackoverflow",
                filter="withbody"# to include question body
            )
            try:
                res = self.se_api.search(search_params).json()
            except e:
                continue
            has_more = res["has_more"]
            questions, stop = self.collect_new_questions(res)
            if questions:
                self.insert_questions(questions)
                answers = self.query_answers(questions)
                self.insert_answers(answers)
                num_q += len(questions)
                num_a += len(answers)
            page_id += 1
        logger.info(f"Finished:\n{num_q} questions\n{num_a} answers")

    def collect_new_questions(self, res):
        stop = False
        questions = []
        for resq in res["items"]:
            q = _construct_question(resq)
            db_record = self.db_session.query(dbmodel.Question).\
                    filter_by(question_id=q.question_id).first()
            if db_record and db_record.updated >= q.updated:
                logger.warn(f"Found question_id={q.question_id} already exists in your DB")
                stop = True
                break
            questions.append(q)
        return questions, stop

    def query_answers(self, questions):
        """
        query all answers (it could be multiple pages)
        """
        qids = ";".join([str(q.question_id) for q in questions])
        page_id = 1
        has_more = True
        answers = []
        while has_more:
            params = dict(
                page=page_id,
                pagesize=PAGESIZE,
                order="desc",
                sort="activity",
                site="stackoverflow",
                filter="withbody"
            )
            res = self.se_api.answers(qids, params).json()
            has_more = res["has_more"]
            new_answers = [_construct_answer(item) for item in res["items"]]
            answers.extend(new_answers)
            page_id += 1
        return answers

    def insert_questions(self, questions):
        for q in questions:
            self.db_session.merge(q)
        self.db_session.commit()

    def insert_answers(self, answers):
        for a in answers:
            self.db_session.merge(a)
        self.db_session.commit()

def _construct_question(q):
    return dbmodel.Question(
        question_id=q["question_id"],
        title=q["title"],
        body=q["body"],
        user_id=q["owner"]["user_id"],
        url=q["link"],
        created=datetime.fromtimestamp(q["creation_date"]),
        updated=datetime.fromtimestamp(q["last_activity_date"]),
        vote_count=q["score"],
        answer_count=q["answer_count"],
        view_count=q["view_count"]
    )


def _construct_answer(a):
    return dbmodel.Answer(
        answer_id=a["answer_id"],
        question_id=a["question_id"],
        user_id=a["owner"]["user_id"],
        body=a["body"],
        created=datetime.fromtimestamp(a["creation_date"]),
        updated=datetime.fromtimestamp(a["last_activity_date"]),
        is_accepted=a["is_accepted"],
        vote_count=a["score"]
    )
