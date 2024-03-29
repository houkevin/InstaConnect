"""Unit tests from test_index.py with a slow server."""
import json
import time
from urllib.parse import urljoin
import test_index
import conftest


def test_delay(slow_driver):
    """Verify server is slow.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_login(slow_driver)

    # Load a REST API route, recording the start time and stop time
    api_url = urljoin(slow_driver.live_server.url(), "/api/v1/")
    start_time = time.time()
    slow_driver.get(api_url)
    stop_time = time.time()

    # Verify REST API request was artificially delayed
    duration = stop_time - start_time
    assert duration >= conftest.SLOW_RESPONSE_DELAY

    # Verify JSON string parses.  The JSON data should be wrapped in an HTML
    # <pre> tag.  Extract the text enclosed by the <pre> tag, then parse.
    json_str = slow_driver.find_element_by_tag_name("pre").text
    _ = json.loads(json_str)


def test_login(slow_driver):
    """Run test from test_index.py with slow REST API server.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_login(slow_driver)


def test_feed_load(slow_driver):
    """Run test from test_index.py with slow REST API server.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_feed_load(slow_driver)


def test_new_comment(slow_driver):
    """Run test from test_index.py with slow REST API server.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_new_comment(slow_driver)


def test_like_unlike(slow_driver):
    """Run test from test_index.py with slow REST API server.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_like_unlike(slow_driver)


def test_refresh(slow_driver):
    """Run test from test_index.py with slow REST API server.

    Note: 'slow_driver' is a fixture fuction that provides access to a headless
    Chrome web browser and a live Flask test server.  The live Flask test
    server artificially delays the response to each request.  It is implemented
    in conftest.py and reused by many tests.  Docs:
    https://docs.pytest.org/en/latest/fixture.html
    """
    test_index.test_refresh(slow_driver)
