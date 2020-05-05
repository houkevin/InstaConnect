"""Insta485."""
import os
import shutil
import uuid
import hashlib
import tempfile
import flask
import arrow
from PIL import Image
from insta485 import mail
from flask import Flask, render_template, url_for, flash, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Message
from flask_wtf.file import FileField, FileAllowed
import insta485

app = Flask(__name__)
flask.app.secret_key = (
        b'pT\xaf\x1dn\x8e\xe3\xf1\xfb?\x80\x93*2\x9d\xae\x846\xacrs.\x99/'
    )

class RegistrationForm(FlaskForm):
    fullname = StringField('Name', validators=[DataRequired()])
    picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    fullname = StringField('Name')
    email = StringField('Email')
    submit = SubmitField('Update')

class UpdatePassword(FlaskForm):
    password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('New Password, again', validators=[DataRequired()])
    submit = SubmitField('Update')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

def send_reset_email(email):
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset', _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@insta485.app.route('/reset_password', methods=['GET','POST'])
def reset_request():
    form = RequestResetForm()
    connection = insta485.model.get_db()
    if flask.request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        cur = connection.execute(
            "SELECT username FROM users "
            "WHERE email = '%s' "
            % email
        )
        cur = cur.fetchall()
        if not cur:
            flash('Email does not exist!', 'danger')
            return flask.render_template('reset_request.html', title='Reset Password', form=form)
        else:
            send_reset_email(email)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return flask.redirect(url_for('login'))
    return flask.render_template('reset_request.html', title='Reset Password', form=form)

@insta485.app.route('/reset', methods=['GET','POST'])
def reset():
    form = ResetPasswordForm()
    if flask.request.method == "POST" and form.validate_on_submit():
        username = flask.session['username']
        password = form.password.data
        confirm = form.confirm_password.data

        connection = insta485.model.get_db()
        if (password == '' and confirm == ''):
            flash('Passwords cannot be empty!', 'danger')
            return flask.render_template("password_account.html", title='Change Password', form=form)
        if (password != confirm):
            flash('Passwords do not match!', 'danger') 
            return flask.render_template("password_account.html", title='Change Password', form=form)
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join(
            [
                algorithm,
                salt,
                password_hash
            ]
            )
        connection.execute(
            "UPDATE users SET password = '%s' WHERE username = '%s'"
            % (password_db_string, username)
        )
        flash('Successfully changed password!', 'success')
        return flask.redirect(flask.url_for('login'))
    return flask.render_template('reset_request.html', title='Reset Password', form=form)

@insta485.app.route('/')
def show_index():
    """Display / route."""
    print("flask session object: " + str(flask.session))
    if not logged_in():
        print("Not logged in. Redirecting to login page.")
        return flask.redirect(flask.url_for('login'))
    # Connect to database
    connection = insta485.model.get_db()
    # Query database
    # only include those person is following, and own posts.
    cur = connection.execute(
        (
            "SELECT * "
            "FROM posts "
            "WHERE owner "
            "IN "
            "(SELECT username2 FROM following WHERE username1 = '%s') "
            "OR owner = '%s' ORDER BY created DESC "
        )
        % (flask.session['username'], flask.session['username'])
    )
    posts = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM comments "
    )
    comments = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM users "
    )
    users = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM likes "
    )
    likes = cur.fetchall()
    cur_user = flask.session['username']

    cur = connection.execute(
        (
            "SELECT postid "
            "FROM likes "
            "WHERE owner = '%s'"
        )
        % cur_user)
    has_liked = cur.fetchall()
    # set the timestamps to time from now
    for post in posts:
        created = arrow.get(post['created'])
        post['created'] = created.humanize()
    # Add database info to context
    context = (
        {
            "posts": posts,
            "likes": likes,
            "comments": comments,
            "users": users,
            "cur_user": cur_user,
            "hasLiked": has_liked
        }
    )
    return flask.render_template("index.html", **context)


@insta485.app.route('/like/', methods=['POST'])
def like():
    """Handle like button."""
    if not logged_in():
        flask.abort(403)
    connection = insta485.model.get_db()
    if flask.request.method == "POST":
        connection.execute(
            (
                "INSERT INTO likes(owner, postid) "
                "VALUES('%s','%s')"
            )
            % (flask.session['username'], flask.request.form['postid'])
        )
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("index.html")


