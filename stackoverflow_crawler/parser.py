import logging
import re
from datetime import datetime


def get_questions_from_search(page):
    raw_questions = page.find_all("div", {"class": "s-post-summary js-post-summary"})
    questions = []
    for question in raw_questions:
        question_id = question["data-post-id"]
        content = _parse_content(question.find("div", {"class": "s-post-summary--content"}))
        stats = _parse_stats(question.find("div", {"class": "s-post-summary--stats js-post-summary-stats"}))
        questions.append({
            **dict(question_id=question_id),
            **content,
            **stats
        })
    return questions


def _parse_content(content):
    return dict(
        url=content.find("a", {"class": "s-link"})["href"],
        updated=datetime.strptime(
            content.find("span", {"class": "relativetime"})["title"], 
            "%Y-%m-%d %H:%M:%SZ"
        ),
        title=content.find("a", {"class": "s-link"}).get_text(strip=True)
    )


def _parse_stats(stats):
    remove_last_s = lambda text: text if not text.endswith("s") else text[:-1]
    ans = {}
    # collect num_view, num_vote, and num_answer
    for elem in stats.find_all("div", class_="s-post-summary--stats-item"):
        unit = elem.find("span", "s-post-summary--stats-item-unit").get_text(strip=True)
        unit = f"num_{remove_last_s(unit)}"
        ans[unit] = _to_integer(elem.find("span", "s-post-summary--stats-item-number").get_text(strip=True))
    return ans


def _to_integer(s):
    s = s.lower().strip()
    return int(float(s[:-1]) * 1e3) if s.endswith('k') \
            else int(float(s[:-1]) * 1e6) if s.endswith('m') \
            else int(s)


def parse_details(page, q):
    question_div = page.find("div", {"class": "question"})
    q["description"] = question_div.find("div", {"class": "s-prose js-post-body"}).get_text(strip=True)
    q["user_id"] = _extract_user_id(question_div.find_all("div", {"class": "user-details"}))
    answers = []
    for answer_div in page.find_all('div', {'class': 'answer'}):
        answers.append(dict(
            answer_id=answer_div["data-answerid"],
            question_id=q["question_id"],
            description=answer_div.find('div', {'class': 's-prose js-post-body'}).get_text(strip=True),
            updated=datetime.strptime(
                answer_div.find("time")["datetime"], 
                "%Y-%m-%dT%H:%M:%S"
            ),
            user_id=_extract_user_id(
                answer_div.find_all("div", {"class": "user-details"})
            ),
            num_vote=_to_integer(answer_div.find('div', {'class': 'js-vote-count'}).get_text(strip=True))
        ))
    return q, answers


def _extract_user_id(divs):
    for div in divs:
        atag = div.find("a")
        if atag:
            return re.search(r'/users/(\d+)/', atag["href"]).group(1)
    return ""
