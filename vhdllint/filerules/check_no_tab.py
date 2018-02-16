from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckNoTAB(FileRule):
    """Check there is no TAB (HT, VT and FF)."""

    rulename = 'NoTAB'

    def __init__(self, tabs=b"\t\v\f", name=None):
        super(self.__class__, self).__init__(name)
        self._tabs = tabs

    def check(self, loc, lines):
        for lineno, line in enumerate(lines):
            for col, c in enumerate(line):
                if c in self._tabs:
                    self.error(loc.new(lineno + 1, col + 1),
                               "HT not allowed" if c == '\t'
                               else "character not allowed")
                    # At most one error per line
                    break

    @staticmethod
    def test(runner):
        rule = CheckNoTAB()
        TestRunOK(runner, "File with no tab",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with an horizontal tab (HT)",
                    rule, "ht.vhdl")
        TestRunFail(runner, "File with an vertical tab (VT)",
                    rule, "vt.vhdl")
        TestRunFail(runner, "File with a form-feed (FF)",
                    rule, "ff.vhdl")
