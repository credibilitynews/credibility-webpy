import time
import web
from web import ctx

from sqlalchemy import desc
from email.Utils import formatdate

import db
from models.link import Link, LinkVote

urls = ('/', 'feed')
app = web.application(urls, locals())


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class feed:
    def latest_articles(self):
        return db.session.query(Link).order_by(desc(Link.created_at)).limit(10)

    def last_link_date(self):
        last_link = db.session\
            .query(Link).order_by(desc(Link.created_at)).limit(1)

        return self.format_datetime(last_link[0].created_at)

    def topic_link(self, link):
        return '<a href="http://credibility.cc/topic/' + \
            str(link.topic.id) + '">' + link.topic.title + \
            ' ' + link.topic.hashtag+'</a>'

    def root_link(self):
        return '<a href="http://credibility.cc">Credibility.cc</a>'

    def format_datetime(self, datetime):
        return formatdate(time.mktime(datetime.timetuple()))

    def feed_posts(self):
        articles = self.latest_articles()
        posts = []
        for article in articles:
            post = {}
            post['title'] = article.title+' '+article.topic.hashtag
            post['link'] = article.url
            post['comments'] = 'http://credibility.cc/link/'+str(article.id)
            post['pub_date'] = self.format_datetime(article.created_at)
            post['guid'] = 'http://credibility.cc/link/'+str(article.id)

            post['body'] = 'More articles on ' + self.topic_link(article) + \
                ' available at ' + self.root_link()
            post['category'] = ' > '.join(
                [str(tag.name) for tag in article.topic.tags])

            posts.append(Struct(**post))
        return posts

    def GET(self):
        render = web.template.render('templates/')
        date = self.last_link_date()
        posts = self.feed_posts()
        category = "Latest Links"
        web.header('Content-Type', 'application/xml')
        return render.feed(date, category, posts)
