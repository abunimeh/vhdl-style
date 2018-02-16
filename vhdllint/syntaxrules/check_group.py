from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs


class CheckGroup(SyntaxNodeRule):
    """Check no group nor group template declaration."""

    rulename = 'GroupDeclaration'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k == iirs.Iir_Kind.Group_Declaration:
            self.error(
                Location.from_node(node),
                "group declaration not allowed")
        elif k == iirs.Iir_Kind.Group_Template_Declaration:
            self.error(
                Location.from_node(node),
                "group template declaration not allowed")

    @staticmethod
    def test(runner):
        rule = CheckGroup()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple disconnection specification",
                    rule, "group1.vhdl")
