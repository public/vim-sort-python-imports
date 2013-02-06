

if !has('python')
    echo "Error: Required vim compiled with +python"
    finish
endif


function PyGoogleImports()
python <<EOF

import ast
import StringIO
import sys
import os
sys.path.append('plugin')
import vim

import sort_imports

firstln = 0
endln = 0
document = StringIO.StringIO()
for endln, ln in enumerate(vim.current.buffer):
    if ln.strip():
        if (
            ln.startswith('from') or
            ln.startswith('import') or
            ln.startswith('#') or
            ln.startswith('"')
        ):
            if not firstln:
                firstln = endln
            print >>document, ln
        else:
            break

sorter = sort_imports.ImportSorter()
sorter.visit(ast.parse(document.getvalue()))

output = StringIO.StringIO()

sorter.print_sorted(output)
lines = output.getvalue().splitlines()

vim.current.buffer[firstln:endln+1] = None
vim.current.buffer[firstln:firstln] = lines

EOF
endfunction

noremap <buffer> <F9> :call PyGoogleImports()<CR>
