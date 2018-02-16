from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckNoSpaceAfter(LexRule):
    """Check some delimiters are not followed by a space."""

    rulename = 'NoSpaceAfter'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._toks = [tokens.Tok.Tick, tokens.Tok.Dot]
        self._spaces = b" \t"

    def check(self, loc, filebuf, tok):
        if tok in self._toks:
            e = loc.end
            if e < len(filebuf) and filebuf[e] in self._spaces:
                self.error(
                    loc, "space not allowed space after '{0}'".format(
                        filebuf[loc.start:loc.end]))

    @staticmethod
    def test(runner):
        rule = CheckNoSpaceAfter()
        TestRunOK(runner, "File without space after '.'",
                  rule, "nospace5.vhdl")
        TestRunFail(runner, "Space after '",
                    rule, "nospace6.vhdl")
