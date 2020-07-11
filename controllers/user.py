import web
import db
import hashlib
from web import ctx

from tools import pretty_date
from models.user import User

urls = (
    # '/login', 'login',
    # '/register', 'register',
    # '/logout', 'logout',
    '/user/(\d+)', 'user')

app = web.application(urls, globals())


class logout:

    def GET(self):
        ctx.session.kill()
        return web.seeother('/', absolute=True)


class login:

    def valid_email_password(self, username, password):
        pwdhash = hashlib.md5(password).hexdigest()
        user = db.session.query(User).filter_by(
            name=username, password=pwdhash).first()
        if not user:
            return False
        else:
            ctx.session.user = user
            return True

    login_form = web.form.Form(
        web.form.Textbox(
            'username', web.form.notnull,
            size=30,
            description="username:"),
        web.form.Password(
            'password', web.form.notnull,
            size=30,
            description="password:"),
        web.form.Button('login'),
    )

    def GET(self):
        url = web.input(url='').url
        login_form = self.login_form()
        login_form.fill({'url': url})

        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.user.login(login_form, "Log in")

    def POST(self):
        i = web.input()
        login_form = self.login_form()
        login_success = self.valid_email_password(i.username, i.password)
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session,
                'hasattr': hasattr, 'pretty_date': pretty_date})

        if (not login_form.validates()) or (not login_success):
            return render.user.login(login_form, "Log in")
        else:
            ctx.session.logged_in = True
            ctx.session.username = ctx.session.user.name
            web.seeother('/', absolute=True)


class register:

    def not_user_exists(username):
        user = db.session.query(User).filter_by(name=username).first()
        if not user:
            return True
        else:
            return False

    def not_email_exists(email):
        email = db.session.query(User).filter_by(email=email).first()
        if not email:
            return True
        else:
            return False

    user_exists_validator = web.form.Validator(
        'Username already taken.', not_user_exists)

    vpass = web.form.regexp(
        r".{3,20}$", 'must be between 3 and 20 characters')
    vemail = web.form.regexp(
        r".*@.*", "must be a valid email address")

    registration_form = web.form.Form(
        web.form.Textbox(
            'username', web.form.notnull, user_exists_validator,
            size=30,
            description="username:"),
        web.form.Password(
            'password', web.form.notnull, vpass,
            size=30,
            description="password:", type="password"),
        web.form.Password(
            "password2", web.form.notnull, vpass,
            description="repeat password:"),
        web.form.Button('sign up'),
        validators=[
            web.form.Validator(
                "Passwords didn't match", lambda i: i.password == i.password2)]
    )

    def GET(self):
        url = web.input(url='').url

        registration_form = self.registration_form()
        registration_form.fill({'url': url})

        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.user.login(registration_form, "Sign up")

    def POST(self):
        i = web.input()

        registration_form = self.registration_form()
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})

        if not registration_form.validates():
            return render.user.login(registration_form, "Sign up")
        else:
            pwdhash = hashlib.md5(i.password).hexdigest()
            u = User(name=i.username, password=pwdhash)
            db.session.add(u)
            db.session.commit()

            ctx.session.logged_in = True
            ctx.session.username = u.name
            ctx.session.user = u

            web.seeother('/', absolute=True)


class user:
    def GET(self, id):
        render = web.template.render(
            'templates/', base='layout',
            globals={
                'session': ctx.session, 'hasattr': hasattr,
                'pretty_date': pretty_date})
        return render.user.show(id)
