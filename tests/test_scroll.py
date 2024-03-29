"""Unit tests for infinite scroll on index page."""
import os
import sqlite3
from urllib.parse import urljoin

import requests

import utils
import test_index


def test_infinite_scroll(driver):
    """Test infinite scroll."""
    # Delete all likes, comments and posts
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 11 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    login_url = urljoin(driver.live_server.url(), "/accounts/login")
    session = requests.Session()
    response = session.get(driver.live_server.url())
    assert response.status_code == 200
    response = session.post(
        login_url,
        data={"username": "awdeorio", "password": "password"}
    )
    assert response.status_code == 200
    pic_filename = os.path.join(utils.TEST_DIR, "testdata/fox.jpg")
    for _ in range(11):
        with open(pic_filename, "rb") as pic:
            post_url = urljoin(driver.live_server.url(), "/u/awdeorio/")
            response = session.post(
                post_url,
                files={"file": pic},
                data={"create_post": "upload new post"}
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(driver)

    # Verify 10 most recent posts are on the page (postids 2-11 inclusive)
    for post_id in range(2, 11 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify there are 11 posts now
    assert driver.find_elements_by_xpath("//a[@href='/p/1/']")


def test_infinite_scroll_many(driver):
    """Test many infinite scrolls."""
    # Delete all likes, comments and posts
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 30 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    login_url = urljoin(driver.live_server.url(), "/accounts/login")
    session = requests.Session()
    response = session.get(driver.live_server.url())
    assert response.status_code == 200
    response = session.post(
        login_url,
        data={"username": "awdeorio", "password": "password"}
    )
    assert response.status_code == 200
    pic_filename = os.path.join(utils.TEST_DIR, "testdata/fox.jpg")
    for _ in range(30):
        with open(pic_filename, "rb") as pic:
            post_url = urljoin(driver.live_server.url(), "/u/awdeorio/")
            response = session.post(
                post_url,
                files={"file": pic},
                data={"create_post": "upload new post"}
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(driver)

    # Verify 10 newest posts are included.  Note: a side effect of this code is
    # to tell Selenium to wait until all 10 posts have been loaded.  Our
    # subsequent check for the number of posts depends on all 10 being loaded.
    for post_id in range(21, 30 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/p/')]")
    assert len(posts) == 10

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify 20 posts
    for post_id in range(11, 30 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/p/')]")
    assert len(posts) == 20

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify 30 posts
    for post_id in range(1, 30 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )
    posts = driver.find_elements_by_xpath("//a[contains(@href, '/p/')]")
    assert len(posts) == 30

    # Scroll to the bottom of the page a couple times, no errors
    utils.scroll_to_bottom_of_page(driver)
    utils.scroll_to_bottom_of_page(driver)
    utils.scroll_to_bottom_of_page(driver)


def test_scroll_refresh(driver):
    """Test infinite scroll with refresh afterward.

    Go to main page, scroll to trigger infinite scroll, make a post from
    background, refresh the page, make sure only 10 posts appear including
    the previously made, new post.
    """
    # Delete all likes, comments and posts
    connection = sqlite3.connect("var/insta485.sqlite3")
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("DELETE FROM likes")
    connection.execute("DELETE FROM comments")
    connection.execute("DELETE FROM posts")
    connection.commit()
    connection.close()

    # Create exactly 11 posts with "fox.jpg".  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    login_url = urljoin(driver.live_server.url(), "/accounts/login")
    session = requests.Session()
    response = session.get(driver.live_server.url())
    assert response.status_code == 200
    response = session.post(
        login_url,
        data={"username": "awdeorio", "password": "password"}
    )
    assert response.status_code == 200
    pic_filename = os.path.join(utils.TEST_DIR, "testdata/fox.jpg")
    for _ in range(11):
        with open(pic_filename, "rb") as pic:
            post_url = urljoin(driver.live_server.url(), "/u/awdeorio/")
            response = session.post(
                post_url,
                files={"file": pic},
                data={"create_post": "upload new post"}
            )
        assert response.status_code == 200

    # Log in by reusing test from test_index
    test_index.test_login(driver)

    # Verify 10 most recent posts are on the page (postids 2-11 inclusive)
    for post_id in range(2, 11 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )

    # Scroll to the bottom of the page
    utils.scroll_to_bottom_of_page(driver)

    # Verify there are 11 posts now
    assert driver.find_elements_by_xpath("//a[@href='/p/1/']")

    # Log in as jflinn and create a new post.  We're making requests directly
    # to the server-side dynamic pages server here, not using Selenium.
    login_url = urljoin(driver.live_server.url(), "/accounts/login")
    session = requests.Session()
    response = session.get(driver.live_server.url())
    assert response.status_code == 200
    response = session.post(
        login_url,
        data={"username": "jflinn", "password": "password"}
    )
    assert response.status_code == 200
    pic_filename = os.path.join(utils.TEST_DIR, "testdata/fox.jpg")
    with open(pic_filename, "rb") as pic:
        post_url = urljoin(driver.live_server.url(), "/u/jflinn/")
        response = session.post(
            post_url,
            files={"file": pic},
            data={"create_post": "upload new post"}
        )
        assert response.status_code == 200

    # awdeorio refreshes the page
    driver.refresh()
    utils.assert_no_browser_console_errors(driver)

    # Verify 10 most recent posts are on the page
    for post_id in range(3, 12 + 1):
        assert driver.find_elements_by_xpath(
            "//a[@href='/p/{}/']".format(post_id)
        )
