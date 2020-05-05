"""REST API for posts."""
import flask
import insta485
from .auth import logged_in


@insta485.app.route('/api/v1/p/', methods=["GET"])
def get_posts():
    """Return the next ten posts."""
    if not logged_in():
        context9 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context9), 403)

    connection = insta485.model.get_db()
    size = flask.request.args.get('size', 10, type=int)
    page = flask.request.args.get('page', 0, type=int)
    if size < 0 or page < 0:
        context = {
            "message": "Bad Request",
            "status_code": 400
        }
        return (flask.jsonify(**context), 400)

    offset = page * size
    # grab newest posts, limit to 10
    posts = connection.execute(
        (
            "SELECT postid "
            "FROM posts "
            "WHERE owner "
            "IN "
            "(SELECT username2 FROM following WHERE username1 = '%s') "
            "OR owner = '%s' "
            "ORDER BY postid desc "
            "LIMIT '%d' "
            "OFFSET '%d'"
        )
        % (flask.session['username'], flask.session['username'], size, offset)
    )
    posts = posts.fetchall()

    count = connection.execute(
        (
            "SELECT COUNT(*) AS count "
            "FROM posts "
            "WHERE owner "
            "IN "
            "(SELECT username2 FROM following WHERE username1 = '%s') "
            "OR owner = '%s' "
        )
        % (flask.session['username'], flask.session['username'])
    )
    count = count.fetchall()
    # append url to dict
    for post in posts:
        post.update({"url": flask.request.path + str(post['postid']) + "/"})
    context = {
        "results": posts,
        "url": flask.request.path,
    }
    if count[0]['count'] <= offset + size:
        context['next'] = ""
    else:
        next_page = page + 1
        context['next'] = (flask.request.path + "?size="
                           + str(size) + "&page=" + str(next_page))
    return flask.jsonify(**context)


@insta485.app.route('/api/v1/p/<int:postid_url_slug>/', methods=["GET"])
def get_post(postid_url_slug):
    """Return the postid."""
    if not logged_in():
        context5 = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context5), 403)
    connection = insta485.model.get_db()
    post_data1 = connection.execute(
        (
            "SELECT * "
            "from posts "
        )
    )
    post_data1 = post_data1.fetchall()
    # if postid_url_slug > len(post_data1):
    #     context = {
    #         "message": "Not found",
    #         "status_code": 404
    #     }
    #     return (flask.jsonify(**context), 404)

    post_data = connection.execute(
        (
            "SELECT * "
            "FROM posts WHERE"
            " postid = '%s'"
        )
        % (postid_url_slug))
    post_data = post_data.fetchall()

    user_info = connection.execute(
        "SELECT filename FROM users "
        "WHERE username = '%s'"
        % post_data[0]['owner']
        )
    user_info = user_info.fetchall()
    context = {
        # "age": "",
        # "img_url": "",
        # "owner": "",
        # "owner_img_url": "",
        # "owner_show_url": "",
        # "post_show_url": "",
        "url": flask.request.path,
    }
    context['age'] = post_data[0]['created']
    context['img_url'] = "/uploads/" + post_data[0]['filename']
    context['owner'] = post_data[0]['owner']
    context['owner_img_url'] = "/uploads/" + user_info[0]['filename']
    context['owner_show_url'] = "/u/" + post_data[0]['owner'] + "/"
    context['post_show_url'] = "/p/" + str(postid_url_slug) + "/"
    return flask.jsonify(**context)
