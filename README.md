Auto-sort Imports
=================

Automatically sorts your Python imports according to the PEP8 / Google style guide.

http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Imports

This is a Pathogen plugin. https://github.com/tpope/vim-pathogen

Install it and fit F9. It will sort all the imports at the top of your file.

If you have comments at the top of your file e.g. `#!/usr/bin/env python`
it will keep them. Unless they are interleaved with your import statements,
in which case currently it will remove them :(


Why not RopeOrganizeImports?
----------------------------

This plugin might seem a bit like the sort of thing Rope already does, but it isn't.

This plugin intentionally doesn't attempt to remove unused names, or to identify
imports that don't exist or are otherwise incorrect. The main reason for this is
that the changes we make to the file are smaller, and so easier to verify for the
programmer.

Our output format is also optimised to match the Google coding style guidelines.


Bugs
----

No attempt is currently made to detect if you are importing something other than
a package or a module.


To Do
-----

Port this to using the Rope AST? It seems to have better fidelity than the one
in stdlib.

Alex Stapleton <alexs@prol.etari.at>

