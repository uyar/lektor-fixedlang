# Copyright (C) 2024 H. Turgut Uyar <uyar@tekir.org>
#
# lektor-fixedlang is released under the BSD license.
# Read the included LICENSE.txt file for details.

import re
from collections import defaultdict
from pathlib import Path

from lektor.db import Page
from lektor.pluginsystem import Plugin


class FixedLangPlugin(Plugin):
    name = "fixedlang"
    description = "Set fixed language for specific patterns."

    def on_setup_env(self, **extra):
        config = self.get_config()
        self.patterns = defaultdict(dict)
        for tag in config.sections():
            for pattern, lang in config.section_as_dict(tag).items():
                self.patterns[pattern].update({"lang": lang, "tag": tag})
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
            for pattern, lang_tag in self.patterns.items():
                if re.search(pattern, content, flags=re.IGNORECASE):
                    content = re.sub(
                        f'({pattern})',
                        '<%(tag)s lang="%(lang)s">\\1</%(tag)s>' % lang_tag,
                        content,
                        flags=re.IGNORECASE,
                    )
                    modified = True
            if modified:
                Path(filename).write_text(content)
            self.processed.add(filename)
