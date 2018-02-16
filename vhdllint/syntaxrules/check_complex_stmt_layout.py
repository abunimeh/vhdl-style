from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocs
import vhdllint.utils as utils


class CheckComplexStmtLayout(SyntaxRule):
    """Check complex statement layout:
       'then' must be either on the same line or same column as 'if'/'elsif',
       'loop' must be on the same line or same column as 'for'/'while',
       'is' must be on the same line as 'case',
       'generate' must be on the same line or column as 'if'/'for'."""

    rulename = 'ComplexStmtLayout'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def chk_line_or_col(self, n, def_loc, loc):
        fe = thin.Location_To_File(def_loc)
        l_fe = thin.Location_To_File(loc)
        assert fe == l_fe, "non-matching file location {} vs {}".format(
            def_loc, loc)
        def_line = thin.Location_File_To_Line(def_loc, fe)
        line = thin.Location_File_To_Line(loc, fe)
        if line == def_line:
            return
        def_col = thin.Location_File_Line_To_Col(def_loc, fe, def_line)
        col = thin.Location_File_Line_To_Col(loc, fe, line)
        if def_col != col:
            self.error(
                utils.Location.from_location(loc),
                "indentation: must be at col {} instead of {}".format(
                    def_col, col))

    def chk_if_stmt(self, n):
        while n != thin.Null_Iir:
            loc = iirs.Get_Location(n)
            then_loc = elocs.Get_Then_Location(n)
            if then_loc != 0:
                self.chk_line_or_col(n, loc, then_loc)
            n = iirs.Get_Else_Clause(n)

    def check(self, input, ast):
        for n in thinutils.constructs_iter(ast):
            k = iirs.Get_Kind(n)
            if k in iirs.Iir_Kinds.Subprogram_Body \
               or k in iirs.Iir_Kinds.Process_Statement:
                for n1 in thinutils.sequential_iter(n):
                    k = iirs.Get_Kind(n1)
                    if k == iirs.Iir_Kind.If_Statement:
                        self.chk_if_stmt(n1)
                    elif (k == iirs.Iir_Kind.For_Loop_Statement
                          or k == iirs.Iir_Kind.While_Loop_Statement):
                        self.chk_line_or_col(
                            n1, iirs.Get_Location(n1),
                            elocs.Get_Loop_Location(n1))
                    elif k == iirs.Iir_Kind.Case_Statement:
                        pass
            elif k == iirs.Iir_Kind.For_Generate_Statement:
                self.chk_line_or_col(
                    n, iirs.Get_Location(n), elocs.Get_Generate_Location(n))
            elif k == iirs.Iir_Kind.If_Generate_Statement:
                self.chk_line_or_col(
                    n, iirs.Get_Location(n), elocs.Get_Generate_Location(n))

    @staticmethod
    def test(runner):
        rule = CheckComplexStmtLayout()
        TestRunOK(runner, "Simple file",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Simple if statement",
                  rule, "complexstmtlayout1.vhdl")
        TestRunFail(runner, "Incorrect if statement",
                    rule, "complexstmtlayout2.vhdl")
        TestRunFail(runner, "Incorrect if statement (elsif)",
                    rule, "complexstmtlayout3.vhdl")
        TestRunOK(runner, "Simple for statement",
                  rule, "complexstmtlayout4.vhdl")
        TestRunOK(runner, "Simple for statement (different line)",
                  rule, "complexstmtlayout5.vhdl")
        TestRunFail(runner, "Incorrect for statement",
                    rule, "complexstmtlayout6.vhdl")
        TestRunOK(runner, "Simple while statement",
                  rule, "complexstmtlayout7.vhdl")
        TestRunFail(runner, "Incorrect while statement",
                    rule, "complexstmtlayout8.vhdl")
        TestRunFail(runner, "Incorrect for-generate statement",
                    rule, "complexstmtlayout9.vhdl")
        TestRunFail(runner, "Incorrect if-generate statement",
                    rule, "complexstmtlayout10.vhdl")
        TestRunOK(runner, "Correct case statement",
                  rule, "complexstmtlayout11.vhdl")
