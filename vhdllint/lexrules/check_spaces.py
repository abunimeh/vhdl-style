from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckSpaces(LexRule):
    """Check operators have a space before and after."""
    # ... for some extended definition of operators.

    rulename = 'Spaces'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        # What a space is
        self._spaces = b" \t\r\n"
        self._before_after = [tokens.Tok.Assign, tokens.Tok.Colon,
                              tokens.Tok.Equal, tokens.Tok.Not_Equal,
                              tokens.Tok.Less, tokens.Tok.Less_Equal,
                              tokens.Tok.Greater, tokens.Tok.Greater_Equal,
                              tokens.Tok.Double_Arrow]
        self._not_before = [tokens.Tok.Comma, tokens.Tok.Semi_Colon]
        self._prev_tok = tokens.Tok.Invalid

    def has_before(self, loc, filebuf):
        return loc.start > 0 and filebuf[loc.start - 1] in self._spaces

    def has_after(self, loc, filebuf):
        return loc.end < len(filebuf) and filebuf[loc.end] in self._spaces

    def check_before(self, loc, filebuf, s):
        if not self.has_before(loc, filebuf):
            self.error(loc, "missing space before '{0}'".format(s))

    def check_not_before(self, loc, filebuf, s):
        if self.has_before(loc, filebuf):
            self.error(loc, "extra space before '{0}'".format(s))

    def check_after(self, loc, filebuf, s):
        if not self.has_after(loc, filebuf):
            self.error(loc, "missing space after '{0}'".format(s))

    def check(self, loc, filebuf, tok):
        if tok in self._before_after:
            s = filebuf[loc.start:loc.end]
            self.check_before(loc, filebuf, s)
            self.check_after(loc, filebuf, s)
        elif tok in self._not_before:
            s = filebuf[loc.start:loc.end]
            self.check_not_before(loc, filebuf, s)

        self._prev_tok = tok

    @staticmethod
    def test(runner):
        rule = CheckSpaces()
        TestRunOK(runner, "File with no issues",
                  rule, "hello.vhdl")
        TestRunFail(runner, "No space after ':'",
                    rule, "nospace1.vhdl")
