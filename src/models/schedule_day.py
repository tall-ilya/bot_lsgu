import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, BigInteger, TIMESTAMP, BOOLEAN, DECIMAL, Table, \
    select, Time
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType
from .base import BaseModel, Base
from .enums import GroupNumbers, DayOfTheWeek


class ScheduleDay(BaseModel):
    __tablename__ = "scheduleDays"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_number = Column(ChoiceType(GroupNumbers, impl=Integer()))
    day_of_the_week = Column(ChoiceType(DayOfTheWeek, impl=Integer()))
    lessons = relationship("Lesson", uselist=True, back_populates="schedule_day", lazy="selectin")
    replacement_lessons = relationship("ReplacementLesson", uselist=True, back_populates="schedule_day", lazy="selectin")

