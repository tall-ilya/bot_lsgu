import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, BigInteger, TIMESTAMP, BOOLEAN, DECIMAL, Table, \
    select, Time, Date
from sqlalchemy_utils import ChoiceType
from .base import BaseModel, Base
from sqlalchemy.orm import relationship
from .enums import LessonNumber


class AbstractLesson(BaseModel):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    lesson_number = Column(ChoiceType(LessonNumber, impl=Integer()))
    title = Column(String(20), nullable=False) # for example "Физика"
    cabinet_number = Column(String, nullable=False)


class Lesson(AbstractLesson):
    __tablename__ = "lessons"

    teacher_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    teacher = relationship("User", back_populates="teacher_lessons", uselist=False)
    schedule_day_id = Column(BigInteger, ForeignKey("scheduleDays.id"))
    schedule_day = relationship("ScheduleDay", uselist=False, back_populates="lessons", lazy="selectin")


class ReplacementLesson(AbstractLesson):
    __tablename__ = "replacementLessons"

    date = Column(Date)
    teacher_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    teacher = relationship("User", uselist=False)
    schedule_day_id = Column(BigInteger, ForeignKey("scheduleDays.id"))
    schedule_day = relationship("ScheduleDay", uselist=False, back_populates="replacement_lessons", lazy="selectin")