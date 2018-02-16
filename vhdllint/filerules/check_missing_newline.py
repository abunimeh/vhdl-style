from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckMissingNewline(FileRule):
    """Check the file finishes with a newline."""

    rulename = 'NewlineEOF'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, loc, lines):
        nbr_lines = len(lines)
        if nbr_lines == 0:
            return
        lastline = lines[nbr_lines - 1]
        linelen = len(lastline)
        if linelen == 0 or lastline[linelen - 1] not in b"\r\n":
            self.error(loc.new(nbr_lines, linelen),
                       'missing newline at end of file')

    @staticmethod
    def test(runner):
        rule = CheckMissingNewline()
        TestRunOK(runner, "File with a newline at the end",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File without a newline at EOF",
                    rule, "nonewlineateof.vhdl")
