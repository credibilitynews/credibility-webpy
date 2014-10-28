from sqlalchemy import Column, Integer, DateTime, String, \
    Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref, object_session

from models import Base
from models.base_extension import TimestampExtension
from models.user import User
from models.link import Link, LinkVote
from models.tag import topic_tags_association_table

from datetime import datetime
import time
import math


class Topic(Base):
    __tablename__ = 'topics'
    __mapper_args__ = {'extension': TimestampExtension()}

    id = Column(Integer, primary_key=True)
    title = Column(String(256))
    hashtag = Column(String(256))
    user_id = Column(Integer, ForeignKey('users.id'))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    views = Column(Integer)

    user = relationship("User")
    tags = relationship("Tag", secondary=topic_tags_association_table)

    def __init__(self, title, hashtag, user_id):
        self.title = title
        self.hashtag = hashtag
        self.user_id = user_id

    def __repr__(self):
        return "<Topic('%s','%s', %d)>" \
            % (self.title, self.hashtag, self.user_id)

    def _get_points(self):
        # hackernews ranking algorithm
        t = time.mktime(datetime.now().timetuple()) \
            - time.mktime(self.created_at.timetuple())
        p = object_session(self).query(
            distinct(TopicVote.user_id)).filter_by(topic_id=self.id).count()
        points = (p - 1) / math.pow(t + 2, 1.8)
        return points
    points = property(_get_points)

    def _get_votes(self):
        return object_session(self).query(
            distinct(TopicVote.user_id)).filter_by(topic_id=self.id).count()
    votes = property(_get_votes)

    def _get_left_stories(self):
        stories = object_session(self).query(
            Link).filter_by(topic_id=self.id, type=1).all()
        return sorted(stories, key=lambda story: story.points, reverse=True)
    left_stories = property(_get_left_stories)

    def _get_right_stories(self):
        stories = object_session(self).query(
            Link).filter_by(topic_id=self.id, type=2).all()
        return sorted(stories, key=lambda story: story.points, reverse=True)
    right_stories = property(_get_right_stories)

    def _get_fact_stories(self):
        stories = object_session(self).query(
            Link).filter_by(topic_id=self.id, type=0).all()
        return sorted(stories, key=lambda story: story.points, reverse=True)
    fact_stories = property(_get_fact_stories)

    def _get_story_count(self):
        return object_session(self).query(
            Link).filter_by(topic_id=self.id).count()
    story_count = property(_get_story_count)


class TopicVote(Base):
    __tablename__ = 'topic_votes'
    __mapper_args__ = {'extension': TimestampExtension()}

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    topic_id = Column(Integer, ForeignKey('topics.id'))

    user = relationship("User")
    topic = relationship("Topic")
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    UniqueConstraint('user_id', 'topic_id', name='one_vote_per_user')

    def __init__(self, topic_id, user_id):
        self.topic_id = topic_id
        self.user_id = user_id

    def __repr__(self):
        return "<TopicVote(%d, %d)>" % (self.topic_id, self.user_id)
