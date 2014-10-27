import hashlib
import web
import db
import re
import collections
import requests
import json
import operator
from web import ctx

from tools import pretty_date, shorten_link
from models.tag import Tag
from models.link import Link
from models.topic import Topic
from sqlalchemy import desc

urls = (
    '/about', 'about',
    '/faq', 'faq',
    '/contact', 'contact',
    '/favicon.ico','favicon',
    "/home", "index")

app = web.application(urls, locals())

## home page
class index:
    def all_tags(self):
        return sorted(db.session.query(Tag).all(), cmp=lambda x,y: cmp(x.name, y.name))

    def all_topics(self):
        topics = {}
        for tag in self.all_tags():
            topics[tag] = sorted(tag.topics, key=lambda topic: topic.points, reverse=True)[:3]
        return collections.OrderedDict(sorted(topics.items()))
   
    def latest_topics(self):
        return db.session.query(Topic).order_by(desc(Topic.created_at)).limit(5)

    def latest_articles(self):
        return db.session.query(Link).order_by(desc(Link.created_at)).limit(5)

    def GET(self):
        render = web.template.render('templates/', base='layout', globals={'session':ctx.session, 'hasattr':hasattr,'pretty_date':pretty_date})
        username = None
        if hasattr(ctx.session,'username'):
            username = ctx.session.username

        topics = self.all_topics()        
        tags = self.all_tags()
        latest_topics = self.latest_topics()
        latest_articles = self.latest_articles()
         
        return render.index(tags, topics, latest_topics, latest_articles)

## favicon
class favicon:
    def GET(self):
        raise web.redirect('/static/favicon.ico')


#latest
class latest:
    def all_tags(self):
        return sorted(db.session.query(Tag).all(), cmp=lambda x,y: cmp(x.name, y.name))

    def latest_topics(self):
        return db.session.query(Topic).order_by(desc(Topic.created_at)).limit(10)
 
    def GET(self):
        render = web.template.render('templates/', base='layout', globals={'session':ctx.session, 'hasattr':hasattr, 'short': shorten_link, 'pretty_date': pretty_date })
        tags = self.all_tags()
        tag = type('Tag', (object,), { "name": "Latest Topics"})
        topics = self.latest_topics()
        return render.tag.show(id, tags, tag, topics)

## static pages
class about:
    def GET(self):
        render = web.template.render('templates/', base='layout', globals={'session':ctx.session, 'hasattr':hasattr,'pretty_date':pretty_date})
        return render.static.about()

class faq:
    def GET(self):
        render = web.template.render('templates/', base='layout', globals={'session':ctx.session, 'hasattr':hasattr,'pretty_date':pretty_date})
        return render.static.faq()

class contact:
    def GET(self):
        render = web.template.render('templates/', base='layout', globals={'session':ctx.session, 'hasattr':hasattr,'pretty_date':pretty_date})
        return render.static.contact()

