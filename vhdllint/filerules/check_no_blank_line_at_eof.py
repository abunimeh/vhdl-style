from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckNoBlankLineAtEOF(FileRule):
    """Check there is not blank line at end of file."""

    rulename = 'BlankLine'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, loc, lines):
        nbr_lines = len(lines)
        if nbr_lines == 0:
            return
        lastline = lines[nbr_lines - 1]
        if lastline.rstrip(b"\r\n\t ") == b'':
            self.error(loc.new(nbr_lines, 1),
                       'blank line at end of file')

    @staticmethod
    def test(runner):
        rule = CheckNoBlankLineAtEOF()
        TestRunOK(runner, "File with a newline at the end",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with a blank line at EOF",
                    rule, "blanklineateof.vhdl")
