from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckComments(LexRule):
    """Check comments are followed by a space or are line comment."""

    rulename = 'Comments'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, loc, filebuf, tok):
        if tok == tokens.Tok.Comment:
            p = loc.start
            assert filebuf[p:p + 2] == b'--'
            if p != 0 and filebuf[p - 1] not in b" \t\r\n":
                self.error(loc, "missing space before comment")
            if filebuf[p + 2] in b" -=\r\n":
                return
            self.error(loc, "space required after comment")

    @staticmethod
    def test(runner):
        rule = CheckComments()
        TestRunOK(runner, "File with correct comments",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Comment not followed by a space",
                    rule, "comment1.vhdl")
        TestRunOK(runner, "File with a line comment",
                  rule, "comment2.vhdl")
