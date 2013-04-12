from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import relationship, backref, object_session
from sqlalchemy.orm.interfaces import MapperExtension 
import db
from datetime import datetime

Base = declarative_base()


class BaseExtension(MapperExtension):  

  def before_insert(self, mapper, connection, instance):  
      instance.created_at = datetime.now()  

  def before_update(self, mapper, connection, instance):  
      instance.updated_at = datetime.now()


class User(Base):
  __tablename__ = 'users'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  name = Column(String(256))
  email = Column(String(256))
  password = Column(String(256))
  active = Column(Boolean, default=True)
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 

  def __init__(self, name, password):
    self.name = name
    self.password = password

  def __repr__(self):
    return "<User('%s','%s', '%s')>" % (self.name, self.password)





class Topic(Base):
  __tablename__ = 'topics'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  title = Column(String(256))
  hashtag = Column(String(256))
  user_id = Column(Integer, ForeignKey('users.id'))
  active = Column(Boolean, default=True)
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 
  views = Column(Integer) 

  user = relationship("User")

  def __init__(self, title, hashtag, user_id):
    self.title = title
    self.hashtag = hashtag
    self.user_id = user_id

  def __repr__(self):
     return "<Topic('%s','%s', %d)>" % (self.title, self.hashtag, self.user_id)
    
  def _get_points(self):
    return object_session(self).query(distinct(TopicVote.user_id)).filter_by(topic_id=self.id).count()
  
  points = property(_get_points)

  def _get_base_stories(self):
    stories =  object_session(self).query(Link).filter_by(topic_id=self.id, type=1).all()
    return  sorted(stories, key=lambda story: story.points, reverse=True)
  
  base_stories = property(_get_base_stories)

  def _get_alt_stories(self):
    stories =  object_session(self).query(Link).filter_by(topic_id=self.id, type=2).all()
    return  sorted(stories, key=lambda story: story.points, reverse=True)
  
  alt_stories = property(_get_alt_stories)

  def _get_story_count(self):
    return object_session(self).query(Link).filter_by(topic_id=self.id).count()
  
  story_count = property(_get_story_count)






class TopicVote(Base):
  __tablename__ = 'topic_votes'
  __mapper_args__ = { 'extension': BaseExtension() }

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





class Link(Base):
  __tablename__ = 'links'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  title = Column(String(256))
  url = Column(String(256))
  user_id = Column(Integer, ForeignKey('users.id'))
  topic_id = Column(Integer, ForeignKey('topics.id'))
  type = Column(Integer)
  active = Column(Boolean, default=True)
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 
  views = Column(Integer) 

  user = relationship("User")
  topic = relationship("Topic")

  def __init__(self, title, url, user_id, topic_id, type):
    self.title = title
    self.url = url
    self.user_id = user_id
    self.topic_id = topic_id
    self.type = type

  def __repr__(self):
     return "<Link('%s','%s', %d, %d)>" % (self.title, self.url, self.user_id, self.topic_id)

  def _get_points(self):
    return object_session(self).query(distinct(LinkVote.user_id)).filter_by(link_id=self.id).count()
  
  points = property(_get_points)

  def _get_comments_count(self):
    return object_session(self).query(Comment).filter_by(link_id=self.id).count()
  
  comments_count = property(_get_comments_count)

  def _get_comments(self):
    comments =  object_session(self).query(Comment).filter_by(link_id=self.id).all()
    return  sorted(comments, key=lambda comment: comment.points, reverse=True)
    
  comments = property(_get_comments)



class LinkVote(Base):
  __tablename__ = 'link_votes'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  user_id = Column(Integer, ForeignKey('users.id'))
  link_id = Column(Integer, ForeignKey('links.id'))
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 

  user = relationship("User")
  link = relationship("Link")

  def __init__(self, link_id, user_id):
    self.link_id = link_id
    self.user_id = user_id

  def __repr__(self):
     return "<LinkVote(%d, %d)>" % (self.link_id, self.user_id)






class Comment(Base):
  __tablename__ = 'comments'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  content = Column(Text)
  user_id = Column(Integer, ForeignKey('users.id'))
  link_id = Column(Integer, ForeignKey('links.id'))
  active = Column(Boolean, default=True)
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 

  user = relationship("User")
  link = relationship("Link")

  def __init__(self, content, user_id, link_id):
    self.content = content
    self.user_id = user_id
    self.link_id = link_id

  def __repr__(self):
     return "<Link('%s', %d, %d)>" % (self.content, self.user_id, self.link_id)

  def _get_points(self):
    return object_session(self).query(distinct(CommentVote.user_id)).filter_by(comment_id=self.id).count()
  
  points = property(_get_points)




class CommentVote(Base):
  __tablename__ = 'comment_votes'
  __mapper_args__ = { 'extension': BaseExtension() }

  id = Column(Integer, primary_key=True)
  user_id = Column(Integer, ForeignKey('users.id'))
  comment_id = Column(Integer, ForeignKey('comments.id'))
  created_at = Column(DateTime) 
  updated_at = Column(DateTime) 

  user = relationship("User")
  comment = relationship("Comment")

  def __init__(self, comment_id, user_id):
    self.comment_id = comment_id
    self.user_id = user_id

  def __repr__(self):
     return "<LinkVote(%d, %d)>" % (self.user_id, self.comment_id)




users_table = User.__table__
metadata = Base.metadata

from db import engine
if __name__ == "__main__":
    metadata.create_all(engine)