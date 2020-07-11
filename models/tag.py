from sqlalchemy import Table, Column, Integer, DateTime, String, \
    Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref, object_session

from models import Base
from models.user import User
from models.link import Link, LinkVote

topic_tags_association_table = Table(
    'topic_tags', Base.metadata,
    Column('topic_id', Integer, ForeignKey('topics.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    code = Column(String(256))
    parent_id = Column(Integer, ForeignKey('tags.id'))

    children = relationship("Tag")
    parent = relationship("Tag", remote_side=[id])
    topics = relationship(
        "Topic", secondary=topic_tags_association_table, lazy='dynamic')

    def __init__(self, name, code, parent_id):
        self.name = name
        self.code = code
        self.parent_id = parent_id

    def __repr__(self):
        return "<Tag('%s','%s')>" % (self.name, self.code)

    def __gt__(self, tag):
        return self.name > tag.name
