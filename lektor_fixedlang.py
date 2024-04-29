# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-fixedlang is released under the BSD license.
# Read the included LICENSE.txt file for details.

__version__ = "0.3"

import re
from pathlib import Path

from bs4 import BeautifulSoup
from lektor.db import Page
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter


def inherited_lang(node):
    lang = None
    for parent in node.parents:
        lang = parent.attrs.get("lang")
        if lang is not None:
            break
    return lang


class FixedLangPlugin(Plugin):
    name = "fixedlang"
    description = "Set fixed language for specific patterns."

    def on_setup_env(self, **extra):
        config = self.get_config()
        self.patterns = []
        for tag in config.sections():
            for pattern, lang in config.section_as_dict(tag).items():
                self.patterns.append((re.compile(f'({pattern})'), lang, tag))
        self.processed = set()

    def on_before_build_all(self, builder, **extra):
        reporter.report_generic("Starting setting fixed languages")

    def on_after_build(self, builder, build_state, source, prog, **extra):
        if not isinstance(source, Page):
            return
        artifact = prog.primary_artifact
        if artifact is None:
            return
        filename = artifact.dst_filename
        if filename in self.processed:
            return
        dst_file = Path(filename)
        content = dst_file.read_text()
        modified = False
        soup = BeautifulSoup(content, "html.parser")
        for (compiled, lang, tag) in self.patterns:
            for node in soup.find_all(string=compiled):
                if lang == inherited_lang(node):
                    continue
                markup = compiled.sub(
                    f'<{tag} lang="{lang}">\\1</{tag}>',
                    node.string,
                )
                subsoup = BeautifulSoup(markup, "html.parser")
                node.replace_with(subsoup)
                modified = True
        if modified:
            dst_file.write_text(str(soup))
        self.processed.add(filename)

    def on_after_build_all(self, builder, **extra):
        reporter.report_generic("Finished setting fixed languages")
