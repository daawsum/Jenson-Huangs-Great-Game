"""One-off repair: a line of 03c_statesize.py that a shell heredoc split across three lines."""
s = open("03c_statesize.py", encoding="utf-8", newline="").read()
i = s.index('cb = rd("common", "cb_types.txt").replace("')
j = s.index("# always start from vanilla's file", i)
s = s[:i] + 'cb = rd("common", "cb_types.txt").replace("\\r\\n", "\\n")      ' + s[j:]
open("03c_statesize.py", "w", encoding="utf-8", newline="").write(s)
import ast
ast.parse(open("03c_statesize.py", encoding="utf-8").read())
print("repaired and parses")
