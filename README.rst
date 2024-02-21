lektor-fixedlang
================

lektor-fixedlang is a plugin for the `Lektor <https://www.getlektor.com>`_
static site generator that marks some patterns in output files
with ``lang`` attributes.

Why?
----

Say you have a multilingual site where one of the languages you support
is Turkish. In Turkish, the uppercase form for ``i`` is ``İ``,
and the lowercase form for ``I`` is ``ı``. If you use an English word
containing these letters in Turkish text, a ``text-transform`` CSS rule
will cause the word to be shown incorrectly. For example, the word
"Wikipedia" transformed to uppercase will become "WİKİPEDİA".

To prevent this, you have to mark such pieces of text using a ``lang``
attribute, as in ``<span lang="en">Wikipedia</span>``. This can of course
be done manually when writing the content, but that's going to be inconvenient
for content writers and it can also be easily overlooked.

Although this "dotless-i / dotted-I" problem was the initial motivation
behind this plugin, it can be useful in other cases as well.

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

*Note*: At the moment, regular expression matches are case insensitive.
