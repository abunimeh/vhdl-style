from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs


class CheckEntitySimple(SyntaxRule):
    """Check entities are simple: no declarations, only assert statements
    are allowed.
    """

    rulename = 'EntityItems'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_entity(self, ent):
        decl = iirs.Get_Declaration_Chain(ent)
        if decl != thin.Null_Iir:
            self.error(Location.from_node(decl),
                       "declaration not allowed in entity")
        first_stmt = iirs.Get_Concurrent_Statement_Chain(ent)
        for s in thinutils.chain_iter(first_stmt):
            k = iirs.Get_Kind(s)
            if k != iirs.Iir_Kind.Concurrent_Assertion_Statement:
                self.error(Location.from_node(s),
                           "concurrent statement not allowed in entity")

    def check(self, input, ast):
        assert iirs.Get_Kind(ast) == iirs.Iir_Kind.Design_File
        for u in thinutils.chain_iter(iirs.Get_First_Design_Unit(ast)):
            lu = iirs.Get_Library_Unit(u)
            if iirs.Get_Kind(lu) == iirs.Iir_Kind.Entity_Declaration:
                self.check_entity(lu)

    @staticmethod
    def test(runner):
        rule = CheckEntitySimple()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Entity with a declaration",
                    rule, "entityitems1.vhdl")
        TestRunFail(runner, "Entity with a process",
                    rule, "entityitems2.vhdl")
