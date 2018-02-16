from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs


class CheckContextUse(SyntaxNodeRule):
    """Check use clauses are placed in context clauses."""

    rulename = 'ContextUse'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Use_Clause:
            parent = iirs.Get_Parent(node)
            if iirs.Get_Kind(parent) != iirs.Iir_Kind.Design_Unit:
                self.error(
                    Location.from_node(node),
                    "use clause must be global (placed before the unit)")

    @staticmethod
    def test(runner):
        rule = CheckContextUse()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Global use clause",
                  rule, "contextuse1.vhdl")
        TestRunFail(runner, "Local use clause",
                    rule, "contextuse2.vhdl")
