import os
import subprocess
from importlib import metadata
from pathlib import Path
from shutil import rmtree
from textwrap import dedent

import pytest

import lektor_fixedlang


LEKTOR_ROOT = Path("/dev/shm/lektor-fixedlang")
LEKTOR_HOME_SRC = LEKTOR_ROOT / "content" / "contents.lr"
LEKTOR_HOME_DST = LEKTOR_ROOT / "_build" / "index.html"
CONFIG_FILE = LEKTOR_ROOT / "configs" / "fixedlang.ini"


@pytest.fixture(autouse=True)
def lektor_init():
    rmtree(LEKTOR_ROOT, ignore_errors=True)
    LEKTOR_HOME_SRC.parent.mkdir(parents=True, exist_ok=True)
    LEKTOR_HOME_DST.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    project_file = LEKTOR_ROOT / "project.lektorproject"
    project_file.parent.mkdir(parents=True, exist_ok=True)
    project_file.write_text(dedent("""
        [project]
        name = Project
        output_path = _build

        [alternatives.en]
        locale = en_US
        primary = yes

        [alternatives.tr]
        locale = tr_TR
        url_prefix = /tr/
    """))

    model_file = LEKTOR_ROOT / "models" / "page.ini"
    model_file.parent.mkdir(parents=True, exist_ok=True)
    model_file.write_text(dedent("""
        [model]
        name = Page
        label = {{ this.title }}

        [fields.title]
        label = Title
        type = string

        [fields.body]
        label = Body
        type = html
    """))

    template_file = LEKTOR_ROOT / "templates" / "page.html"
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text("""{{ this.body }}\n""")

    current_dir = os.getcwd()
    os.chdir(LEKTOR_ROOT)
    yield

    os.chdir(current_dir)
    rmtree(LEKTOR_ROOT)


def test_installed_version_should_match_tested_version():
    assert metadata.version("lektor_fixedlang") == lektor_fixedlang.__version__


@pytest.mark.parametrize(("config", "content", "output"), [
    (
        """[span]\nWikipedia = en\n""",
        """title: Test\n---\nbody: <p>..Wikipedia...</p>\n""",
        """<p>..<span lang="en">Wikipedia</span>...</p>\n""",
    ),
])
def test_matched_pattern_should_be_wrapped_in_given_tag(config, content, output):
    CONFIG_FILE.write_text(config)
    LEKTOR_HOME_SRC.write_text(content)
    subprocess.run(["lektor", "build"])
    generated = LEKTOR_HOME_DST.read_text()
    assert generated == output


@pytest.mark.parametrize(("config", "content", "output"), [
    (
        """[span]\nWikipedia = en\n""",
        """title: Test\n---\nbody: <p lang="en">..Wikipedia...</p>\n""",
        """<p lang="en">..Wikipedia...</p>\n""",
    ),
    (
        """[span]\nWikipedia = en\n""",
        """title: Test\n---\nbody: <div lang="en">..<p>Wikipedia</p>...</div>\n""",
        """<div lang="en">..<p>Wikipedia</p>...</div>\n""",
    ),
    (
        """[span]\nWikipedia = en\n""",
        """title: Test\n---\nbody: <div lang="en"><p lang="tr">..Wikipedia...</p></div>\n""",
        """<div lang="en"><p lang="tr">..<span lang="en">Wikipedia</span>...</p></div>\n""",
    ),
])
def test_matched_pattern_should_consider_inherited_language(config, content, output):
    CONFIG_FILE.write_text(config)
    LEKTOR_HOME_SRC.write_text(content)
    subprocess.run(["lektor", "build"])
    generated = LEKTOR_HOME_DST.read_text()
    assert generated == output