@insta485.app.route('/unlike/', methods=['POST'])
def unlike():
    """Handle like button."""
    if not logged_in():
        flask.abort(403)
    connection = insta485.model.get_db()
    if flask.request.method == "POST":
        connection.execute(
            (
                "DELETE FROM likes "
                "WHERE owner = '%s' and postid = '%s'"
            )
            % (flask.session['username'], flask.request.form['postid'])
        )
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("index.html")


@insta485.app.route('/comment/', methods=['POST'])
def comment():
    """Handle comment button."""
    if not logged_in():
        flask.abort(403)
    connection = insta485.model.get_db()
    if flask.request.method == "POST":
        connection.execute(
            (
                "INSERT INTO comments(owner, postid, text) "
                "VALUES('%s','%s','%s')"
            )
            % (flask.session['username'], flask.request.form['postid'],
               flask.request.form['text'])
        )
        return flask.redirect(flask.url_for('show_index'))
    return flask.render_template("index.html")


@insta485.app.route('/uncomment/', methods=['POST'])
def uncomment():
    """Handle uncomment button."""
    if not logged_in():
        flask.abort(403)
    connection = insta485.model.get_db()
    if flask.request.method == "POST":
        # so that we canget the postid for redirect
        cur = connection.execute(
            (
                "SELECT postid "
                "FROM comments WHERE commentid = '%s'"
            )
            % (flask.request.form['commentid'])
        )
        get_postid = cur.fetchall()
        # delete the comment
        connection.execute(
            "DELETE FROM comments WHERE commentid = '%s'" %
            (flask.request.form['commentid'])
        )
        return flask.redirect(
            flask.url_for('user_post', postid=get_postid[0]['postid']))
    return flask.render_template("post.html")


@insta485.app.route('/p/<path:postid>/', methods=['GET', 'POST'])
def user_post(postid):
    """Display post page."""
    connection = insta485.model.get_db()
    if flask.request.method == "POST":
        if not logged_in():
            return flask.abort(403)

        if flask.request.form.get('comment'):
            connection.execute(
                (
                    "INSERT INTO comments(owner, postid, text) "
                    "VALUES('%s','%s','%s')"
                )
                % (flask.session['username'], flask.request.form['postid'],
                   flask.request.form['text'])
            )
        elif flask.request.form.get('uncomment'):
            # make sure only comment owner can uncomment.
            cur = connection.execute(
                (
                    "SELECT owner "
                    "FROM comments WHERE commentid = '%s'"
                )
                % (flask.request.form['commentid'])
            )
            check_comment = cur.fetchall()
            if check_comment[0]['owner'] != flask.session['username']:
                return flask.abort(403)
            # delete the comment
            connection.execute(
                "DELETE FROM comments WHERE commentid = '%s'" %
                (flask.request.form['commentid'])
            )
        elif flask.request.form.get('like'):
            connection.execute(
                (
                    "INSERT INTO likes(owner, postid) "
                    "VALUES('%s','%s')"
                )
                % (flask.session['username'], flask.request.form['postid'])
            )
        elif flask.request.form.get('unlike'):
            connection.execute(
                (
                    "DELETE FROM likes "
                    "WHERE owner = '%s' and postid = '%s'"
                )
                % (flask.session['username'], flask.request.form['postid'])
            )
        elif flask.request.form.get('delete'):
            cur = connection.execute(
                "SELECT owner FROM posts WHERE postid = '%s'" %
                (flask.request.form['postid'])
            )
            username = cur.fetchall()
            if username[0]['owner'] != flask.session['username']:
                flask.abort(403)
            # delete image file
            cur = connection.execute(
                "SELECT filename FROM posts WHERE postid = '%s'"
                % (flask.request.form['postid'])
            )
            filename = cur.fetchall()
            filepath = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                filename[0]['filename']
            )
            os.remove(filepath)
            connection.execute(
                "DELETE FROM posts WHERE postid = '%s'" %
                (flask.request.form['postid'])
            )
            return flask.redirect(
                flask.url_for('user', username=flask.session['username']))

    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    username = flask.session['username']
    # get the correct post information based on postid
    cur = connection.execute(
        (
            "SELECT * "
            "FROM posts "
            "WHERE postid = '%s'"
        )
        % (postid))
    posts = cur.fetchall()

    # get the comments for the post
    cur = connection.execute(
        (
            "SELECT * "
            "FROM comments "
            "WHERE postid = '%s'"
        )
        % (postid))
    comments = cur.fetchall()

    # timestamp calculation
    for post in posts:
        created = arrow.get(post['created'])
        post['created'] = created.humanize()

    # determine if like/unlike should appear on post
    cur = connection.execute(
        "SELECT postid "
        "FROM likes "
        "WHERE owner = '%s'"
        % username
        )
    has_liked = cur.fetchall()

    # get the number of likes for the post
    cur = connection.execute(
        "SELECT * FROM likes "
    )
    likes = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM users "
        "WHERE username = '%s'"
        % posts[0]['owner']
        )
    user_info = cur.fetchall()

    context = (
        {
            "posts": posts,
            "cur_user": username,
            "comments": comments,
            "hasLiked": has_liked,
            "likes": likes,
            "user_info": user_info
        }
    )
    return flask.render_template("post.html", **context)

