"""Shared test fixtures.

Pytest will automatically run the setup_teardown_selenium_driver() function
before a test.  A test should use "driver" as an input, because the name of the
fixture is "driver".

EXAMPLE:
>>> def test_anything(driver):
>>>     driver.get(driver.live_server.url())
>>>     assert driver.find_elements_by_xpath(".//*")

Pytest fixture docs:
https://docs.pytest.org/en/latest/fixture.html#conftest-py-sharing-fixture-functions

pytest-flask: a Python plugin for the pytest that provides a live server test
fixture.  In other words, a function that starts your flask app in a separate
process.

Google Chrome: a web browser that supports headless browsing.

Selenium: a Python library for controlling a headless web browser.

Chromedriver: middle man executable between Selenium and Chrome.

"""
import os
import glob
import time
import logging
import pytest
import sh
import flask
import selenium
import selenium.webdriver
import insta485

# Set up logging
LOGGER = logging.getLogger("autograder")

# An implicit wait tells WebDriver to poll the DOM for a certain amount of
# time when trying to find any element (or elements) not immediately
# available. Once set, the implicit wait is set for the life of the
# WebDriver object.
#
# We'll need longer wait times on slow machines like the autograder.
#
# https://selenium-python.readthedocs.io/waits.html#implicit-waits
if "TRAVIS" in os.environ:
    IMPLICIT_WAIT_TIME = 10
elif os.path.isdir("/home/autograder/working_dir"):
    IMPLICIT_WAIT_TIME = 30
else:
    IMPLICIT_WAIT_TIME = 10

# Implicit wait time when using a slow server
IMPLICIT_WAIT_TIME_SLOW_SERVER = 2 * IMPLICIT_WAIT_TIME

# Delay for intentionally slow REST API responses
SLOW_RESPONSE_DELAY = 0.5


@pytest.fixture(name='app')
def setup_teardown_flask_app():
    """Configure a Flask app object to be used as a live server.

    This fixture is called by pytest-flask's live_server fixture, which starts
    the Flask app in a separate process.  We need a separate process so that
    a headless Chrome browser can run in yet another process and load a page
    from the server process.

    Docs:
    https://pypi.org/project/pytest-flask/#quick-start
    https://issue.life/questions/54450601
    https://stackoverrun.com/fr/q/9938631
    """
    LOGGER.info("Setup test fixture 'app'")

    # Sanity check JavaScript distribution bundle
    assert os.path.isfile("insta485/static/js/bundle.js"), \
        "Can't find bundle.js.  Did you forget to run webpack?"
    jsx_mtimes = [os.path.getmtime(x) for x in glob.glob("insta485/js/*.jsx")]
    bundle_mtime = os.path.getmtime("insta485/static/js/bundle.js")
    assert bundle_mtime > max(jsx_mtimes), \
        "Looks like bundle.js is out of date.  Try running webpack again."

    # Reset the database
    insta485db = sh.Command("bin/insta485db")
    insta485db("reset")

    # Log requests to file. Later, we'll read the log to verify REST API
    # requests made by the client front end show up at the server backend.  We
    # need to log to a file, not an in-memory object because our live server
    # which creates this log will be run in a separate process.
    if os.path.exists("flask.log"):
        os.remove("flask.log")
    werkzeug_logger = logging.getLogger("werkzeug")
    assert not werkzeug_logger.handlers, "Unexpected handler already attached"
    werkzeug_logger.setLevel("INFO")
    werkzeug_logger.addHandler(logging.FileHandler("flask.log"))

    # Configure Flask app.  Testing mode so that exceptions are propagated
    # rather than handled by the the app's error handlers.
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield insta485.app

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'app'")
    werkzeug_logger.handlers.clear()
    os.remove("flask.log")


