from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils


class CheckSignalsName(SyntaxNodeRule):
    """Check names of signals."""

    rulename = 'SignalsName'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_name(self, node, name):
        orig_name = name
        if len(name) > 2 and name[-2] == '_' and name[-1] in 'oib':
            name = name[:-2]
        if name.endswith('_n'):
            name = name[:-2]
        if name.endswith('_a'):
            name = name[:-2]
        while True:
            if name.endswith('_p'):
                name = name[:-2]
            elif name.endswith('_d'):
                name = name[:-2]
            elif (len(name) > 3 and name[-3] == '_'
                  and name[-2] == 'd' and name[-1].isdigit()):
                name = name[:-3]
            else:
                break
        if name.endswith('_n'):
            self.error(Location.from_node(node),
                       "'_n' suffix of signal '{}' is too early".format(
                       orig_name))
        if name.endswith('_a'):
            self.error(Location.from_node(node),
                       "'_a' suffix of signal '{}' is too early".format(
                       orig_name))

    def check(self, input, node):
        if nodeutils.is_port(node):
            s = nodeutils.get_identifier_str(node)
            self.check_name(node, s)
        elif iirs.Get_Kind(node) == iirs.Iir_Kind.Signal_Declaration:
            s = nodeutils.get_identifier_str(node)
            self.check_name(node, s)

    @staticmethod
    def test(runner):
        rule = CheckSignalsName()
        TestRunOK(runner, "File without ports",
                  rule, "hello.vhdl")
        TestRunOK(runner, "correct signals",
                  rule, "signalsname1.vhdl")
        TestRunOK(runner, "signal with a direction suffix",
                  rule, "signalsname2.vhdl")
        TestRunFail(runner, "bad suffix order in signal name",
                    rule, "signalsname3.vhdl")
