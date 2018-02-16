from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils


class CheckEnum(SyntaxNodeRule):
    """Check names of enumeration literals."""

    rulename = 'EnumName'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Enumeration_Literal:
            s = nodeutils.get_identifier_str(node)
            if not s.isupper():
                self.error(
                    Location.from_node(node),
                    "enumeration literal '{0}' must be in upper case".format(
                        s))

    @staticmethod
    def test(runner):
        rule = CheckEnum()
        TestRunOK(runner, "File without enum",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Simple enum",
                  rule, "enum1.vhdl")
        TestRunFail(runner, "Simple enum with incorrect case",
                    rule, "enum2.vhdl")
