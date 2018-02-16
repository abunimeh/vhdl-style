from vhdllint.semrules import SemRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import vhdllint.nodeutils as nodeutils
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs


class CheckUnused(SemRule):
    """Report unused declarations in architectures and package bodies.

       One character loop iterators (like 'for i in ...') are not reported."""

    rulename = 'Unused'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._handlers = {}

    def mark_used(self, n):
        self._used.add(n)

    def mark(self, unit):
        for n in thinutils.nodes_iter(unit):
            k = iirs.Get_Kind(n)
            if k == iirs.Iir_Kind.Simple_Name \
               or k == iirs.Iir_Kind.Selected_Name:
                self.mark_used(iirs.Get_Named_Entity(n))
            elif k == iirs.Iir_Kind.Selected_Element:
                self.mark_used(iirs.Get_Selected_Element(n))

    def is_second_subprogram(self, decl):
        return iirs.Get_Kind(decl) in iirs.Iir_Kinds.Subprogram_Declaration \
            and thin.Iirs_Utils.Is_Second_Subprogram_Specification(decl)

    def report_unused(self, unit):
        for n in thinutils.declarations_iter(unit):
            if n in self._used \
               or nodeutils.is_predefined_node(n):
                # Node is used (or not user defined)
                continue
            k = iirs.Get_Kind(n)
            if k in [iirs.Iir_Kind.Function_Body,
                     iirs.Iir_Kind.Procedure_Body]:
                # Bodies are never referenced.
                continue
            if self.is_second_subprogram(n):
                # Subprogram specification of a body is never referenced.
                continue
            if k in iirs.Iir_Kinds.Interface_Object_Declaration:
                p = iirs.Get_Parent(n)
                if p != thin.Null_Iir \
                   and self.is_second_subprogram(p):
                    # Interfaces without parent are from implicit subprograms.
                    # Interfaces of the subprg spec of the body aren't
                    # referenced.
                    continue
            if k in [iirs.Iir_Kind.Anonymous_Type_Declaration]:
                # Anonymous types are never referenced.
                continue
            if k == iirs.Iir_Kind.Iterator_Declaration \
               and thin.Get_Name_Length(iirs.Get_Identifier(n)) == 1:
                # Loop iterator with a very short name (for i in ...)
                # Allow it to be unused.
                continue
            self.error(
                Location.from_node(n),
                "{} is not used".format(
                    nodeutils.get_identifier_str(n)))

    def check(self, input, unit):
        libunit = iirs.Get_Library_Unit(unit)
        k = iirs.Get_Kind(libunit)
        if k == iirs.Iir_Kind.Architecture_Body:
            self._used = set()
            ent = thin.Iirs_Utils.Get_Entity(libunit)
            self.mark(ent)
            self.mark(libunit)
            self.report_unused(ent)
            self.report_unused(libunit)
        elif k == iirs.Iir_Kind.Package_Body:
            self._used = set()
            self.mark(libunit)
            self.report_unused(libunit)

    @staticmethod
    def test(runner):
        rule = CheckUnused()
        TestRunOK(runner, "File without references",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Unused port",
                    rule, "unused1.vhdl")
        TestRunOK(runner, "Used generic",
                  rule, "unused2.vhdl")
        TestRunFail(runner, "Unused constant declaration in package body",
                    rule, "unused3.vhdl")
        TestRunOK(runner, "Used function with a specification",
                  rule, "unused4.vhdl")
