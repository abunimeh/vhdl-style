from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location, Location_To_File_Line_Col
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocations


class CheckSubprgIsLayout(SyntaxRule):
    """Check location of `is` in subprogram bodies: must be on the same column
       as function/procedure if there are declarations."""

    rulename = 'SubprgIsLayout'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check(self, input, ast):
        for node in thinutils.constructs_iter(ast):
            k = iirs.Get_Kind(node)
            if k not in iirs.Iir_Kinds.Subprogram_Body:
                continue
            if iirs.Get_Declaration_Chain(node) == thin.Null_Iir:
                continue
            is_loc = elocations.Get_Is_Location(node)
            is_file, is_ln, is_col = Location_To_File_Line_Col(is_loc)
            beg_loc = elocations.Get_Begin_Location(node)
            beg_file, beg_line, beg_col = Location_To_File_Line_Col(beg_loc)
            if is_col != beg_col:
                self.error(
                    Location.from_location(is_loc),
                    "'is' and 'begin' must be on the same column")

    @staticmethod
    def test(runner):
        rule = CheckSubprgIsLayout()
        TestRunOK(runner, "correct column for 'is' in procedure body",
                  rule, "subprgislayout1.vhdl")
        TestRunFail(runner, "bad column for 'is' in procedure body",
                    rule, "subprgislayout2.vhdl")
