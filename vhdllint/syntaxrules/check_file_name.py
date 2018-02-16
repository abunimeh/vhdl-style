from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils
import os.path


class CheckFileName(SyntaxRule):
    """Check fiel name."""

    rulename = 'FileName'

    def __init__(self, name=None, extension='.vhdl'):
        super(self.__class__, self).__init__(name)
        self.extension = extension

    def check(self, input, ast):
        assert iirs.Get_Kind(ast) == iirs.Iir_Kind.Design_File
        unit = iirs.Get_First_Design_Unit(ast)
        lu = iirs.Get_Library_Unit(unit)
        s = nodeutils.get_identifier_str(lu)
        filename = s + self.extension
        if os.path.basename(input.filename) != filename:
            self.error(Location.from_node(unit),
                       "filename must be {0}".format(filename))

    @staticmethod
    def test(runner):
        rule = CheckFileName()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "File with incorrect name",
                    rule, "filename1.vhdl")
