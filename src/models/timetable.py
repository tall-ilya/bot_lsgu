from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, BigInteger, TIMESTAMP, BOOLEAN, DECIMAL, Table, \
    select, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from .base import BaseModel, Base
from .enums import LessonNumber


class Timetable(BaseModel):
    __tablename__ = "timetables"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(20), nullable=False) # for example 'usual' or 'short'
    timetable_lessons = relationship("TimetableLesson", back_populates="timetable", uselist=True, lazy="selectin")
    holidays = relationship("Holiday", back_populates="timetable", uselist=True, lazy="selectin")


class TimetableLesson(BaseModel):
    __tablename__ = "timetableLessons"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timetable_id = Column(BigInteger, ForeignKey("timetables.id"))
    timetable = relationship("Timetable", back_populates="timetable_lessons", uselist=False)
    lesson_number = Column(ChoiceType(LessonNumber, impl=Integer()))
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class Holiday(BaseModel):
    __tablename__ = "holidays"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    timetable_id = Column(BigInteger, ForeignKey("timetables.id"))
    timetable = relationship("Timetable", back_populates="holidays", uselist=False, lazy="selectin")
    date = Column(Date)
