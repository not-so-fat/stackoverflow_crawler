import pytest
from stackoverflow_crawler import StackoverflowCrawler


@pytest.fixture
def instantiate():
    db_url = "sqlite:///test.db"
    tag = "python"
    return StackoverflowCrawler(db_url, tag)


def test(instantiate):
    crawler = instantiate
    # replace later
    assert isinstance(crawler, StackoverflowCrawler)
