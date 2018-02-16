from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckSpaceAfter(LexRule):
    """Check some delimiters are followed by one space."""

    rulename = 'SpaceAfter'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._toks = [tokens.Tok.Comma, tokens.Tok.Colon]
        self._spaces = b" \t\r\n"

    def check(self, loc, filebuf, tok):
        if tok in self._toks:
            e = loc.end
            if e < len(filebuf) and filebuf[e] not in self._spaces:
                self.error(
                    loc, "missing space after '{0}'".format(
                        filebuf[loc.start:loc.end]))

    @staticmethod
    def test(runner):
        rule = CheckSpaceAfter()
        TestRunOK(runner, "File with spaces around operator",
                  rule, "hello.vhdl")
        TestRunFail(runner, "No space after ':'",
                    rule, "nospace1.vhdl")
