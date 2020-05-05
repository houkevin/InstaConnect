"""Verify a user is logged in."""
import flask


def logged_in():
    """Check if the current user is logged in."""
    return flask.session.get('username')
