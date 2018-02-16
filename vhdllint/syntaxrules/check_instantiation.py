from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import vhdllint.utils as utils
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocations


class CheckInstantiation(SyntaxRule):
    """Check layout of component instantiation"""
    # TODO: check order (need sem)
    # check 'generic' and 'port' on a different line

    rulename = 'Instantiation'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_associations(self, assoc):
        col = -1
        line = -1
        while assoc != thin.Null_Iir:
            if iirs.Get_Formal(assoc) == thin.Null_Iir:
                self.error(Location.from_node(assoc),
                           "association by name required")
            else:
                loc = elocations.Get_Arrow_Location(assoc)
                fe, ln, co = utils.Location_To_File_Line_Col(loc)
                if ln <= line:
                    self.error(Location.from_node(assoc),
                               "one association per line")
                elif col != co and col >= 0:
                    self.error(Location.from_node(assoc),
                               "`=>` place is not aligned with previous one")
                col = co
                line = ln
            assoc = iirs.Get_Chain(assoc)

    def check(self, input, ast):
        for node in thinutils.concurrent_stmts_iter(ast):
            k = iirs.Get_Kind(node)
            if k != iirs.Iir_Kind.Component_Instantiation_Statement:
                continue
            self.check_associations(iirs.Get_Generic_Map_Aspect_Chain(node))
            self.check_associations(iirs.Get_Port_Map_Aspect_Chain(node))

    @staticmethod
    def test(runner):
        rule = CheckInstantiation()
        TestRunOK(runner, "arch without instantiation",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Correct instantiation",
                  rule, "instantiation1.vhdl")
        TestRunFail(runner, "association not by name",
                    rule, "instantiation2.vhdl")
        TestRunFail(runner, "association on the same line",
                    rule, "instantiation3.vhdl")
        TestRunFail(runner, "associations not aligned",
                    rule, "instantiation4.vhdl")
