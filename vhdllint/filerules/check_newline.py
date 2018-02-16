from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckNewline(FileRule):
    """Check the newline is LF (unix convention)."""

    rulename = 'Newline'

    def __init__(self, newline=b'\n', name=None):
        super(self.__class__, self).__init__(name)
        self._newline = newline

    def check(self, loc, lines):
        nllen = len(self._newline)
        for lineno, line in enumerate(lines):
            l = len(line)
            if l < nllen \
               or line[-nllen:] != self._newline \
               or (l > nllen and line[-nllen - 1] in b"\r\n"):
                self.error(loc.new(lineno + 1, l), "incorrect newline")
            elif l > nllen > l and line[0] in b"\r\n":
                self.error(loc.new(lineno + 1, 1), "incorrect newline")

    @staticmethod
    def test(runner):
        rule = CheckNewline()
        TestRunOK(runner, "File with unix newline",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with dos newline",
                    rule, "dosfile.vhdl")
        TestRunFail(runner, "File with macos newline",
                    rule, "macfile.vhdl")
