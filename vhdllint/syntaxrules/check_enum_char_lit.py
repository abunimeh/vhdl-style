from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.std_names as std_names


class CheckEnumCharLit(SyntaxNodeRule):
    """Check no character for enumeration literal."""

    rulename = 'NoCharEnumLit'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Enumeration_Literal:
            if iirs.Get_Identifier(node) <= std_names.Name.Last_Character:
                self.error(
                    Location.from_node(node),
                    "character not allowed in enumeration declaration")

    @staticmethod
    def test(runner):
        rule = CheckEnumCharLit()
        TestRunOK(runner, "File without attributes",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Enumerated type with character",
                    rule, "enumcharlit1.vhdl")
