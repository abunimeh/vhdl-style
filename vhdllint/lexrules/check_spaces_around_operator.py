from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens


class CheckSpacesAroundOperator(LexRule):
    """Check operators have a space before and after."""
    # ... for some extended definition of operators.

    rulename = 'OperatorSpace'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._operators = [tokens.Tok.Assign,
                           tokens.Tok.Equal, tokens.Tok.Not_Equal,
                           tokens.Tok.Less, tokens.Tok.Less_Equal,
                           tokens.Tok.Greater, tokens.Tok.Greater_Equal,
                           tokens.Tok.Plus,
                           tokens.Tok.Ampersand,  # tokens.Tok.Star,
                           tokens.Tok.Slash]
        self._spaces = b" \t\r\n"

    def check(self, loc, filebuf, tok):
        if tok in self._operators:
            s = filebuf[loc.start:loc.end]
            if loc.start > 0 and filebuf[loc.start - 1] not in self._spaces:
                self.error(
                    loc, "missing space before operator '{0}'".format(s))
            if loc.end < len(filebuf) and filebuf[loc.end] not in self._spaces:
                self.error(
                    loc, "missing space after operator '{0}'".format(s))
            elif (loc.end < len(filebuf) + 1
                  and filebuf[loc.end] in b" \t"
                  and filebuf[loc.end + 1] in b" \t"):
                self.error(
                    loc, "multiple spaces after operator '{0}'".format(s))

    @staticmethod
    def test(runner):
        rule = CheckSpacesAroundOperator()
        TestRunOK(runner, "File with spaces around operator",
                  rule, "hello.vhdl")
        TestRunFail(runner, "No space after '+'",
                    rule, "operatorspace1.vhdl")
        TestRunFail(runner, "No space before '/'",
                    rule, "operatorspace2.vhdl")
        TestRunFail(runner, "Multiple spaces after '>'",
                    rule, "operatorspace3.vhdl")
