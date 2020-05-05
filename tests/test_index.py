"""Unit tests for the index page when user is logged in.

Run with logs visible:
$ pytest -v --log-cli-level=INFO ../autograder/test_index.py
"""
import os
from urllib.parse import urlparse, urljoin
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import bs4
import sh
import utils


def test_anything(driver):
    """Verify server returns anything at all.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    driver.get(driver.live_server.url())
    assert driver.find_elements_by_xpath(".//*")
    utils.assert_no_browser_console_errors(driver)


def test_login(driver):
    """Verify user awdeorio can log in.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    # Load login page
    login_url = urljoin(driver.live_server.url(), "/accounts/login")
    driver.get(login_url)
    assert driver.find_elements_by_xpath(".//*")
    utils.assert_no_browser_console_errors(driver)

    # Log in
    assert driver.find_elements_by_name("username")
    assert driver.find_elements_by_name("password")
    username_field = driver.find_element_by_name("username")
    password_field = driver.find_element_by_name("password")
    username_field.send_keys("awdeorio")
    password_field.send_keys("password")
    submit_buttons = driver.find_elements_by_xpath(
        "//input[@type='submit' and @value='login']"
    )
    assert len(submit_buttons) == 1
    submit_button = submit_buttons[0]
    submit_button.click()

    # After logging in, we should be redirected to the "/" URL
    assert urlparse(driver.current_url).path == "/"

    # The "/" page should contain a React entry point called 'reactEntry'
    assert driver.find_elements_by_id("reactEntry")
    utils.assert_no_browser_console_errors(driver)

    react_entry = driver.find_element_by_id("reactEntry")
    assert react_entry.find_elements_by_xpath(".//*"), \
        "Failed to find an element rendered by ReactJS"


def test_feed_load(driver):
    """Verify feed loads on index page.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_login(driver)

    # Verify react is being used
    assert driver.find_elements_by_tag_name("script")
    script_element = driver.find_element_by_tag_name("script")
    assert "/static/js/bundle.js" in script_element.get_attribute("src")
    assert script_element.get_attribute("type") == 'text/javascript'

    # Verify links
    assert driver.find_elements_by_xpath("//a[@href='/p/1/']")
    assert driver.find_elements_by_xpath("//a[@href='/p/2/']")
    assert driver.find_elements_by_xpath("//a[@href='/p/3/']")
    assert driver.find_elements_by_xpath("//a[@href='/u/awdeorio/']")
    assert driver.find_elements_by_xpath("//a[@href='/u/jflinn/']")
    assert driver.find_elements_by_xpath("//a[@href='/u/michjc/']")

    # Verify images
    assert driver.find_elements_by_xpath(  # Flinn
        "//img[@src='/uploads/505083b8b56c97429a728b68f31b0b2a089e5113.jpg']"
    )
    assert driver.find_elements_by_xpath(  # DeOrio
        "//img[@src='/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg']"
    )
    assert driver.find_elements_by_xpath(  # Postid 1
        "//img[@src='/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg']"
    )
    assert driver.find_elements_by_xpath(  # Postid 2
        "//img[@src='/uploads/ad7790405c539894d25ab8dcf0b79eed3341e109.jpg']"
    )
    assert driver.find_elements_by_xpath(
        "//img[@src='/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg']"
    )

    # Verify text
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '#chickensofinstagram']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'I <3 chickens']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'Cute overload!']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = 'Sick #crossword']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '"
        "Walking the plank #chickensofinstagram"
        "']"
    )
    assert driver.find_elements_by_xpath(
        "//*[normalize-space(text()) = '"
        "This was after trying to teach them to do a #crossword"
        "']"
    )

    # Verify REST API requests.  A parallel process is writing the log, so we
    # need to wait for it to finish writing.
    flask_log = utils.wait_for_read("flask.log", nlines=10)
    assert "GET /api/v1/p/" in flask_log
    assert "GET /api/v1/p/1/" in flask_log
    assert "GET /api/v1/p/1/likes/" in flask_log
    assert "GET /api/v1/p/1/comments/" in flask_log
    assert "GET /api/v1/p/2/" in flask_log
    assert "GET /api/v1/p/2/likes/" in flask_log
    assert "GET /api/v1/p/2/comments/" in flask_log
    assert "GET /api/v1/p/3/" in flask_log
    assert "GET /api/v1/p/3/likes/" in flask_log
    assert "GET /api/v1/p/3/comments/" in flask_log
    assert "GET /api/v1/p/4/" not in flask_log


def test_new_comment(driver):
    """Verify new comment appears without refresh.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(driver)

    # Clear the Flask request log
    with open("flask.log", "w") as infile:
        infile.write("")

    # Find comment field on for postid 3, which is the first one on the page
    comment_fields = driver.find_elements_by_xpath(
        "//form[contains(@class, 'comment-form')]//input[@type='text']"
    )
    assert comment_fields
    comment_field = comment_fields[0]

    # Type into comment field and submit by typing "enter"
    comment_field.send_keys("test comment")
    comment_field.send_keys(Keys.RETURN)

    # Verify new comment exists
    assert driver.find_elements_by_xpath(
        "//*[text()[contains(.,'test comment')]]"
    )
    utils.assert_no_browser_console_errors(driver)

    # Verify REST API POST request from new comment is the *only* new request.
    # A parallel process is writing the log, so we need to wait for it to
    # finish writing.
    flask_log = utils.wait_for_read("flask.log", nlines=1)
    assert flask_log.count('\n') == 1, flask_log
    assert "POST /api/v1/p/3/comments/" in flask_log


