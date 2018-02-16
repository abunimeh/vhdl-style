from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils


class CheckPortsName(SyntaxNodeRule):
    """Check names of ports."""

    rulename = 'PortsName'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if nodeutils.is_port(node):
            s = nodeutils.get_identifier_str(node)
            mode = iirs.Get_Mode(node)
            if mode == iirs.Iir_Mode.Out_Mode:
                if not s.endswith('_o'):
                    self.error(Location.from_node(node),
                               "out port '{0}' must end with '_o'".format(s))
            elif mode == iirs.Iir_Mode.In_Mode:
                if not s.endswith('_i'):
                    self.error(Location.from_node(node),
                               "in port '{0}' must end with '_i'".format(s))
            elif mode == iirs.Iir_Mode.Inout_Mode:
                if not s.endswith('_b'):
                    self.error(Location.from_node(node),
                               "inout port '{0}' must end with '_b'".format(s))
            elif mode == iirs.Iir_Mode.Buffer_Mode:
                self.error(Location.from_node(node),
                           "buffer port '{0}' not allowed".format(s))
            elif mode == iirs.Iir_Mode.Linkage_Mode:
                self.error(Location.from_node(node),
                           "linkage port '{0}' not allowed".format(s))

    @staticmethod
    def test(runner):
        rule = CheckPortsName()
        TestRunOK(runner, "File without ports",
                  rule, "hello.vhdl")
        TestRunOK(runner, "correct ports",
                  rule, "port1.vhdl")
        TestRunFail(runner, "incorrect out port",
                    rule, "port2.vhdl")
        TestRunFail(runner, "incorrect in port",
                    rule, "port3.vhdl")
        TestRunFail(runner, "not allowed buffer port",
                    rule, "port4.vhdl")
