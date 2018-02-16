from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils
import string


class CheckAttributeDecl(SyntaxNodeRule):
    """Check no user attribute declarations."""

    rulename = 'NoUserAttributes'

    def __init__(self, name=None, allowed=[]):
        """Create the rule
        :param execpt: is the list of allowed attribute.
        """
        super(self.__class__, self).__init__(name)
        self.allowed = [string.lower(attr) for attr in allowed]

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Attribute_Declaration:
            s = nodeutils.get_identifier_str(node)
            if string.lower(s) not in self.allowed:
                self.error(
                    Location.from_node(node),
                    "user attribute declaration for '{0}' not allowed".format(
                        s))

    @staticmethod
    def test(runner):
        rule = CheckAttributeDecl(allowed=['Reserved'])
        TestRunOK(runner, "File without attributes",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple attribute declaration",
                    rule, "attrdecl1.vhdl")
        TestRunOK(runner, "Allowed attribute declaration",
                  rule, "attrdecl2.vhdl")
