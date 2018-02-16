from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs


class CheckConfigSpec(SyntaxNodeRule):
    """Check no configuration specification."""

    rulename = 'ConfigSpec'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k == iirs.Iir_Kind.Configuration_Specification:
            self.error(
                Location.from_node(node),
                "configuration specification not allowed")

    @staticmethod
    def test(runner):
        rule = CheckConfigSpec()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple configuration specification",
                    rule, "configspec1.vhdl")
