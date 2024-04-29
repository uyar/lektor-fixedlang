# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-fixedlang is released under the BSD license.
# Read the included LICENSE.txt file for details.

__version__ = "0.2"

import re
from pathlib import Path

from lektor.db import Page
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter


class FixedLangPlugin(Plugin):
    name = "fixedlang"
    description = "Set fixed language for specific patterns."

    def on_setup_env(self, **extra):
        config = self.get_config()
        self.patterns = {}
        for tag in config.sections():
            for pattern, lang in config.section_as_dict(tag).items():
                self.patterns[pattern] = (lang, tag)
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
        for pattern, (lang, tag) in self.patterns.items():
            if re.search(pattern, content, flags=re.IGNORECASE):
                content = re.sub(
                    f'({pattern})',
                    f'<{tag} lang="{lang}">\\1</{tag}>',
                    content,
                )
                modified = True
        if modified:
            dst_file.write_text(content)
        self.processed.add(filename)

    def on_after_build_all(self, builder, **extra):
        reporter.report_generic("Finished setting fixed languages")
