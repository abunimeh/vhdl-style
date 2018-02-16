from vhdllint.semrules import SemRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs
import libghdl.std_names as std_names
import vhdllint.nodeutils as nodeutils


class CheckStdHidding(SemRule):
    """Check that standard names (from std.standard or any ieee package)
    are never redeclared by user.

    TODO: should have a list of ieee identifiers instead of using those
    from use-d packages ?
    """

    rulename = 'StdHidding'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._standard_ids = None
        self._ieee_ids = set()
        self._ieee_pkgs = []

    def add_identifier(self, dct, decl):
        id = iirs.Get_Identifier(decl)
        if id >= std_names.Name.First_Keyword \
           and id <= std_names.Name.Last_Vhdl93:
            # An operator (like "and")
            return
        if id >= std_names.Name.First_Operator \
           and id <= std_names.Name.Last_Operator:
            # An operator (like "/=")
            return
        if id >= std_names.Name.First_Character \
           and id <= std_names.Name.Last_Character:
            # A character
            return
        dct.add(id)

    def gather_identifiers(self, pkg):
        res = set()
        for d in thinutils.chain_iter(iirs.Get_Declaration_Chain(pkg)):
            k = iirs.Get_Kind(d)
            if d in iirs.Iir_Kinds.Specification:
                continue
            self.add_identifier(res, d)
            if k in [iirs.Iir_Kind.Type_Declaration,
                     iirs.Iir_Kind.Anonymous_Type_Declaration]:
                typ = iirs.Get_Type_Definition(d)
                k = iirs.Get_Kind(typ)
                if k == iirs.Iir_Kind.Enumeration_Type_Definition:
                    for lit in thinutils.list_iter(
                            iirs.Get_Enumeration_Literal_List(typ)):
                        self.add_identifier(res, lit)
                elif k == iirs.Iir_Kind.Physical_Type_Definition:
                    for un in thinutils.chain_iter(iirs.Get_Unit_Chain(typ)):
                        self.add_identifier(res, un)
        return res

    def check(self, input, dsgn):
        if self._standard_ids is None:
            self._standard_ids = self.gather_identifiers(
                thin.Standard_Package.value)
        pkgs = nodeutils.extract_packages_from_context_clause(dsgn)
        for pkg in pkgs:
            lib = iirs.Get_Library(
                iirs.Get_Design_File(iirs.Get_Design_Unit(pkg)))
            if iirs.Get_Identifier(lib) == std_names.Name.Ieee \
               and pkg not in self._ieee_pkgs:
                self._ieee_pkgs.append(pkg)
                self._ieee_ids = self._ieee_ids.union(
                    self.gather_identifiers(pkg))
        lu = iirs.Get_Library_Unit(dsgn)
        for d in thinutils.declarations_iter(lu):
            id = iirs.Get_Identifier(d)
            if id in self._standard_ids:
                self.error(Location.from_node(d),
                           "declaration of {} uses a standard name".format(
                           nodeutils.get_identifier_str(d)))
            if id in self._ieee_ids:
                self.error(Location.from_node(d),
                           "declaration of {} uses an ieee name".format(
                           nodeutils.get_identifier_str(d)))

    @staticmethod
    def test(runner):
        rule = CheckStdHidding()
        TestRunOK(runner, "File without ieee",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Redefiniton of a standard identifier",
                    rule, "stdhide1.vhdl")
        TestRunFail(runner, "Redefiniton of an ieee identifier",
                    rule, "stdhide2.vhdl")