# Account functions
@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def login():
    """Display login page."""
    if logged_in():
        print("Already logged in. Redirecting to index page.")
        return flask.redirect(flask.url_for('show_index'))
    # error = None
    form = LoginForm()
    if flask.request.method == "POST":
        username = form.username.data
        password = form.password.data

        print("Username in post request: " + username)
        connection = insta485.model.get_db()
        cur = connection.execute(
            (
                "SELECT password "
                "FROM users "
                "WHERE username = '%s'"
            )
            % (username)
            )
        check = cur.fetchall()
        # if no username match, abort
        if form.validate_on_submit():
            if not check:
                flash('Login Unsuccessful. Please check username and password', 'danger')
                return flask.render_template("login.html", title='Login', form=form)

            pass_sql = check[0]['password']
            pass_split = pass_sql.rsplit('$', 2)
            algorithm = pass_split[0]
            salt = pass_split[1]
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(str(salt + password).encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])
            if password_db_string == check[0]['password']:
                flash('You have been logged in!', 'success')
                flask.session['username'] = flask.request.form['username']
                return flask.redirect(flask.url_for('show_index'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return flask.render_template("login.html", title='Login', form=form)


@insta485.app.route('/accounts/logout/')
def logout():
    """Log the current user out."""
    flask.session.clear()
    return flask.redirect(flask.url_for('login'))


@insta485.app.route('/accounts/create/', methods=['GET', 'POST'])
def create_account():
    """Create an new account."""
    # redirect the user to edit their account if already logged in
    if flask.session.get('username'):
        return flask.redirect(flask.url_for('edit_account'))
    form = RegistrationForm()
    if flask.request.method == "POST" and form.validate_on_submit():
        connection = insta485.model.get_db()
        cur = connection.execute(
            "SELECT password FROM users WHERE username = '%s'"
            % (form.username.data)
        )
        user_exists = cur.fetchall()
        # abort if the user already exists
        if user_exists:
            flash('Username exists!', 'danger')
            return flask.render_template("create_account.html", title='Register', form=form)
        username = form.username.data
        email = form.email.data
        fullname = form.fullname.data
        password = form.password.data
        picture = form.picture.data
        # Hash the password
        algorithm = 'sha512'
        salt = uuid.uuid4().hex
        hash_obj = hashlib.new(algorithm)
        password_salted = salt + password
        hash_obj.update(password_salted.encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])
        if not picture:
            hash_filename = ""
        else:
            hash_filename = create_file_hash(picture)

        connection.execute(
            (
                "INSERT INTO "
                "users(username, fullname, email, password, filename) "
                "VALUES('%s', '%s', '%s', '%s', '%s')"
            )
            %
            (
                username,
                fullname,
                email,
                password_db_string,
                os.path.basename(hash_filename)
            )
        )
        flask.session['username'] = username
        flash(f'Account created for {form.username.data}!', 'success')
        return flask.redirect(flask.url_for('show_index'))

    return flask.render_template("create_account.html", title='Register', form=form)


@insta485.app.route('/accounts/edit/', methods=['GET', 'POST'])
def edit_account():
    """Edit an existing users account."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))

    connection = insta485.model.get_db()
    form = UpdateAccountForm()
    if flask.request.method == "POST" and form.validate_on_submit():
        fullname = form.fullname.data
        email = form.email.data
        picture = form.picture.data
        # update all of the fields if a new image is given
        # otherwise just update the name and email
        if picture:
            # The user uploaded a new profile pic
            hash_filename = create_file_hash(picture)
            # Delete the old photo from /var/uploads/ before replacing it
            cur = connection.execute(
                (
                    "SELECT filename "
                    "FROM users "
                    "WHERE username = '%s'"
                )
                % (flask.session['username'])
            )
            filename = cur.fetchall()
            filepath = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                filename[0]['filename']
                )
            if not os.path.isdir(filepath):
                os.remove(filepath)

            connection.execute(
                (
                    "UPDATE users "
                    "SET fullname = '%s', email = '%s', filename = '%s' "
                    "WHERE username = '%s'"
                )
                % (fullname, email,
                   os.path.basename(hash_filename), flask.session['username'])
            )
        else:
            cur = connection.execute(
                (
                    "UPDATE users "
                    "SET fullname = '%s', email = '%s'  "
                    "WHERE username = '%s'"
                )
                % (fullname, email,
                   flask.session['username'])
            )
        flash('Your account has been updated!', 'success')
        return flask.redirect(flask.url_for('edit_account'))

    cur = connection.execute(
        (
            "SELECT fullname, email, filename "
            "FROM users "
            "WHERE username = '%s'"
        )
        % (flask.session['username'])
    )

    user_data = cur.fetchall()
    cur = connection.execute(
        (
            "SELECT fullname, email, filename "
            "FROM users "
            "WHERE username = '%s'"
        )
        % (flask.session['username'])
    )

    cur_user = flask.session['username']

    content = {'user': user_data, 'cur_user': cur_user}
    return flask.render_template('edit_account.html', **content, form=form)


@insta485.app.route('/accounts/delete/', methods=['GET', 'POST'])
def delete_account():
    """Delete an existing account."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))

    if flask.request.method == "POST":
        connection = connection = insta485.model.get_db()

        cur = connection.execute(
            (
                "SELECT filename "
                "FROM posts "
                "WHERE owner = '%s'"
            )
            % (flask.session['username'])
        )
        files = cur.fetchall()
        # delete all of the images associated with a users posts
        for file in files:
            filepath = os.path.join(
                insta485.app.config["UPLOAD_FOLDER"],
                file['filename']
                )
            os.remove(filepath)
        cur = connection.execute(
            "SELECT filename FROM users WHERE username = '%s'"
            % (flask.session['username'])
        )

        profile_pic = cur.fetchall()

        filepath = os.path.join(
            insta485.app.config["UPLOAD_FOLDER"],
            profile_pic[0]['filename']
            )
        # delete the users profile picture
        if not os.path.isdir(filepath):
            os.remove(filepath)

        # Delete the user from the database
        # delete on cascade clean up all of the other tables
        connection.execute(
            "DELETE FROM users WHERE username = '%s'"
            % (flask.session['username'])
        )

        # Clear the session since the user no longer exists
        flask.session.clear()
        return flask.redirect(flask.url_for('create_account'))

    cur_user = flask.session['username']
    config = {'cur_user': cur_user}
    return flask.render_template("delete_account.html", **config)


@insta485.app.route('/accounts/password/', methods=['GET', 'POST'])
def change_password():
    """Change the password of an existing user."""
    form = UpdatePassword()
    if flask.request.method == 'POST' and form.validate_on_submit():
        username = flask.session['username']
        password = form.password.data
        new = form.new_password.data
        confirm = form.confirm_password.data

        connection = insta485.model.get_db()
        cur = connection.execute(
            (
                "SELECT password "
                "FROM users "
                "WHERE username = '%s'"
            )
            % (username)
            )
        check = cur.fetchall()
        if not check:
            flash('User does not exist!', 'danger')
            return flask.render_template("password_account.html", title='Change Password', form=form)

        pass_sql = check[0]['password']
        pass_split = pass_sql.rsplit('$', 2)
        algorithm = pass_split[0]
        salt = pass_split[1]
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(str(salt + password).encode('utf-8'))
        password_hash = hash_obj.hexdigest()
        password_db_string = "$".join([algorithm, salt, password_hash])

        # if doesn't match password in database, abort
        if password_db_string == check[0]['password']:
            if (new == '' and confirm == ''):
                flash('Passwords cannot be empty!', 'danger')
                return flask.render_template("password_account.html", title='Change Password', form=form)
            if (new != confirm):
                flash('Passwords do not match!', 'danger') 
                return flask.render_template("password_account.html", title='Change Password', form=form)
            algorithm = 'sha512'
            salt = uuid.uuid4().hex
            hash_obj = hashlib.new(algorithm)
            password_salted = salt + new
            hash_obj.update(password_salted.encode('utf-8'))
            password_hash = hash_obj.hexdigest()
            password_db_string = "$".join(
                [
                    algorithm,
                    salt,
                    password_hash
                ]
                )
            connection.execute(
                "UPDATE users SET password = '%s' WHERE username = '%s'"
                % (password_db_string, username)
            )
            flash('Successfully changed password!', 'success')
            return flask.redirect(flask.url_for('edit_account'))
        flash('Password is wrong!', 'danger')
        return flask.render_template("password_account.html", title='Change Password', form=form)

    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    print('I am here')
    return flask.render_template("password_account.html", title='Change Password', form=form)


@insta485.app.route('/uploads/<path:filename>')
def get_file(filename):
    """Return the filename located in /var/uploads/."""
    # users that aren't logged do not have access to uploads
    if not flask.session.get('username'):
        return flask.abort(403)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'],
        filename
        )


