"""REST API for likes."""
import flask
import insta485

from .auth import logged_in


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["GET"])
def get_likes(postid_url_slug):
    """Return the number of likes on postid."""
    if not logged_in():
        context6 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context6), 403)

    connection = insta485.model.get_db()
    post_data2 = connection.execute(
        (
            "SELECT * FROM"
            " posts "
        )
    )
    post_data2 = post_data2.fetchall()
    if postid_url_slug > len(post_data2):
        context2 = {
            "message": "Not found",
            "status_code": 404
        }
        return (flask.jsonify(**context2), 404)
    numlikes = connection.execute(
        (
            "SELECT COUNT(*) AS numlikes "
            "FROM likes "
            "WHERE postid = '%s'"
        )
        % (postid_url_slug)
    )
    numlikes = numlikes.fetchall()[0]

    logname_likes = cur_user_likes(postid_url_slug, flask.session['username'])
    context = {
        "logname_likes_this": logname_likes,
        "likes_count": numlikes['numlikes'],
        "postid": postid_url_slug,
        "url": flask.request.path,
    }
    return flask.jsonify(**context)

@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["POST"])
def like_post(postid_url_slug):
    """Add 1 like to postid."""
    if not logged_in():
        context7 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context7), 403)
    authenticated = logged_in()
    if (authenticated and
            cur_user_likes(postid_url_slug, flask.session['username'])):
        context = {
            "logname": flask.session['username'],
            "message": "Conflict",
            "postid": postid_url_slug,
            "status_code": 409
        }
        return (flask.jsonify(**context), 409)
    if authenticated:
        connection = insta485.model.get_db()
        connection.execute(
            (
                "insert into likes(owner, postid) "
                "values('%s','%s')"
            )
            % (flask.session['username'], postid_url_slug)
        )
        context = {
            "logname": flask.session['username'],
            "postid": postid_url_slug,
        }

    return (flask.jsonify(**context), 201)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/likes/',
                    methods=["DELETE"])
def dislike_post(postid_url_slug):
    """Remove 1 like from postid."""
    if not logged_in():
        context8 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context8), 403)
    connection = insta485.model.get_db()
    connection.execute(
        (
            "DELETE FROM likes WHERE"
            " owner = '%s' and postid = '%s'"
        )
        % (flask.session['username'], postid_url_slug)
    )
    logname_likes = cur_user_likes(postid_url_slug, flask.session['username'])
    context = {
        "logname_likes_this": logname_likes
    }

    return (flask.jsonify(**context), 204)


def cur_user_likes(postid, username):
    """Get the current user likes."""
    connection = insta485.model.get_db()
    user_likes = connection.execute(
        (
            "SELECT * "
            "FROM likes "
            "WHERE postid = '%s' AND owner = '%s'"
        )
        % (postid, username)
    )
    user_likes = user_likes.fetchall()

    if len(user_likes) > 0:
        user_likes = 1
    else:
        user_likes = 0

    return user_likes
