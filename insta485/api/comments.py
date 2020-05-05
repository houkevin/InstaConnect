"""REST API for comments."""
import flask
import insta485

from .auth import logged_in


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["GET"])
def get_comments(postid_url_slug):
    """Return the comments for the post with the id: postid_url_slug."""
    if not logged_in():
        context1 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context1), 403)
    connection = insta485.model.get_db()
    post_data = connection.execute(
        (
            "SELECT * "
            "FROM posts "
        )
    )
    post_data = post_data.fetchall()
    if postid_url_slug > len(post_data):
        context1 = {
            "message": "Not found",
            "status_code": 404
        }
        return (flask.jsonify(**context1), 404)
    comments = connection.execute(
        (
            "SELECT commentid, owner, postid, text "
            "FROM comments "
            "WHERE postid = '%s'"
        )
        % (postid_url_slug))

    comments = comments.fetchall()
    for comment in comments:
        comment['owner_show_url'] = '/u/' + comment['owner'] + '/'
    context = {
        "comments": comments,
        "url": flask.request.path,
    }
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/comments/',
                    methods=["POST"])
def post_comment(postid_url_slug):
    """Upload a comment to postid."""
    if not logged_in():
        context2 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context2), 403)
    connection = insta485.model.get_db()
    data = flask.request.get_json()
    text = data['text']
    connection.execute(
        (
            "insert into comments(owner, postid, text) "
            "values('%s','%s','%s')"
        )
        % (flask.session['username'], postid_url_slug, text)
    )
    commentid = connection.execute(
        (
            "SELECT last_insert_rowid()"
            "FROM comments"
        )
    )
    commentid = commentid.fetchall()
    context = {
        "commentid": commentid[0]['last_insert_rowid()'],
        "owner": flask.session['username'],
        "owner_show_url": '/u/' + flask.session['username'],
        "postid": postid_url_slug,
        "text": text
    }
    return (flask.jsonify(**context), 201)
