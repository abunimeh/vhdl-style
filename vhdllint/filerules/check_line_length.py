from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckLineLength(FileRule):
    """Check maximum length of lines"""
    rulename = 'LineLen'

    def __init__(self, maxlen=80, name=None):
        super(self.__class__, self).__init__(name)
        self._maxlen = maxlen

    def check(self, loc, lines):
        lineno = 1
        for line in lines:
            linelen = len(line)
            # Strip CR/LF
            while linelen > 1 and line[linelen - 1] in b"\r\n":
                linelen -= 1
            if linelen > self._maxlen:
                self.error(loc.new(lineno, linelen), 'line is too long')
            lineno += 1

    @staticmethod
    def test(runner):
        rule = CheckLineLength()
        TestRunOK(runner, "File with normal lines",
                  rule, "hello.vhdl")
        TestRunOK(runner, "File with 2 lines of exactely 80 characters",
                  rule, "line80.vhdl")
        TestRunFail(runner, "File with a long line",
                    rule, "longline.vhdl")
