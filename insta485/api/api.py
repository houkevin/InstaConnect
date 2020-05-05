"""REST API for Insta485."""
import flask
import insta485
from .auth import logged_in


@insta485.app.route('/api/v1/', methods=["GET"])
def api():
    """Return a list of available services."""
    # spec: https://eecs485staff.github.io/p3-insta485-clientside/#get-apiv1
    if not logged_in():
        context = {
            "message": "Forbidden",
            "status_code": 403,
        }
        return (flask.jsonify(**context), 403)
    context = {
        "posts": flask.request.path + "p/",
        "url": flask.request.path,
    }
    return flask.jsonify(**context)
