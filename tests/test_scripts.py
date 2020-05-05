"""
Test student-created utility scripts.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import sqlite3
import sh


def test_executables():
    """Verify insta485run, insta485test, insta485db are executables."""
    assert_is_shell_script("bin/insta485run")
    assert_is_shell_script("bin/insta485test")
    assert_is_shell_script("bin/insta485db")
    assert_is_shell_script("bin/insta485install")


def test_insta485install():
    """Verify insta485test contains the right commands."""
    with open("bin/insta485install") as file:
        insta485test_content = file.read()
    assert "python3 -m venv" in insta485test_content
    assert "source env/bin/activate" in insta485test_content
    assert "pip install nodeenv" in insta485test_content
    assert "nodeenv --python-virtualenv" in insta485test_content
    assert "chromedriver" in insta485test_content
    assert "pip install -e ." in insta485test_content
    assert "npm install ." in insta485test_content


def test_insta485db_random():
    """Verify insta485db reset does a destroy and a create."""
    # Run "insta485db reset && insta485db random"
    insta485db = sh.Command("bin/insta485db")
    insta485db("reset")
    insta485db("random")

    # Connect to the database
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")

    # Get the number of posts from the database
    cur = connection.execute("SELECT count(*) FROM posts")
    num_rows = cur.fetchone()[0]
    assert num_rows > 100


def assert_is_shell_script(path):
    """Assert path is an executable shell script."""
    assert os.path.isfile(path)
    output = sh.file(path)  # run "file" command line utility
    assert "shell script" in output
    assert "executable" in output
