import os
from sqlalchemy import Column, Integer, DateTime, String, \
    Boolean, ForeignKey, distinct, UniqueConstraint, Text
from sqlalchemy.orm import relationship, backref, object_session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from base_extension import TimestampExtension
from models import Base


class User(Base):
    __tablename__ = 'users'
    __mapper_args__ = {'extension': TimestampExtension()}

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

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def generate_auth_token(self, expiration = 600):
        s = Serializer(os.environ['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.query.get(data['id'])
        return user
