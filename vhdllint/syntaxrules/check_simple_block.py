from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thin as thin


class CheckSimpleBlock(SyntaxNodeRule):
    """Check block statements declare neither ports, nor generics nor
    implicit GUARD signal."""

    rulename = 'BlockStatement'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Block_Statement:
            hdr = iirs.Get_Block_Header(node)
            if hdr != thin.Null_Iir:
                if iirs.Get_Generic_Chain(hdr) != thin.Null_Iir:
                    self.error(
                        Location.from_node(node),
                        "block cannot declare generics")
                if iirs.Get_Port_Chain(hdr) != thin.Null_Iir:
                    self.error(
                        Location.from_node(node),
                        "block cannot declare ports")
            if iirs.Get_Guard_Decl(node) != thin.Null_Iir:
                    self.error(
                        Location.from_node(node),
                        "block cannot have an implicit GUARD signal")

    @staticmethod
    def test(runner):
        rule = CheckSimpleBlock()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Block with a generic",
                    rule, "simpleblock1.vhdl")
        TestRunFail(runner, "Block with a port",
                    rule, "simpleblock2.vhdl")
        TestRunFail(runner, "Block with a GUARD",
                    rule, "simpleblock3.vhdl")
        TestRunOK(runner, "Simple block",
                  rule, "simpleblock4.vhdl")
