from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils


class CheckProcessLabel(SyntaxRule):
    """Check each process has either a label or a preceeding comment."""

    rulename = 'ProcessLabel'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, ast):
        for node in thinutils.concurrent_stmts_iter(ast):
            if iirs.Get_Kind(node) not in iirs.Iir_Kinds.Process_Statement:
                continue
            if iirs.Get_Label(node) != thin.Null_Identifier:
                continue
            loc = iirs.Get_Location(node)
            fil = thin.Location_To_File(loc)
            line = thin.Location_File_To_Line(loc, fil)
            if input.comments.get(line - 1, None) is None:
                self.error(
                    Location.from_node(node),
                    "missing label or comment for process")

    @staticmethod
    def test(runner):
        rule = CheckProcessLabel()
        TestRunFail(runner, "Process without label",
                    rule, "hello.vhdl")
        TestRunOK(runner, "Process with a label",
                  rule, "processlabel1.vhdl")
        TestRunOK(runner, "Process with a comment",
                  rule, "processlabel2.vhdl")
        TestRunFail(runner, "Process without a comment",
                    rule, "processlabel3.vhdl")
