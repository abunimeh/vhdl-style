from vhdllint.lexrules import LexRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.tokens as tokens
import libghdl.thin as thin


class CheckForbiddenId(LexRule):
    """Check for fobidden identifiers."""

    rulename = 'ForbiddenId'

    def __init__(self, ids=[b'l', b'o'], name=None):
        super(self.__class__, self).__init__(name)
        self._ids = ids

    def check(self, loc, filebuf, tok):
        if tok == tokens.Tok.Identifier:
            s = thin.Get_Name_Ptr(thin.Scanner.Current_Identifier())
            if s in self._ids:
                self.error(
                    loc, "use of forbidden identifier '{0}'".format(
                        s.decode('latin-1')))

    @staticmethod
    def test(runner):
        rule = CheckForbiddenId()
        TestRunOK(runner, "File with no forbidden id",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with identifier 'l'",
                    rule, "forbiddenid.vhdl")
