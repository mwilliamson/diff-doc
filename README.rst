diff-doc
========

Installation
------------

::

    pip install diff-doc

Usage
-----

To compile a source file:

    diff-doc compile README.src.rst > README.rst

To convert a diff block starting on line 42 to a replace block:

    diff-doc convert-block README.src.rst 42 replace

To convert a replace block starting on line 42 to a diff block:

    diff-doc convert-block README.src.rst 42 diff
