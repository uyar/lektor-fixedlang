import os
import subprocess
from importlib import metadata
from pathlib import Path
from shutil import copytree, rmtree

from pytest import fixture

import lektor_fixedlang


LEKTOR_SRC_ROOT = Path(__file__).parent / "project"
LEKTOR_ROOT = Path("/dev/shm/lektor-fixedlang")
LEKTOR_CONTENT_ROOT = LEKTOR_ROOT / "content"
LEKTOR_BUILD_ROOT = LEKTOR_ROOT / "_build"
LEKTOR_CONTENT_INDEX = LEKTOR_CONTENT_ROOT / "contents.lr"
LEKTOR_BUILD_INDEX = LEKTOR_BUILD_ROOT / "index.html"
LEKTOR_CONFIG_DIR = LEKTOR_ROOT / "configs"
FIXEDLANG_CONFIG_FILE = LEKTOR_CONFIG_DIR / "fixedlang.ini"


@fixture(autouse=True)
def lektor_init():
    rmtree(LEKTOR_ROOT, ignore_errors=True)
    copytree(LEKTOR_SRC_ROOT, LEKTOR_ROOT)

    LEKTOR_CONFIG_DIR.mkdir()

    current_dir = os.getcwd()
    os.chdir(LEKTOR_ROOT)
    yield

    os.chdir(current_dir)
    rmtree(LEKTOR_ROOT)


def test_installed_version_should_match_tested_version():
    assert metadata.version("lektor_fixedlang") == lektor_fixedlang.__version__


def test_matched_pattern_should_be_wrapped_in_given_tag():
    config = "[span]\nJive = en\n"
    FIXEDLANG_CONFIG_FILE.write_text(config)
    content = "title: Test\n---\nbody: Jive\n"
    LEKTOR_CONTENT_INDEX.write_text(content)
    subprocess.run(["lektor", "build"])
    assert '<span lang="en">Jive</span>' in LEKTOR_BUILD_INDEX.read_text()


def test_matching_should_be_case_sensitive():
    config = "[span]\nJive = en\n"
    FIXEDLANG_CONFIG_FILE.write_text(config)
    content = "title: Test\n---\nbody: jive\n"
    LEKTOR_CONTENT_INDEX.write_text(content)
    subprocess.run(["lektor", "build"])
    assert '<span lang="en">' not in LEKTOR_BUILD_INDEX.read_text()
