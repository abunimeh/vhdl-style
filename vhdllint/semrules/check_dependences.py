from vhdllint.semrules import SemRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thinutils as thinutils
import libghdl.thin as thin
import vhdllint.nodeutils as nodeutils


class CheckDependences(SemRule):
    """Check all packages are 'imported' by a use clause.

       Detect reference to packages that weren't referenced in a context
       clause."""
    # Check architecture

    rulename = 'Dependences'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, ast):
        # Build the list of use'd packages.
        pkgs = []
        for n in thinutils.chain_iter(iirs.Get_Context_Items(ast)):
            if iirs.Get_Kind(n) != iirs.Iir_Kind.Use_Clause:
                continue
            cl = n
            while cl != thin.Null_Iir:
                name = iirs.Get_Selected_Name(cl)
                if iirs.Get_Kind(name) == iirs.Iir_Kind.Selected_By_All_Name:
                    name = iirs.Get_Prefix(name)
                p = iirs.Get_Named_Entity(name)
                if iirs.Get_Kind(p) == iirs.Iir_Kind.Package_Declaration:
                    pkgs.append(p)
                cl = iirs.Get_Use_Clause_Chain(cl)
        # Check dependences
        for du in thinutils.list_iter(iirs.Get_Dependence_List(ast)):
            lu = iirs.Get_Library_Unit(du)
            if iirs.Get_Kind(lu) == iirs.Iir_Kind.Package_Declaration:
                if lu != thin.Standard_Package.value and lu not in pkgs:
                    self.error(
                        Location.from_node(ast),
                        "unit depends on '{}' but not by a use clause".format(
                            nodeutils.get_identifier_str(lu)))

    @staticmethod
    def test(runner):
        rule = CheckDependences()
        TestRunOK(runner, "Correct file",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Use through entity",
                  rule, "dependences1.vhdl")
        TestRunOK(runner, "Normal use",
                  rule, "dependences2.vhdl")
        TestRunFail(runner, "Incorrect use",
                    rule, "dependences3.vhdl")
        TestRunFail(runner, "Incorrect use",
                    rule, "dependences4.vhdl")
