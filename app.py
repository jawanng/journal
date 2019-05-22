from flask import (Flask, g, render_template, flash, redirect,
                   url_for, abort, request)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user,
                         current_user, login_required, logout_user)
from slugify import slugify
from peewee import IntegrityError

import forms
import models

app = Flask(__name__)
app.secret_key = 'this is our super secret key. do not share it with anyone!'
models.initialize()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    """Grabs the current user"""
    try:
        return models.User.select().where(
            models.User.id == int(user_id)
        ).get()
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Makes the current user available to all of the models and templates"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Closes the database after every call"""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Link and place for registration"""
    form = forms.SignUpForm()
    if form.validate_on_submit():
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        flash("Thanks for registering!")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Link and form for login"""
    form = forms.SignInForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(
                models.User.email == form.email.data
            )
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You're now logged in!")
                return redirect(url_for('index'))
            else:
                flash("No user with that email/password combo")
        except models.DoesNotExist:
            flash("No user with that email/password combo")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Log out the current user and redirect to /index"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/entries/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(slug):
    """Allows the editing of an entry include tags as a string"""
    try:
        result = models.Journal.get(slug=slug)
    except models.DoesNotExist:
        abort(404)

    form = forms.JournalCreateForm(obj=result)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(result)
        result.save()
        flash("Journal Entry Updated")
        return redirect(url_for('detail_entry', slug=result.slug))
    return render_template('edit.html', form=form)


@app.route('/entries/<slug>/delete')
@login_required
def delete_entry(slug):
    """Deletes an journal entry and redirect to /index"""
    try:
        result = models.Journal.get(slug=slug)
        result.delete_instance()
    except models.DoesNotExist:
        abort(404)
    return redirect(url_for('index'))


@app.route('/entries/<slug>')
def detail_entry(slug):
    """It shows the detail of a journal entry with tags"""
    try:
        result = models.Journal.get(slug=slug)
    except models.DoesNotExist:
        abort(404)

    return render_template('detail.html', journal=result, detail=True)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    """Creates a new journal entry with slugs"""
    form = forms.JournalCreateForm()
    if form.validate_on_submit():
        try:
            models.Journal.create(
                title=form.title.data,
                date=form.date.data,
                time_spent=form.time_spent.data,
                learned_info=form.learned_info.data,
                resources=form.resources.data,
                slug=slugify(form.title.data),
                tags=form.tags.data
            )
            flash("Journal Entry Added")
            return redirect(url_for('index'))
        except IntegrityError:
            flash("This is a duplicate entry")
    return render_template('new.html', form=form)


@app.route('/entries')
@app.route('/')
def index():
    """/index and /entries which gives a list of journal entries"""
    results = models.Journal.select()
    return render_template('index.html', journals=results)


@app.route('/tag/<name>')
def show_tag(name):
    """Gives a list of journal entries for a given tag"""
    try:
        result = models.Journal.select().where(models.
                                               Journal.tags.contains(name))
    except models.DoesNotExist:
        abort(404)

    return render_template('tag.html', journals=result, name=name)


if __name__ == '__main__':
    app.run()

