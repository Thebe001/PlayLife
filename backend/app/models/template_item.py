from sqlalchemy import Column, Integer, String, ForeignKey
from app.db import Base


class TemplateItem(Base):

    __tablename__ = "template_items"

    id = Column(Integer, primary_key=True, index=True)

    template_id = Column(Integer, ForeignKey("day_templates.id"))

    habit_id = Column(Integer)

    task_title = Column(String)

    points = Column(Integer)

    order = Column(Integer)