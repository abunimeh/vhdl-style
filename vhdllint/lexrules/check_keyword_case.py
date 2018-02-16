from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckKeywordCase(LexRule):
    """Check keywords are in lower-case."""
    # OK, in VHDL there are no keywords but reserved words.

    rulename = 'KeywordCase'

    def __init__(self, filter=lambda x: x.islower(), name=None):
        super(self.__class__, self).__init__(name)
        self._filter = filter

    def check(self, loc, filebuf, tok):
        if tok >= tokens.Tok.And and tok <= tokens.Tok.Tolerance:
            s = filebuf[loc.start:loc.end]
            if not self._filter(s):
                self.error(loc, "incorrect keyword case for {0}".format(s))

    @staticmethod
    def test(runner):
        rule = CheckKeywordCase()
        TestRunOK(runner, "File with no tab",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File a keyword in upper case",
                    rule, "keyword.vhdl")
        TestRunFail(runner, "File a capitalized keyword",
                    rule, "keyword2.vhdl")
