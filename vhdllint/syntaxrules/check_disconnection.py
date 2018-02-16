from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs


class CheckDisconnection(SyntaxNodeRule):
    """Check no disconnection specification."""

    rulename = 'Disconnection'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k == iirs.Iir_Kind.Disconnection_Specification:
            self.error(
                Location.from_node(node),
                "disconnection specification not allowed")

    @staticmethod
    def test(runner):
        rule = CheckDisconnection()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple disconnection specification",
                    rule, "disconnect1.vhdl")
