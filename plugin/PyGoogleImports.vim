

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
            ln.startswith('import')
        ):
            if not firstln:
                firstln = endln
            print >>document, ln
        else:
            break
endln -= 1

source = document.getvalue()

sorter = sort_imports.ImportSorter()
sorter.visit(ast.parse(source))

output = StringIO.StringIO()

sorter.print_sorted(output)
lines = output.getvalue().splitlines()

print firstln, endln

vim.current.buffer[firstln-1:endln+1] = None
vim.current.buffer[firstln-1:firstln-1] = lines

EOF
endfunction

noremap <buffer> <F9> :call PyGoogleImports()<CR>
