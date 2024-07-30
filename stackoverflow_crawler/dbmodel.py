from sqlalchemy import create_engine, inspect, Column, String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    user_id = Column(String)
    url = Column(String)
    updated = Column(TIMESTAMP)
    num_vote = Column(Integer)
    num_answer = Column(Integer)
    num_view = Column(Integer)


class Answer(Base):
    __tablename__ = 'answers'
    answer_id = Column(String, primary_key=True, index=True)
    question_id = Column(String, ForeignKey('questions.question_id'))
    description = Column(String)
    updated = Column(TIMESTAMP)
    user_id = Column(String)
    num_vote = Column(Integer)
    question = relationship("Question", back_populates="answers")


Question.answers = relationship("Answer", order_by=Answer.answer_id, back_populates="question")


def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
