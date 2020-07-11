from sqlalchemy import Column, Integer, DateTime, String, \
    Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref, object_session

from models import Base
from models.user import User


class Comment(Base):
    __tablename__ = 'comments'

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
        return "<Link('%s', %d, %d)>" \
            % (self.content, self.user_id, self.link_id)

    def _get_points(self):
        return object_session(self).query(
            distinct(CommentVote.user_id)).filter_by(
                comment_id=self.id).count()

    points = property(_get_points)


class CommentVote(Base):
    __tablename__ = 'comment_votes'

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
