import web
import db

from web import ctx

urls = ('/(\d+)/upvote', 'upvote_comment')
app = web.application(urls, globals())


class upvote_comment:

    def GET(self, id):
        username = None
        if hasattr(ctx.session, 'username'):
            username = ctx.session.username
        else:
            return web.seeother('/user/register', absolute=True)

        voted = db.session.query(CommentVote).filter_by(
            comment_id=id,
            user_id=ctx.session.user.id).first()

        if not voted:
            vote = CommentVote(comment_id=id, user_id=ctx.session.user.id)
            db.session.add(vote)

        comment = db.session.query(Comment).filter_by(id=id).first()

        return web.seeother("/link/%d" % int(comment.link_id), absolute=True)
