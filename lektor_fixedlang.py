# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-fixedlang is released under the BSD license.
# Read the included LICENSE.txt file for details.

__version__ = "0.5"

import re
from functools import partial
from pathlib import Path

from lektor.db import Page
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter
from lxml import html


_NAMESPACES = {"re": "http://exslt.org/regular-expressions"}


def inherited_lang(node):
    lang = None
    for parent in [node] + list(node.iterancestors()):
        lang = parent.get("lang")
        if lang is not None:
            break
    return lang


from_html = html.fromstring
to_html = partial(html.tostring, encoding="unicode")


class FixedLangPlugin(Plugin):
    name = "fixedlang"
    description = "Set fixed language for specific patterns."

    def on_setup_env(self, **extra):
        reporter.report_generic("Setting up fixed language patterns")
        config = self.get_config()
        self.patterns = []
        for lang in config.sections():
            for _, pattern in config.section_as_dict(lang).items():
                self.patterns.append((pattern, lang))

    def on_after_build(self, builder, build_state, source, prog, **extra):
        if not isinstance(source, Page):
            return
        artifact = prog.primary_artifact
        if (artifact is None) or (not artifact.updated):
            return
        dst_file = Path(artifact.dst_filename)
        content = dst_file.read_text()
        tree = from_html(content)
        modified = False
        for pattern, lang in self.patterns:
            nodes = tree.xpath(f"""//body//*[re:test(text(), '{pattern}')]""",
                               namespaces=_NAMESPACES)
            if len(nodes) > 0:
                for node in nodes:
                    if lang == inherited_lang(node):
                        continue
                    markup = re.sub(
                        f'({pattern})',
                        f'<span lang="{lang}">\\1</span>',
                        to_html(node),
                    )
                    new_node = from_html(markup)
                    for child in node:
                        node.remove(child)
                    node.text = new_node.text
                    for child in new_node:
                        node.append(child)
                modified = True
        if modified:
            dst_file.write_text(to_html(tree))
