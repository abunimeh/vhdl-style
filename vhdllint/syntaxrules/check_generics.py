from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import vhdllint.nodeutils as nodeutils


class CheckGenerics(SyntaxNodeRule):
    """Check names of generics."""

    rulename = 'GenericsName'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, node):
        if nodeutils.is_generic(node):
            s = nodeutils.get_identifier_str(node)
            if not s.startswith("g_"):
                self.error(Location.from_node(node),
                           "generic '{0}' must start with 'g_'".format(s))
            if not s[2:].isupper():
                self.error(
                    Location.from_node(node),
                    "generic '{0}' must be in upper case after 'g_'".format(s))

    @staticmethod
    def test(runner):
        rule = CheckGenerics()
        TestRunOK(runner, "File without generics",
                  rule, "hello.vhdl")
        TestRunOK(runner, "correct generic",
                  rule, "generic1.vhdl")
        TestRunFail(runner, "generic not in upper case",
                    rule, "generic2.vhdl")
        TestRunFail(runner, "generic without 'g_' prefix",
                    rule, "generic3.vhdl")