@pytest.fixture(name='base_driver')
def setup_teardown_selenium_base_driver(live_server):
    """Configure Selenium library to connect to a headless Chrome browser.

    The live-server pytest fixture is provided by pytest-flask.  This fixture
    is really a function that starts a live Flask test server in a separate
    process.

    Note that this test fixture doesn't start the live_server.  You'll have to
    do that manually with driver.live_server.start() either in each test, or in
    a fixture that uses this fixture as a dependency.
    """
    LOGGER.info("Setup test fixture 'base_driver'")

    # Configure Selenium
    #
    # Pro-tip: remove the "headless" option and set a breakpoint.  A Chrome
    # browser window will open, and you can play with it using the developer
    # console.
    #
    # We use the "capabilities" object to access the Chrome logs, which is
    # similar to what you'd see in the developer console.   Later, we'll use
    # the logs to check for JavaScript exceptions.
    # Docs: https://stackoverflow.com/questions/44991009/
    options = selenium.webdriver.chrome.options.Options()
    options.add_argument("--headless")  # Don't open a browser GUI window
    options.add_argument("--no-sandbox")  # Required by Docker
    capabilities = selenium.webdriver.common.desired_capabilities.\
        DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'browser': 'SEVERE'}

    driver = selenium.webdriver.Chrome(
        options=options,
        desired_capabilities=capabilities,
    )

    # An implicit wait tells WebDriver to poll the DOM for a certain amount of
    # time when trying to find any element (or elements) not immediately
    # available. Once set, the implicit wait is set for the life of the
    # WebDriver object.
    #
    # https://selenium-python.readthedocs.io/waits.html#implicit-waits
    driver.implicitly_wait(IMPLICIT_WAIT_TIME)
    LOGGER.info("IMPLICIT_WAIT_TIME=%s", IMPLICIT_WAIT_TIME)

    # Pass live_server object to test that uses this fixture.  The live server
    # port is automatically generated, so we don't know the url until run time.
    # Later, tests that use this fixture can call driver.live_server.url() to
    # get the host and port.
    driver.live_server = live_server

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'base_driver'")

    # Verify no errors in the browser console, e.g., JavaScript exceptions or
    # failed page loads
    console_log = driver.get_log("browser")
    console_log_empty = not console_log
    console_log_str = "\n".join(x["message"] for x in console_log)
    assert console_log_empty,\
        "Error in browser console:\n{}".format(console_log_str)

    # Clean up the browser processes started by Selenium
    driver.quit()


@pytest.fixture(name='driver')
def setup_teardown_selenium_driver(base_driver):
    """Selenium driver with started live server."""
    LOGGER.info("Setup test fixture 'driver'")
    driver = base_driver

    # Start live server
    # pylint: disable=protected-access
    assert not driver.live_server._process
    driver.live_server.start()

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield driver

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'driver'")


@pytest.fixture(name='slow_driver')
def setup_teardown_selenium_slow_driver(base_driver):
    """Selenium driver with started live server and slow REST API."""
    LOGGER.info("Setup test fixture 'slow_driver'")
    slow_driver = base_driver

    def delay_request():
        """Delay Flask response to a request."""
        if "/api/v1/" not in flask.request.path:
            return
        LOGGER.info(
            'Delaying response %ss to request "%s %s"',
            SLOW_RESPONSE_DELAY, flask.request.method, flask.request.path,
        )
        time.sleep(SLOW_RESPONSE_DELAY)

    # Register delay as a callback to be executed before each request.  This
    # function should be the only callback.
    assert not slow_driver.live_server.app.before_request_funcs
    slow_driver.live_server.app.before_request(delay_request)

    # Increase the implicit wait time
    slow_driver.implicitly_wait(IMPLICIT_WAIT_TIME_SLOW_SERVER)
    LOGGER.info(
        "IMPLICIT_WAIT_TIME_SLOW_SERVER=%s ",
        IMPLICIT_WAIT_TIME_SLOW_SERVER,
    )

    # Start live server *after* registering callback
    # pylint: disable=protected-access
    assert not slow_driver.live_server._process
    slow_driver.live_server.start()

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    yield slow_driver

    # Teardown code starts here.  Unregister callback.
    LOGGER.info("Teardown test fixture 'slow_driver'")
    slow_driver.live_server.app.before_request_funcs.clear()


@pytest.fixture(name="client")
def client_setup_teardown():
    """
    Start a Flask test server with a clean database.

    This fixture is used to test the REST API, it won't start a live server.

    Flask docs: https://flask.palletsprojects.com/en/1.1.x/testing/#testing
    """
    LOGGER.info("Setup test fixture 'client'")

    # Reset the database
    insta485db = sh.Command("bin/insta485db")
    insta485db("reset")

    # Configure Flask test server
    insta485.app.config["TESTING"] = True

    # Transfer control to test.  The code before the "yield" statement is setup
    # code, which is executed before the test.  Code after the "yield" is
    # teardown code, which is executed at the end of the test.  Teardown code
    # is executed whether the test passed or failed.
    with insta485.app.test_client() as client:
        yield client

    # Teardown code starts here
    LOGGER.info("Teardown test fixture 'client'")
