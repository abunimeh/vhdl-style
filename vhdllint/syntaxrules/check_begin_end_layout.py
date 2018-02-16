from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location, Location_To_File_Line_Col
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocations


class CheckBeginEndLayout(SyntaxRule):
    """Check each process has either a label or a preceeding comment."""

    rulename = 'BeginEndLayout'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, ast):
        for node in thinutils.constructs_iter(ast):
            k = iirs.Get_Kind(node)
            if k not in [iirs.Iir_Kind.Architecture_Body,
                         iirs.Iir_Kind.Block_Statement,
                         iirs.Iir_Kind.Entity_Declaration,
                         iirs.Iir_Kind.Generate_Statement_Body,
                         iirs.Iir_Kind.Process_Statement,
                         iirs.Iir_Kind.Sensitized_Process_Statement,
                         iirs.Iir_Kind.Procedure_Body,
                         iirs.Iir_Kind.Function_Body]:
                continue
            beg_loc = elocations.Get_Begin_Location(node)
            end_loc = elocations.Get_End_Location(node)
            if beg_loc == thin.No_Location or end_loc == thin.No_Location:
                continue
            beg_file, beg_line, beg_col = Location_To_File_Line_Col(beg_loc)
            end_file, end_line, end_col = Location_To_File_Line_Col(end_loc)
            if end_col != beg_col:
                self.error(
                    Location.from_location(end_loc),
                    "'begin' and 'end' must be aligned on the same column")
            if k in iirs.Iir_Kinds.Subprogram_Body:
                if iirs.Get_Declaration_Chain(node) != thin.Null_Iir:
                    is_loc = elocations.Get_Is_Location(node)
                    is_file, is_ln, is_col = Location_To_File_Line_Col(is_loc)
                    if is_col != beg_col:
                        self.error(
                            Location.from_location(is_loc),
                            "'is' and 'begin' must be on the same column")

    @staticmethod
    def test(runner):
        rule = CheckBeginEndLayout()
        TestRunOK(runner, "Process without label",
                  rule, "hello.vhdl")
        TestRunOK(runner, "'begin' in entity",
                  rule, "beginendlayout1.vhdl")
        TestRunFail(runner, "unaligned 'begin' in entity",
                    rule, "beginendlayout2.vhdl")
        TestRunFail(runner, "unaligned 'begin' in architecture",
                    rule, "beginendlayout3.vhdl")
        TestRunFail(runner, "unaligned 'begin' in block",
                    rule, "beginendlayout4.vhdl")
        TestRunFail(runner, "unaligned 'begin' in process",
                    rule, "beginendlayout6.vhdl")
        TestRunFail(runner, "unaligned 'begin' in function body",
                    rule, "beginendlayout7.vhdl")
        TestRunFail(runner, "unaligned 'begin' in procedure body",
                    rule, "beginendlayout8.vhdl")
        TestRunFail(runner, "bad column for 'is' in procedure body",
                    rule, "beginendlayout9.vhdl")
