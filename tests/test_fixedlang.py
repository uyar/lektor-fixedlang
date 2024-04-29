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
        type = markdown
    """))

    template_file = LEKTOR_ROOT / "templates" / "page.html"
    template_file.parent.mkdir(parents=True, exist_ok=True)
    template_file.write_text(dedent("""
        <html>
        <head>
          <meta charset="utf-8">
          <title>{{ this.title }}</title>
        </head>
        <body>
          {{ this.body }}
        </body>
        </html>
    """))

    current_dir = os.getcwd()
    os.chdir(LEKTOR_ROOT)
    yield

    os.chdir(current_dir)
    rmtree(LEKTOR_ROOT)


def test_installed_version_should_match_tested_version():
    assert metadata.version("lektor_fixedlang") == lektor_fixedlang.__version__


@pytest.mark.parametrize(("config", "content", "output"), [
    (
        """[span]\nJive = en\n""",
        """title: Test\n---\nbody: Jive\n""",
        """<span lang="en">Jive</span>""",
    ),
])
def test_matched_pattern_should_be_wrapped_in_given_tag(config, content, output):
    CONFIG_FILE.write_text(config)
    LEKTOR_HOME_SRC.write_text(content)
    subprocess.run(["lektor", "build"])
    generated = LEKTOR_HOME_DST.read_text()
    assert output in generated


@pytest.mark.parametrize(("config", "content", "output"), [
    (
        """[span]\nJive = en\n""",
        """title: Test\n---\nbody: jive\n""",
        """<span lang="en">""",
    ),
])
def test_matching_should_be_case_sensitive(config, content, output):
    CONFIG_FILE.write_text(config)
    LEKTOR_HOME_SRC.write_text(content)
    subprocess.run(["lektor", "build"])
    generated = LEKTOR_HOME_DST.read_text()
    assert output not in generated
