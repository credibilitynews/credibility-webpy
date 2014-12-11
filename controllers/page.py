import hashlib
import web
import db
import re
import collections
import requests
import operator
import json
from web import ctx
from sqlalchemy import desc, sql

from tools import pretty_date, shorten_link
from models.tag import Tag
from models.link import Link
from models.topic import Topic

urls = (
    '/about', 'about',
    '/faq', 'faq',
    '/contact', 'contact',
    '/favicon.ico', 'favicon',
    "/home", "index")

app = web.application(urls, locals())


class favicon:
    def GET(self):
        raise web.redirect('/static/favicon.ico')


class index:

    def all_tags(self):
        return sorted(
            db.session.query(Tag).filter(Tag.parent_id == sql.expression.null()),
            cmp=lambda x, y: cmp(x.name, y.name))

    def all_topics(self):
        topics = {}
        for tag in self.all_tags():
            topics[tag] = sorted(
                tag.topics, key=lambda topic: topic.points, reverse=True)[:3]
        return collections.OrderedDict(sorted(topics.items()))

    def latest_topics(self):
        return db.session.query(Topic) \
            .order_by(desc(Topic.created_at)).limit(5)

    def latest_articles(self):
        return db.session.query(Link).order_by(desc(Link.created_at)).limit(5)

    def GET(self):
        topics = self.all_topics()
        tags = self.all_tags()
        latest_topics = self.latest_topics()
        latest_articles = self.latest_articles()

        web.header('Content-Type', 'application/json')
        web.header('Access-Control-Allow-Origin', 'http://localhost:8000')
        web.header('Access-Control-Allow-Credentials', 'true')
        return json.dumps({
            "data": {
                "latest_topics": [i.serialize for i in latest_topics],
                "categories": [i.serialize for i in tags],
                "latest_articles": [i.serialize for i in latest_articles],
                "topics": [i.serialize for i in topics]
            }
        })


class latest:
    def all_tags(self):
        return sorted(
            db.session.query(Tag).all(),
            cmp=lambda x, y: cmp(x.name, y.name))

    def latest_topics(self):
        return db.session.query(Topic)\
            .order_by(desc(Topic.created_at)).limit(10)

    def GET(self):
        tags = self.all_tags()
        tag = type('Tag', (object,), {"name": "Latest Topics"})
        topics = self.latest_topics()

        web.header('Content-Type', 'application/json')
        return json.dumps({
            "data": {
                "tags": [i.serialize for i in tags],
                "topics": [i.serialize for i in topics]
            }
        })


class about:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return json.dumps({
            "data": {
                "text": ""
            }
        })


class faq:
    def GET(self):
        web.header('Content-Type', 'application/json')
        return json.dumps({
            "data": {
                "text": ""
            }
        })


class contact:
    def GET(self):
        return json.dumps({
            "data": {
                "text": ""
            }
        })
