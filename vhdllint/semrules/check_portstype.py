from vhdllint.semrules import SemRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thinutils as thinutils
import vhdllint.nodeutils as nodeutils


class CheckPortsType(SemRule):
    """Check type of ports.

       Port of top units must be of type std_logic or std_logic_vector, or
       record of these types."""

    rulename = 'PortsType'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_type(self, typ):
        if nodeutils.is_std_logic_or_std_logic_vector(typ):
            return True
        basetype = iirs.Get_Base_Type(typ)
        if iirs.Get_Kind(basetype) == iirs.Iir_Kind.Record_Type_Definition:
            els = iirs.Get_Elements_Declaration_List(basetype)
            for el in thinutils.flist_iter(els):
                if not self.check_type(iirs.Get_Type(el)):
                    return False
            return True
        return False

    def check(self, input, ast):
        if 'top' not in input.props:
            return
        unit = iirs.Get_Library_Unit(ast)
        if iirs.Get_Kind(unit) != iirs.Iir_Kind.Entity_Declaration:
            return
        for port in thinutils.chain_iter(iirs.Get_Port_Chain(unit)):
            if not self.check_type(iirs.Get_Type(port)):
                self.error(
                    Location.from_node(port),
                    "type of port '{0}' must be std_logic/_vector".format(
                        nodeutils.get_identifier_str(port)))

    @staticmethod
    def test(runner):
        rule = CheckPortsType()
        TestRunOK(runner, "File without ports",
                  rule, ['--top', "hello.vhdl"])
        TestRunOK(runner, "correct ports",
                  rule, ['--top', "porttypes1.vhdl"])
        TestRunFail(runner, "port std_ulogic",
                    rule, ['--top', "porttypes2.vhdl"])
        TestRunFail(runner, "port std_ulogic_vector",
                    rule, ['--top', "porttypes3.vhdl"])
        TestRunOK(runner, "port with record",
                  rule, ['--top', "porttypes4.vhdl"])
        TestRunFail(runner, "port with bad record",
                    rule, ['--top', "porttypes5.vhdl"])
        TestRunOK(runner, "port with nested record",
                  rule, ['--top', "porttypes6.vhdl"])
