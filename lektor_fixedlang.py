# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-fixedlang is released under the BSD license.
# Read the included LICENSE.txt file for details.

import re
from pathlib import Path

from lektor.db import Page
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter


class FixedLangPlugin(Plugin):
    name = "fixedlang"
    description = "Set fixed language for specific patterns."

    def on_setup_env(self, **extra):
        reporter.report_generic("Starting fixedlang processing")
        config = self.get_config()
        self.patterns = config.section_as_dict("default")
        self.processed = set()

    def on_after_build(self, builder, build_state, source, prog, **extra):
        if isinstance(source, Page):
            artifact = prog.primary_artifact
            if artifact is None:
                return
            filename = artifact.dst_filename
            if filename in self.processed:
                return
            content = Path(filename).read_text()
            modified = False
            for pattern, lang in self.patterns.items():
                if re.search(pattern, content, flags=re.IGNORECASE):
                    content = re.sub(f'({pattern})',
                                     f'<span lang="{lang}">\\1</span>',
                                     content,
                                     flags=re.IGNORECASE)
                    modified = True
            if modified:
                Path(filename).write_text(content)
                self.processed.add(filename)
