from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckHeader(FileRule):
    """Check the file starts with an header."""

    rulename = 'Header'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def extract_header(self, lines):
        header = b""
        for l in lines:
            if not l.startswith(b'--'):
                break
            header += l
        return header

    def check(self, loc, lines):
        header = self.extract_header(lines)
        if header == b'':
            self.error(loc.new(1, 1), "file should have an header")

    @staticmethod
    def test(runner):
        rule = CheckHeader()
        TestRunOK(runner, "File with an header",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File without an header",
                    rule, "noheader.vhdl")
        TestRunFail(runner, "File without an header at line 1",
                    rule, "noheader2.vhdl")
