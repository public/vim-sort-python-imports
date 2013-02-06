Auto-sort Imports
=================

Automatically sorts your Python imports according to the Google style guide.
http://google-styleguide.googlecode.com/svn/trunk/pyguide.html#Imports

This is a Pathogen plugin. https://github.com/tpope/vim-pathogen

Install it and fit F9. It will sort all the imports at the top of your file.

If you have comments at the top of your file e.g. `#!/usr/bin/env python`
it will keep them. Unless they are interleaved with your import statements,
in which case currently it will remove them :( The ast module ignores comments
entirely so this is probably not going to get fixed any time soon, but if you
have any ideas, do let me know :)

Alex Stapleton <alexs@prol.etari.at>

