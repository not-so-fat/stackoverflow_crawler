from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship, 
    sessionmaker
)


Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    body = Column(String) # body (not markdown)
    user_id = Column(String) # owner - user_id
    url = Column(String) # link
    created = Column(DateTime) # creation_date
    updated = Column(DateTime) # last_activity_date
    vote_count = Column(Integer) # score
    answer_count = Column(Integer)
    view_count = Column(Integer)


class Answer(Base):
    __tablename__ = 'answers'
    answer_id = Column(String, primary_key=True, index=True)
    question_id = Column(String, ForeignKey('questions.question_id'))
    user_id = Column(String) # owner - user_id
    body = Column(String) # not markdown
    created = Column(DateTime) # creation_date
    updated = Column(DateTime) # last_activity_date
    is_accepted = Column(Boolean)
    vote_count = Column(Integer) # score
    question = relationship("Question", back_populates="answers")


Question.answers = relationship("Answer", order_by=Answer.answer_id, back_populates="question")


def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
