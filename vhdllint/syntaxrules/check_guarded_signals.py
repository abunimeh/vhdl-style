from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import vhdllint.nodeutils as nodeutils
import libghdl.iirs as iirs


class CheckGuardedSignals(SyntaxNodeRule):
    """Check no guarded signals."""

    rulename = 'GuardedSignals'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k == iirs.Iir_Kind.Signal_Declaration \
           or k == iirs.Iir_Kind.Interface_Signal_Declaration:
            if iirs.Get_Guarded_Signal_Flag(node):
                self.error(
                    Location.from_node(node),
                    "signal '{0}' must not be guarded".format(
                        nodeutils.get_identifier_str(node)))

    @staticmethod
    def test(runner):
        rule = CheckGuardedSignals()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Guarded signal declaration",
                    rule, "guardedsignal1.vhdl")
        TestRunOK(runner, "resolved signal declaration",
                  rule, "guardedsignal2.vhdl")
        TestRunFail(runner, "Guarded interface",
                    rule, "guardedsignal3.vhdl")
