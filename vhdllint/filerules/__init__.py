"""File wide rules.
   The input of these rule checkers is the filename and the files (as a list
   of line). The rules must have a file scope, like presence of an header,
   no trailing spaces, max line length...

   Do not check about comments, the place for that in lexrules."""

from vhdllint.rule import Rule


class FileRule(Rule):
    def __init__(self, rulename):
        super(FileRule, self).__init__(rulename)

    def check(self, loc, lines):
        """The check to be performed on the whole file.
            lines is the list of lines, with the line terminator"""
        assert False  # Must be redefined
