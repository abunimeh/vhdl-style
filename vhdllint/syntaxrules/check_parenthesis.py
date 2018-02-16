from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.elocations as elocations


class CheckParenthesis(SyntaxNodeRule):
    """Check for useless parenthesis."""

    rulename = 'Parenthesis'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_parenthesis(self, expr):
        if expr == thin.Null_Iir:
            # For else clause.
            return
        if iirs.Get_Kind(expr) != iirs.Iir_Kind.Parenthesis_Expression:
            return
        left_loc = iirs.Get_Location(expr)
        right_loc = elocations.Get_Right_Paren_Location(expr)
        fe = thin.Location_To_File(left_loc)
        assert fe == thin.Location_To_File(right_loc)
        left_line = thin.Location_File_To_Line(left_loc, fe)
        right_line = thin.Location_File_To_Line(right_loc, fe)
        if left_line != right_line:
            # Assume that's for grouping
            return
        self.error(Location.from_node(expr),
                   "useless parenthesis around expression")

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k in [iirs.Iir_Kind.If_Statement,
                 iirs.Iir_Kind.Elsif,
                 iirs.Iir_Kind.While_Loop_Statement,
                 iirs.Iir_Kind.Exit_Statement,
                 iirs.Iir_Kind.Next_Statement,
                 iirs.Iir_Kind.If_Generate_Statement,
                 iirs.Iir_Kind.If_Generate_Else_Clause,
                 iirs.Iir_Kind.Conditional_Waveform,
                 iirs.Iir_Kind.Conditional_Expression]:
            self.check_parenthesis(iirs.Get_Condition(node))
        elif k in [iirs.Iir_Kind.Case_Generate_Statement,
                   iirs.Iir_Kind.Case_Statement,
                   iirs.Iir_Kind.Concurrent_Selected_Signal_Assignment,
                   iirs.Iir_Kind.Selected_Waveform_Assignment_Statement,
                   iirs.Iir_Kind.Return_Statement]:
            self.check_parenthesis(iirs.Get_Expression(node))

    @staticmethod
    def test(runner):
        rule = CheckParenthesis()
        TestRunOK(runner, "File without ports",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Useless parenthesis for if",
                    rule, "paren1.vhdl")
        TestRunOK(runner, "if statement",
                  rule, "paren2.vhdl")
        TestRunOK(runner, "if statement with a very long condition",
                  rule, "paren3.vhdl")
        TestRunOK(runner, "Return statement without parenthesis",
                  rule, "paren4.vhdl")
        TestRunFail(runner, "Useless parenthesis for return",
                    rule, "paren5.vhdl")
