"""
Check Python style with pycodestyle, pydocstyle and pylint.

EECS 485 Project 3

Andrew DeOrio <awdeorio@umich.edu>
"""
import os
import sh
import utils


def test_pycodestyle():
    """Run pycodestyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    pycodestyle = sh.Command("pycodestyle")
    print("\n", pycodestyle, pycodestyle("--version").strip())
    pycodestyle("setup.py", "insta485")


def test_pydocstyle():
    """Run pydocstyle."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    pydocstyle = sh.Command("pydocstyle")
    print("\n", pydocstyle, pydocstyle("--version").strip())
    pydocstyle("setup.py", "insta485")


def test_pylint():
    """Run pylint."""
    assert_no_prohibited_terms("nopep8", "noqa", "pylint")
    pylint = sh.Command("pylint")
    pylintrc_path = os.path.join(utils.TEST_DIR, "testdata/pylintrc")
    print("\n", pylint, pylint("--version").strip())
    pylint(
        "--rcfile", pylintrc_path,
        "--disable=cyclic-import",
        "setup.py",
        "insta485",
    )


def test_eslint():
    """Run eslint."""
    assert_no_prohibited_terms("eslint-disable", "jQuery", "XMLHttpRequest")
    eslint = sh.Command("npx").bake("eslint")
    eslintrc_path = os.path.join(utils.TEST_DIR, "testdata/eslintrc.js")
    print("\n", eslint, eslint("--version").strip())
    eslint(
        "--ext", "js,jsx",
        "--no-inline-config",
        "--no-eslintrc",
        "--config", eslintrc_path,
        "insta485/js/",
    )


def assert_no_prohibited_terms(*terms):
    """Check for prohibited terms before testing style."""
    for term in terms:
        grep = sh.Command("grep")
        try:
            output = grep(
                "-r",
                "-n",
                term,
                "--include=*.py",
                "--include=*.jsx",
                "--include=*.js",
                "--exclude=__init__.py",
                "--exclude=setup.py",
                "--exclude=bundle.js",
                "--exclude=*node_modules/*",
                "insta485",
            )
        except sh.ErrorReturnCode_1:
            # Did not find prohibited term, do nothing
            pass
        else:
            # Zero exit code indicates that grep found a prohibited term.
            assert output.exit_code != 0, (
                "The term '{term}' is prohibited.\n{message}"
                .format(term=term, message=str(output))
            )
