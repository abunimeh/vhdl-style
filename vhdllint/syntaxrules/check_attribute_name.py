from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils
import string


class CheckAttributeName(SyntaxNodeRule):
    """Check no user attribute name.

       This is a syntax rule, so predefined attribute names are not separated
       from user ones, but this check can be applied on a single file.
    """

    rulename = 'NoUserAttrName'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)
        # Some reserved attributes, to be completed ?
        self.predefined = ['length', 'left', 'right', 'low', 'high', 'range',
                           'reverse_range', 'ascending', 'pos', 'val',
                           'image', 'value',
                           'event', 'delayed', 'stable', 'quiet']

    def check(self, input, node):
        if iirs.Get_Kind(node) == iirs.Iir_Kind.Attribute_Name:
            s = nodeutils.get_identifier_str(node)
            if string.lower(s) not in self.predefined:
                self.error(
                    Location.from_node(node),
                    "attribute name '{0}' not allowed".format(
                        s))

    @staticmethod
    def test(runner):
        rule = CheckAttributeName()
        TestRunOK(runner, "File without attributes",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple attribute name",
                    rule, "attrname1.vhdl")
        TestRunOK(runner, "Predefined attribute name",
                  rule, "attrname2.vhdl")