@insta485.app.route('/u/<path:username>/', methods=['GET', 'POST'])
def user(username):
    """Return a user page."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    if flask.request.method == 'POST':
        connection = insta485.model.get_db()
        if flask.request.form.get('follow'):
            # insert into the following table the new following tuple
            connection.execute(
                (
                    "INSERT INTO "
                    "following(username1,username2) "
                    "VALUES('%s','%s')"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
        elif flask.request.form.get('unfollow'):
            connection.execute(
                (
                    "DELETE FROM "
                    "following WHERE "
                    "username1 = '%s' and username2 = '%s'"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
    if (flask.request.method == "POST" and
            flask.request.files.get('file')):
        if username != flask.session['username']:
            return flask.abort(403)
        if not logged_in():
            return flask.abort(403)
        # create the post
        connection = insta485.model.get_db()
        print(flask.request.files['file'])
        hash_filename = create_file_hash(flask.request.files['file'])
        connection.execute(
            "INSERT INTO posts(filename, owner) VALUES('%s','%s')"
            % (os.path.basename(hash_filename), flask.session['username'])
        )

    connection = insta485.model.get_db()
    cur = connection.execute(
        (
            "SELECT username, fullname, email, filename "
            "FROM users "
            "WHERE username = '%s'"
        )
        % username
    )
    user_data = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM posts WHERE owner = '%s'" % username
    )
    user_posts = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username1 = '%s'" %
        (username)
    )
    num_following = cur.fetchall()

    cur = connection.execute(
        "SELECT COUNT(*) FROM following WHERE username2 = '%s'" %
        (username)
    )
    num_followers = cur.fetchall()

    following_val = str()
    # Check if the current user follows the logged in user
    if flask.session['username'] != username:
        cur = connection.execute(
            (
                "SELECT EXISTS"
                "(SELECT 1 "
                "FROM following "
                "WHERE username1 = '%s' AND username2 = '%s')"
            )
            % (flask.session['username'], username)
        )
        following_val = cur.fetchall()
        # theres gotta be a better way lol
        following_val = str(
            following_val[0][next(iter(following_val[0]))])
    else:
        following_val = -1

    cur_user = flask.session['username']
    context = (
        {
            "user": user_data,
            "user_posts": user_posts,
            "num_posts": len(user_posts),
            "cur_user": cur_user,
            "following": following_val,
            "num_followers": num_followers[0]['COUNT(*)'],
            "num_following": num_following[0]['COUNT(*)']
        }
        )

    # return "user page"
    return flask.render_template("user.html", **context)


@insta485.app.route('/u/<path:username>/followers/', methods=['GET', 'POST'])
def followers(username):
    """Return a followers page."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        if flask.request.form.get('follow'):
            # insert into the following table the new following tuple
            connection.execute(
                (
                    "INSERT INTO "
                    "following(username1,username2) "
                    "VALUES('%s','%s')"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
        elif flask.request.form.get('unfollow'):
            connection.execute(
                (
                    "DELETE FROM "
                    "following WHERE "
                    "username1 = '%s' and username2 = '%s'"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
    cur_user = flask.session['username']

    cur = connection.execute(
        "SELECT f.username1, u.filename "
        "FROM following f, users u "
        "WHERE username2 = '%s' AND u.username = f.username1 "
        "INTERSECT "
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        % (username, cur_user)
    )
    overlap_img_user = cur.fetchall()

    cur = connection.execute(
        "SELECT f.username1, u.filename "
        "FROM following f, users u "
        "WHERE username2 = '%s' AND u.username = f.username1 "
        "EXCEPT "
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        % (username, cur_user)
    )
    non_overlap_img_user = cur.fetchall()

    context = (
        {
            "username": username,
            "cur_user": cur_user,
            "overlap_img_user": overlap_img_user,
            "non_overlap_img_user": non_overlap_img_user
        }
        )

    # return "this users followers page"
    return flask.render_template("followers.html", **context)


@insta485.app.route('/u/<path:username>/following/', methods=['GET', 'POST'])
def following(username):
    """Return a following page."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        if flask.request.form.get('follow'):
            # insert into the following table the new following tuple
            connection.execute(
                (
                    "INSERT INTO "
                    "following(username1,username2) "
                    "VALUES('%s','%s')"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
        elif flask.request.form.get('unfollow'):
            connection.execute(
                (
                    "DELETE FROM "
                    "following WHERE "
                    "username1 = '%s' and username2 = '%s'"
                )
                % (flask.session['username'], flask.request.form['username'])
            )
    cur = connection.execute(
        (
            "SELECT username, fullname, email, filename "
            "FROM users "
            "WHERE username = '%s'"
        )
        % username
    )

    cur_user = flask.session['username']

    cur = connection.execute(
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        "INTERSECT "
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        % (username, cur_user)
    )
    overlap_img_user = cur.fetchall()

    cur = connection.execute(
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        "EXCEPT "
        "SELECT f.username2, u.filename "
        "FROM following f, users u "
        "WHERE username1 = '%s' AND u.username = f.username2 "
        % (username, cur_user)
    )
    non_overlap_img_user = cur.fetchall()

    context = (
        {
            "username": username,
            "cur_user": cur_user,
            "overlap_img_user": overlap_img_user,
            "non_overlap_img_user": non_overlap_img_user
        }
        )

    # return "this users following page"
    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/', methods=['GET', 'POST'])
def explore():
    """Explore page."""
    if not logged_in():
        return flask.redirect(flask.url_for('login'))
    connection = insta485.model.get_db()
    if flask.request.method == 'POST':
        # insert into the following table the new following tuple
        connection.execute(
            (
                "INSERT INTO following(username1,username2) "
                "VALUES('%s','%s')"
            )
            % (flask.session['username'], flask.request.form['username'])
        )
    # nested query to select those in users that are not in following
    cur = connection.execute(
        (
            "SELECT * FROM users "
            "WHERE username "
            "NOT IN "
            "(SELECT username2 FROM following WHERE username1 = '%s')"
        )
        % (flask.session['username'])
    )
    not_following = cur.fetchall()
    context = (
        {
            'not_following': not_following,
            'cur_user': flask.session['username']
        }
        )
    return flask.render_template("explore.html", **context)


def sha256sum(filename):
    """Return sha256 hash of file content, similar to UNIX sha256sum."""
    content = open(filename, 'rb').read()
    sha256_obj = hashlib.sha256(content)
    return sha256_obj.hexdigest()


def create_file_hash(filename):
    """Generate a hash filename."""
    dummy, temp_filename = tempfile.mkstemp()
    file = filename
    file.save(temp_filename)

    # Compute filename
    hash_txt = sha256sum(temp_filename)
    dummy, suffix = os.path.splitext(file.filename)
    hash_filename_basename = hash_txt + suffix
    hash_filename = os.path.join(
        insta485.app.config["UPLOAD_FOLDER"],
        hash_filename_basename
    )
    # Move temp file to permanent location
    shutil.move(temp_filename, hash_filename)
    return hash_filename


def logged_in():
    """Check if the current user is logged in."""
    return flask.session.get('username')
