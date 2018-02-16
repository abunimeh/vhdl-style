from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckNoTrailingSpaces(FileRule):
    """Check there is no trailing spaces."""

    rulename = 'NoSpaceEOL'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, loc, lines):
        for lineno, line in enumerate(lines):
            line = line.rstrip(b"\r\n")
            ln = len(line)
            if ln > 0 and line[ln - 1] in b' \t':
                self.error(loc.new(lineno + 1, ln), "trailing space")

    @staticmethod
    def test(runner):
        rule = CheckNoTrailingSpaces()
        TestRunOK(runner, "File with no trailing spaces",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with a trailing space",
                    rule, "trailingspace.vhdl")
