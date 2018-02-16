from vhdllint.semrules import SemRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thinutils as thinutils
import libghdl.thin as thin
import vhdllint.nodeutils as nodeutils


class CheckAssocs(SemRule):
    """Check associations order of instantiations.

       In component instantiations generics and ports must be associated by
       name in the same order as the interfaces."""

    rulename = 'Assocs'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_assocs(self, n, inters, assocs):
        if assocs == thin.Null_Iir:
            # Also cover the case of no interfaces
            return
        inter = inters
        for assoc in thinutils.chain_iter(assocs):
            if iirs.Get_Kind(assoc) \
               == iirs.Iir_Kind.Association_Element_By_Individual:
                continue
            formal = iirs.Get_Formal(assoc)
            if formal == thin.Null_Iir:
                self.error(
                    Location.from_node(assoc),
                    "association by position for {}".format(
                        nodeutils.get_identifier_str(inter)))
                # Should the tool report all errors ?
                return
            assoc_inter = thin.Iirs_Utils.Get_Interface_Of_Formal(formal)
            while assoc_inter != inter:
                if inter == thin.Null_Iir:
                    self.error(
                        Location.from_node(assoc),
                        "incorrect association order for {}".format(
                            nodeutils.get_identifier_str(assoc_inter)))
                    return
                inter = iirs.Get_Chain(inter)
            if iirs.Get_Whole_Association_Flag(assoc):
                inter = iirs.Get_Chain(inter)

    def check(self, input, ast):
        for n in thinutils.concurrent_stmts_iter(ast):
            if iirs.Get_Kind(n) \
               == iirs.Iir_Kind.Component_Instantiation_Statement:
                comp = thin.Iirs_Utils.Get_Entity_From_Entity_Aspect(
                    iirs.Get_Instantiated_Unit(n))
                self.check_assocs(
                    n, iirs.Get_Generic_Chain(comp),
                    iirs.Get_Generic_Map_Aspect_Chain(n))
                self.check_assocs(
                    n, iirs.Get_Port_Chain(comp),
                    iirs.Get_Port_Map_Aspect_Chain(n))

    @staticmethod
    def test(runner):
        rule = CheckAssocs()
        TestRunOK(runner, "File without ports",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Simple component",
                  rule, "assocs1.vhdl")
        TestRunFail(runner, "Simple component with incorrect order",
                    rule, "assocs2.vhdl")
        TestRunOK(runner, "Simple component without generics",
                  rule, "assocs3.vhdl")
        TestRunFail(runner, "Component with instantiation by position",
                    rule, "assocs4.vhdl")
