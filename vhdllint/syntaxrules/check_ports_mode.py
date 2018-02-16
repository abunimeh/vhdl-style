from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils


class CheckPortsMode(SyntaxNodeRule):
    """Check mode of ports."""

    rulename = 'PortMode'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if nodeutils.is_port(node):
            mode = iirs.Get_Mode(node)
            if mode == iirs.Iir_Mode.Buffer_Mode:
                self.error(Location.from_node(node),
                           "buffer port '{0}' not allowed".format(
                           nodeutils.get_identifier_str(node)))
            elif mode == iirs.Iir_Mode.Linkage_Mode:
                self.error(Location.from_node(node),
                           "linkage port '{0}' not allowed".format(
                           nodeutils.get_identifier_str(node)))

    @staticmethod
    def test(runner):
        rule = CheckPortsMode()
        TestRunOK(runner, "File without ports",
                  rule, "hello.vhdl")
        TestRunOK(runner, "correct ports",
                  rule, "port1.vhdl")
        TestRunFail(runner, "not allowed buffer port",
                    rule, "port4.vhdl")