def test_like_unlike(driver):
    """Verify like/unlike button behavior without refresh.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(driver)

    # Clear the Flask request log
    with open("flask.log", "w") as infile:
        infile.write("")

    # Click the first like button
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3
    like_button = like_buttons[0]
    like_button.click()

    # First post started with 1 like by awdeorio, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '0 likes']")
    utils.assert_no_browser_console_errors(driver)

    # Click the first like button again
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3
    like_button = like_buttons[0]
    like_button.click()

    # First post should now have 1 like
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")
    utils.assert_no_browser_console_errors(driver)

    # Verify REST API requests from like and unlike are the *only* new
    # requests.  A parallel process is writing the log, so we need to wait for
    # it to finish writing.
    flask_log = utils.wait_for_read("flask.log", nlines=2)
    assert flask_log.count('\n') == 2, flask_log
    assert "DELETE /api/v1/p/3/likes/" in flask_log
    assert "POST /api/v1/p/3/likes/" in flask_log


def test_double_click_like(driver):
    """
    Verify double clicking on an unliked image likes the image.

    Load main page, unlike first image, perform two double clicks on it,
    the first of which should like the image, the second should have no effect.
    """
    test_feed_load(driver)

    # Clear the Flask request log
    with open("flask.log", "w") as outfile:
        outfile.write("")

    # Check that the like buttons exist
    like_buttons = driver.find_elements_by_xpath(
        "//button[contains(@class, 'like-unlike-button')]"
    )
    assert len(like_buttons) == 3

    # Click the like button for the first image
    # This will unlike the image which is already liked
    like_button = like_buttons[0]
    like_button.click()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '0 likes']")

    # Verify first image exists
    images = driver.find_elements_by_xpath(
        "//img[@src='/uploads/9887e06812ef434d291e4936417d125cd594b38a.jpg']"
    )
    # assert that exactly one copy of the image exists on the page
    assert images
    assert len(images) == 1

    jflinn_post_image = images[0]

    # Perform double click on the first image
    # this should like the image again
    action_chains = ActionChains(driver)
    action_chains.double_click(jflinn_post_image).perform()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")

    # Perform another double click, this shouldn't do anything
    # because the image is already liked
    action_chains.double_click(jflinn_post_image).perform()

    # First post started with 1 like, now it should be 0
    assert driver.find_elements_by_xpath("//*[normalize-space() = '1 like']")

    # Verify REST API requests from like and unlike are the *only* new
    # requests.  A parallel process is writing the log, so we need to wait for
    # it to finish writing.
    flask_log = utils.wait_for_read("flask.log", nlines=2)
    assert flask_log.count('\n') == 2, flask_log
    assert "DELETE /api/v1/p/3/likes/" in flask_log
    assert "POST /api/v1/p/3/likes/" in flask_log


def test_refresh(driver):
    """Verify refresh with content from another client.

    Load main page, create new post via another client, refresh the page,
    make sure both old posts and new post appear.

    Note: 'driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  It is implemented in
    conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_feed_load(driver)

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

    # Clear Flask request log
    with open("flask.log", "w") as infile:
        infile.write("")

    # Refresh
    driver.refresh()

    # Verify posts on page: 1,2,3 are old, 5 is new
    assert driver.find_elements_by_xpath("//a[@href='/p/1/']")
    assert driver.find_elements_by_xpath("//a[@href='/p/2/']")
    assert driver.find_elements_by_xpath("//a[@href='/p/3/']")
    assert driver.find_elements_by_xpath("//a[@href='/p/5/']")

    utils.assert_no_browser_console_errors(driver)

    # Verify REST API requests.  A parallel process is writing the log, so we
    # need to wait for it to finish writing.
    flask_log = utils.wait_for_read("flask.log", nlines=2)
    assert "GET /api/v1/p/1/" in flask_log
    assert "GET /api/v1/p/2/" in flask_log
    assert "GET /api/v1/p/3/" in flask_log
    assert "GET /api/v1/p/4/" not in flask_log
    assert "GET /api/v1/p/5/" in flask_log


def test_html(driver):
    """Verify HTML5 compliance in HTML portion of the index page."""
    test_feed_load(driver)

    # Clean up
    if os.path.exists("tmp/index.html"):
        os.remove("tmp/index.html")
    os.makedirs("tmp", exist_ok=True)

    # Prettify the HTML for easier debugging
    html = "<!DOCTYPE html>" + driver.page_source  # Selenium strips DOCTYPE
    soup = bs4.BeautifulSoup(html, "html.parser")
    html = soup.prettify()

    # Write HTML of current page source to file
    with open("tmp/index.html", "w") as outfile:
        outfile.write(html)

    # Run html5validator on the saved file
    html5validator = sh.Command("html5validator")
    print(html5validator("--version").strip())
    print("html5validator tmp/index.html")
    html5validator("--ignore=JAVA_TOOL_OPTIONS", "tmp/index.html")
