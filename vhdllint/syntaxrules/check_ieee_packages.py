from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs
import libghdl.std_names as std_names
import vhdllint.nodeutils as nodeutils


class CheckIeeePackages(SyntaxRule):
    """Check that only standard IEEE packages are referenced in use clauses.
    This check only applies to 'synth' units.

    Only top-level use clauses are checked."""

    rulename = 'IeeePackages'

    def __init__(self, extra_pkg=[], name=None):
        super(self.__class__, self).__init__(name)
        # Add math_real and math_complex ?
        # Add vhdl-2008 packages ?
        self._allowed_name = ["std_logic_1164", "numeric_std"]
        self._allowed_name.extend(extra_pkg)
        self._allowed_id = None

    def check_clause(self, cl):
        name = iirs.Get_Selected_Name(cl)
        if iirs.Get_Kind(name) == iirs.Iir_Kind.Selected_By_All_Name:
            name = iirs.Get_Prefix(name)
        if iirs.Get_Kind(name) != iirs.Iir_Kind.Selected_Name:
            self.error(Location.from_node(name),
                       "unhandled use clause form")
            return
        lib = iirs.Get_Prefix(name)
        if iirs.Get_Kind(lib) != iirs.Iir_Kind.Simple_Name:
            self.error(Location.from_node(name),
                       "unhandled use clause form")
            return
        if iirs.Get_Identifier(lib) != std_names.Name.Ieee:
            # User package ?
            return
        if iirs.Get_Identifier(name) not in self._allowed_id:
            self.error(Location.from_node(name),
                       "non-allowed use of IEEE package {}".format(
                       nodeutils.get_identifier_str(name)))

    def check(self, input, file):
        if self._allowed_id is None:
            self._allowed_id = [thin.Get_Identifier(n)
                                for n in self._allowed_name]
        for unit in thinutils.chain_iter(iirs.Get_First_Design_Unit(file)):
            for n in thinutils.chain_iter(iirs.Get_Context_Items(unit)):
                if iirs.Get_Kind(n) != iirs.Iir_Kind.Use_Clause:
                    continue
                cl = n
                while cl != thin.Null_Iir:
                    self.check_clause(cl)
                    cl = iirs.Get_Use_Clause_Chain(cl)

    @staticmethod
    def test(runner):
        rule = CheckIeeePackages()
        TestRunOK(runner, "File without ieee",
                  rule, "hello.vhdl")
        TestRunOK(runner, "standard ieee package",
                  rule, "ieeepkg1.vhdl")
        TestRunFail(runner, "non-standard ieee package",
                    rule, "ieeepkg2.vhdl")
