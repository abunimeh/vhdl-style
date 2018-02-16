from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckCharSet(FileRule):
    """Check only 7-bit ASCII characters are used."""

    rulename = 'CharSet'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, loc, lines):
        for lineno, line in enumerate(lines):
            for col, c in enumerate(line):
                if ord(c) > 127:
                    self.error(loc.new(lineno + 1, col + 1),
                               "Non 7-bit ASCII character")
                    # At most one error per line
                    break

    @staticmethod
    def test(runner):
        rule = CheckCharSet()
        TestRunOK(runner, "File with no tab",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with an invalid character",
                    rule, "charset1.vhdl")
