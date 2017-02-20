import os

from flask import Flask, redirect, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from whitenoise import WhiteNoise
from wtforms_sqlalchemy.orm import model_form

flask_app = Flask(__name__)
app = WhiteNoise(flask_app, root='static/')

flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default='postgres://dsanders@localhost/wheres_the_changelog')
flask_app.secret_key = 'derp'

db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app, db)


class Changelog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    changelog_url = db.Column(db.String)
    package_name = db.Column(db.String)


ChangelogForm = model_form(Changelog, base_class=FlaskForm)


@flask_app.route('/', methods=('GET', 'POST'))
def main():
    form = ChangelogForm()
    if form.validate_on_submit():
        changelog = Changelog(package_name=form.package_name.data, changelog_url=form.changelog_url.data)
        db.session.add(changelog)
        db.session.commit()
        return redirect('/')
    changelogs = Changelog.query.all()
    return render_template('base.html', changelogs=changelogs, form=form)


@flask_app.route('/<package_name>')
def where_is_it(package_name):
    try:
        the_changelog = Changelog.query.filter_by(package_name=package_name).first()
        return redirect(the_changelog.changelog_url)
    except:
        return redirect('/')
