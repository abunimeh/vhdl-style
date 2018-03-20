from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils


class CheckNameDecl(SyntaxNodeRule):
    """Check name of declarations."""

    rulename = 'NameDecl'

    def __init__(self, kind=None, predicate=None, name=None):
        """Create the rule
        :param kind: only these nodes are checked.
        :param predicate: predicate on the name
        """
        super(self.__class__, self).__init__(name)
        self.kind = kind
        self.predicate = predicate

    def check_predicate(self, p, node, s):
        """Test predicate :param p: on string :param s:.  The predicate shall
         return an error message in case of error or None if the name is
         correct."""
        res = p(s)
        if isinstance(res, str):
            self.error(Location.from_node(node), res)
            return True
        elif res is None or res:
            return False
        else:
            self.error(Location.from_node(node),
                       "incorrect name '{}'".format(s))
            return True

    def check(self, input, node):
        if iirs.Get_Kind(node) == self.kind:
            s = nodeutils.get_identifier_str(node)
            if isinstance(self.predicate, list):
                for p in self.predicate:
                    if self.check_predicate(p, node, s):
                        break
            else:
                self.check_predicate(self.predicate, node, s)

    @staticmethod
    def test(runner):
        rule = CheckNameDecl(
            kind=iirs.Iir_Kind.Constant_Declaration,
            predicate=(lambda s: ("name {} must not be 'Reserved'".format(s)
                                  if s == 'Reserved' else None)))
        TestRunOK(runner, "File without attributes",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Incorrect name",
                    rule, "namedecl1.vhdl")
        TestRunOK(runner, "Correct name",
                  rule, "namedecl2.vhdl")
