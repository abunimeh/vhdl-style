from vhdllint.semrules import SemNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import vhdllint.nodeutils as nodeutils
import libghdl.thin as thin
import libghdl.iirs as iirs
import libghdl.std_names as std_names


class CheckReferences(SemNodeRule):
    """Check case of names is the same as their definition.

    References to libraries name must be in lower case.
    References to names defined in the IEEE library must be in lower case.
    References to names defined in the STD library must be in lower case,
    except for control characters which must be in upper case.

    TODO: end names, operators."""

    rulename = 'References'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        self._handlers = {}

    def get_lower(self, dfn, s):
        """Referenced identifier must be in lower case."""
        return s.lower()

    def get_standard(self, dfn, s):
        """Referenced indentifier must be in lower case, except for control
           characters (which must be in upper case)."""
        if iirs.Get_Kind(dfn) == iirs.Iir_Kind.Enumeration_Literal \
           and iirs.Get_Type(dfn) == thin.Character_Type_Definition.value:
            return s.upper()
        else:
            return s.lower()

    def get_user(self, dfn, s):
        """Referenced identifier must match its definition."""
        return nodeutils.get_identifier_str(dfn)

    def find_handler(self, n):
        """Return the function to comparse the definition with the
           reference."""
        dfn_loc = iirs.Get_Location(n)
        dfn_file = thin.Location_To_File(dfn_loc)
        handler = self._handlers.get(dfn_file, None)
        if handler:
            return handler
        if dfn_loc == thin.Library_Location.value:
            handler = self.get_lower
        else:
            while iirs.Get_Kind(n) != iirs.Iir_Kind.Library_Declaration:
                n = iirs.Get_Parent(n)
            lib_id = iirs.Get_Identifier(n)
            if lib_id == std_names.Name.Std:
                handler = self.get_standard
            elif lib_id == std_names.Name.Ieee:
                handler = self.get_lower
            else:
                handler = self.get_user
        self._handlers[dfn_file] = handler
        return handler

    def check_identifier(self, node, dfn):
        if dfn == 0:
            # Can happen for architecture in entity aspect
            return
        ref_str = nodeutils.get_identifier_str(node)
        handler = self.find_handler(dfn)
        def_str = handler(dfn, ref_str)
        if ref_str == def_str:
            # OK!
            return
        if iirs.Get_Kind(dfn) == iirs.Iir_Kind.Guard_Signal_Declaration:
            # Guard signals are implicitely declared
            def_str = "GUARD"
            if ref_str == def_str:
                return
        self.error(
            Location.from_node(node),
            "{} is not the correct spelling for '{}'".format(
                ref_str, def_str))

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k == iirs.Iir_Kind.Simple_Name \
           or k == iirs.Iir_Kind.Selected_Name:
            self.check_identifier(node, iirs.Get_Named_Entity(node))
        elif k == iirs.Iir_Kind.Selected_Element:
            self.check_identifier(node, iirs.Get_Selected_Element(node))
        elif k == iirs.Iir_Kind.Library_Clause:
            self.check_identifier(node, iirs.Get_Library_Declaration(node))
        elif k == iirs.Iir_Kind.Attribute_Name:
            attr_val = iirs.Get_Named_Entity(node)
            attr_spec = iirs.Get_Attribute_Specification(attr_val)
            attr_name = iirs.Get_Attribute_Designator(attr_spec)
            self.check_identifier(node, iirs.Get_Named_Entity(attr_name))

    @staticmethod
    def test(runner):
        rule = CheckReferences()
        TestRunOK(runner, "File without references",
                  rule, "hello.vhdl")
        TestRunOK(runner, "correct reference (simple name)",
                  rule, "reference1.vhdl")
        TestRunFail(runner, "incorrect reference (simple name)",
                    rule, "reference2.vhdl")
        TestRunOK(runner, "correct reference (library clause)",
                  rule, "reference3.vhdl")
        TestRunFail(runner, "incorrect reference (library clause)",
                    rule, "reference4.vhdl")
        TestRunOK(runner, "correct reference (library name, selected name)",
                  rule, "reference5.vhdl")
        TestRunFail(runner, "incorrect reference (library name)",
                    rule, "reference6.vhdl")
        TestRunFail(runner, "incorrect reference (selected name)",
                    rule, "reference7.vhdl")
        TestRunOK(runner, "correct reference (name from ieee library)",
                  rule, "reference8.vhdl")
        TestRunFail(runner, "incorrect reference (name from ieee library)",
                    rule, "reference9.vhdl")
        TestRunOK(runner, "correct reference (name from standard package)",
                  rule, "reference10.vhdl")
        TestRunFail(runner, "incorrect reference (name from standard package)",
                    rule, "reference11.vhdl")
        TestRunOK(runner, "correct reference (control character name)",
                  rule, "reference12.vhdl")
        TestRunOK(runner, "correct reference (attribute)",
                  rule, "reference13.vhdl")
        TestRunFail(runner, "incorrect reference (attribute spec)",
                    rule, "reference14.vhdl")
        TestRunOK(runner, "correct reference (attribute name)",
                  rule, "reference15.vhdl")
        TestRunFail(runner, "incorrect reference (attribute name)",
                    rule, "reference16.vhdl")
        TestRunOK(runner, "reference to an entity",
                  rule, "reference17.vhdl")
        TestRunOK(runner, "architecture in an entity aspect",
                  rule, "reference18.vhdl")
        TestRunOK(runner, "unknown architecture in an entity aspect",
                  rule, "reference19.vhdl")
        TestRunFail(runner, "incorrect reference to an architecture",
                    rule, "reference20.vhdl")
