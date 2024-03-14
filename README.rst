lektor-fixedlang
================

lektor-fixedlang is a plugin for the `Lektor`_ static site generator
that marks some patterns in output files with ``lang`` attributes.

Why?
----

It might be the case that a document contains words or phrases
that are in a language other than the current document's language.
If not marked properly, these parts will be processed
using an incorrect language's rules
(such as for case conversion and hyphenation),
and screen readers will pronounce them aloud incorrectly.
For example, in Turkish, the uppercase form for ``i`` is ``İ``,
and the lowercase form for ``I`` is ``ı``.
If you use the word "Wikipedia" in Turkish text,
a ``text-transform: uppercase`` CSS rule will cause it
to be displayed as "WİKİPEDİA".

To prevent this, such pieces of text have to be marked using a ``lang``
attribute, as in ``<span lang="en">Wikipedia</span>``.
This can of course be done manually when writing the content,
but that's going to be inconvenient for content writers,
and it can also be easily overlooked.

Installation
------------

To use the plugin, add it to your project::

  lektor plugin add lektor-fixedlang

The plugin can be configured using the ``configs/fixedlang.ini`` file.
Every section is the name of the tag that will wrap the pattern.
Every key in the section is a regular expression pattern
and the value is the language for the pattern.

Example::

  [span]
  \bWikipedia\b = en

.. _Lektor: https://www.getlektor.com/
