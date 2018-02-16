from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocs
import vhdllint.utils as utils
import vhdllint.nodeutils as nodeutils


class CheckIndent(SyntaxRule):
    """Check indentation."""

    rulename = 'Indentation'

    def __init__(self, name=None, level=2):
        super(self.__class__, self).__init__(name)
        self._l = level

    def chk_level(self, n, loc, level):
        if loc == thin.No_Location:
            return
        fe = thin.Location_To_File(loc)
        line = thin.Location_File_To_Line(loc, fe)
        col = thin.Location_File_Line_To_Col(loc, fe, line)
        if col != level:
            self.error(
                utils.Location.from_location(loc),
                "indentation: must be at col {} instead of {}".format(
                    level, col))
            # thin.Disp_Iir(n, 0, 1)

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

    def chk_case_alternatives(self, alt, level):
        when_loc = None
        while alt != thin.Null_Iir:
            alt_loc = iirs.Get_Location(alt)
            if not iirs.Get_Same_Alternative_Flag(alt):
                # Indentation of 'when'
                when_loc = alt_loc
                self.chk_level(alt, alt_loc, level)
                stmts = iirs.Get_Associated_Chain(alt)
                if nodeutils.is_one_stmt(stmts) \
                   and nodeutils.is_same_line(iirs.Get_Location(stmts),
                                              alt_loc):
                    # This is ok (providing this is a simple statement...)
                    # TODO
                    pass
                else:
                    self.chk_sequential(stmts, level + self._l)
            elif not nodeutils.is_same_line(alt_loc, when_loc):
                self.chk_level(alt, alt_loc, level + 3)
            alt = iirs.Get_Chain(alt)

    def chk_if_stmt(self, n, level):
        nlevel = level + self._l
        while n != thin.Null_Iir:
            # if/else/elsif
            loc = iirs.Get_Location(n)
            self.chk_level(n, loc, level)
            # then
            then_loc = elocs.Get_Then_Location(n)
            if then_loc != 0:
                self.chk_line_or_col(n, loc, then_loc)
            self.chk_sequential(iirs.Get_Sequential_Statement_Chain(n), nlevel)
            self.chk_level(n, elocs.Get_End_Location(n), level)
            n = iirs.Get_Else_Clause(n)

    def chk_if_set(self, n, level):
        if n == thin.Null_Iir:
            return
        self.chk(n, level)

    def chk_context_clauses(self, parent, level):
        for n in thinutils.chain_iter(iirs.Get_Context_Items(parent)):
            k = iirs.Get_Kind(n)
            if k == iirs.Iir_Kind.Library_Clause:
                self.chk_level(n, elocs.Get_Start_Location(n), level)
                # Check: same line for next clauses
            elif k == iirs.Iir_Kind.Use_Clause:
                self.chk_level(n, iirs.Get_Location(n), level)
                # Check: same line for next clauses
            else:
                assert False, "unhandled context clause"

    def chk_library_unit(self, n, level):
        k = iirs.Get_Kind(n)
        nlevel = level + self._l
        self.chk_level(n, elocs.Get_Start_Location(n), level)
        if k == iirs.Iir_Kind.Package_Declaration \
           or k == iirs.Iir_Kind.Package_Body:
            self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
        elif k == iirs.Iir_Kind.Entity_Declaration:
            self.chk_level(n, elocs.Get_Generic_Location(n), nlevel)
            self.chk_level(n, elocs.Get_Port_Location(n), nlevel)
            self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
            self.chk_level(n, elocs.Get_Begin_Location(n), level)
            self.chk_concurrent(iirs.Get_Concurrent_Statement_Chain(n), nlevel)
        elif k == iirs.Iir_Kind.Architecture_Body:
            self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
            self.chk_level(n, elocs.Get_Begin_Location(n), level)
            self.chk_concurrent(iirs.Get_Concurrent_Statement_Chain(n), nlevel)
        elif k == iirs.Iir_Kind.Configuration_Declaration:
            self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
            # TODO: block configuration
        else:
            assert False, "unhandled unit {}".format(thinutils.kind_image(k))
        self.chk_level(n, elocs.Get_End_Location(n), level)

    def chk_declarations(self, head, level):
        nlevel = level + self._l
        for n in thinutils.chain_iter(head):
            k = iirs.Get_Kind(n)
            if k == iirs.Iir_Kind.Constant_Declaration \
               or k == iirs.Iir_Kind.Signal_Declaration \
               or k == iirs.Iir_Kind.Variable_Declaration \
               or k == iirs.Iir_Kind.File_Declaration \
               or k == iirs.Iir_Kind.Object_Alias_Declaration \
               or k == iirs.Iir_Kind.Attribute_Declaration \
               or k == iirs.Iir_Kind.Attribute_Specification:
                self.chk_level(n, elocs.Get_Start_Location(n), level)
            elif (k == iirs.Iir_Kind.Configuration_Specification
                  or k == iirs.Iir_Kind.Disconnection_Specification):
                self.chk_level(n, iirs.Get_Location(n), level)
            elif (k == iirs.Iir_Kind.Subtype_Declaration
                  or k == iirs.Iir_Kind.Type_Declaration
                  or k == iirs.Iir_Kind.Anonymous_Type_Declaration):
                self.chk_level(n, elocs.Get_Start_Location(n), level)
            elif k == iirs.Iir_Kind.Component_Declaration:
                self.chk_level(n, elocs.Get_Start_Location(n), level)
                self.chk_level(n, elocs.Get_Generic_Location(n), nlevel)
                self.chk_level(n, elocs.Get_Port_Location(n), nlevel)
                self.chk_level(n, elocs.Get_End_Location(n), level)
            elif (k == iirs.Iir_Kind.Function_Declaration
                  or k == iirs.Iir_Kind.Procedure_Declaration):
                self.chk_level(n, elocs.Get_Start_Location(n), level)
            elif (k == iirs.Iir_Kind.Function_Body
                  or k == iirs.Iir_Kind.Procedure_Body):
                self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_Begin_Location(n), level)
                self.chk_sequential(
                    iirs.Get_Sequential_Statement_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_End_Location(n), level)
                # check start
            elif k == iirs.Iir_Kind.Use_Clause:
                self.chk_level(n, iirs.Get_Location(n), level)
            else:
                assert False, "unhandled declaration {}".format(
                    thinutils.kind_image(k))

    def chk_generate_body(self, bod, level):
        nlevel = level + self._l
        assert iirs.Get_Kind(bod) == iirs.Iir_Kind.Generate_Statement_Body
        self.chk_concurrent(iirs.Get_Concurrent_Statement_Chain(bod), nlevel)

    def chk_concurrent(self, head, level):
        nlevel = level + self._l
        for n in thinutils.chain_iter(head):
            self.chk_level(n, iirs.Get_Location(n), level)
            k = iirs.Get_Kind(n)
            if k == iirs.Iir_Kind.Component_Instantiation_Statement:
                # TODO
                pass
            elif (k == iirs.Iir_Kind.Concurrent_Assertion_Statement
                  or k == iirs.Iir_Kind.Concurrent_Simple_Signal_Assignment
                  or k ==
                    iirs.Iir_Kind.Concurrent_Conditional_Signal_Assignment
                  or k == iirs.Iir_Kind.Concurrent_Selected_Signal_Assignment):
                pass
            elif k == iirs.Iir_Kind.Concurrent_Procedure_Call_Statement:
                pass
            elif k == iirs.Iir_Kind.Block_Statement:
                self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_Begin_Location(n), level)
                self.chk_concurrent(
                    iirs.Get_Concurrent_Statement_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_End_Location(n), level)
            elif k == iirs.Iir_Kind.For_Generate_Statement:
                self.chk_line_or_col(
                    n, iirs.Get_Location(n), elocs.Get_Generate_Location(n))
                self.chk_generate_body(
                    iirs.Get_Generate_Statement_Body(n), level)
                self.chk_level(n, elocs.Get_End_Location(n), level)
            elif k == iirs.Iir_Kind.If_Generate_Statement:
                self.chk_line_or_col(
                    n, iirs.Get_Location(n), elocs.Get_Generate_Location(n))
                self.chk_generate_body(
                    iirs.Get_Generate_Statement_Body(n), level)
                self.chk_level(n, elocs.Get_End_Location(n), level)
            elif (k == iirs.Iir_Kind.Sensitized_Process_Statement
                  or k == iirs.Iir_Kind.Process_Statement):
                self.chk_declarations(iirs.Get_Declaration_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_Begin_Location(n), level)
                self.chk_sequential(
                    iirs.Get_Sequential_Statement_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_End_Location(n), level)

    def chk_sequential(self, head, level):
        nlevel = level + self._l
        for n in thinutils.chain_iter(head):
            k = iirs.Get_Kind(n)
            self.chk_level(n, iirs.Get_Location(n), level)
            if k == iirs.Iir_Kind.If_Statement:
                self.chk_if_stmt(n, level)
            elif (k == iirs.Iir_Kind.For_Loop_Statement
                  or k == iirs.Iir_Kind.While_Loop_Statement):
                self.chk_line_or_col(
                    n, iirs.Get_Location(n), elocs.Get_Loop_Location(n))
                self.chk_sequential(
                    iirs.Get_Sequential_Statement_Chain(n), nlevel)
                self.chk_level(n, elocs.Get_End_Location(n), level)
            elif k == iirs.Iir_Kind.Case_Statement:
                alts = iirs.Get_Case_Statement_Alternative_Chain(n)
                self.chk_case_alternatives(alts, nlevel)
            elif (k == iirs.Iir_Kind.Wait_Statement
                  or k == iirs.Iir_Kind.Return_Statement
                  or k == iirs.Iir_Kind.Assertion_Statement
                  or k == iirs.Iir_Kind.Report_Statement
                  or k == iirs.Iir_Kind.Procedure_Call_Statement
                  or k == iirs.Iir_Kind.Null_Statement
                  or k == iirs.Iir_Kind.Exit_Statement
                  or k == iirs.Iir_Kind.Next_Statement):
                pass
            elif (k == iirs.Iir_Kind.Simple_Signal_Assignment_Statement
                  or k == iirs.Iir_Kind.Variable_Assignment_Statement):
                pass
            else:
                assert False, "Indent: unhandled node {}".format(
                    thinutils.kind_image(k))

    def check(self, input, ast):
        assert iirs.Get_Kind(ast) == iirs.Iir_Kind.Design_File
        for u in thinutils.chain_iter(iirs.Get_First_Design_Unit(ast)):
            self.chk_context_clauses(u, 1)
            lib_unit = iirs.Get_Library_Unit(u)
            self.chk_library_unit(lib_unit, 1)

    @staticmethod
    def test(runner):
        rule = CheckIndent()
        TestRunOK(runner, "Simple file",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Incorrect generic indentation",
                    rule, "indent1.vhdl")
        TestRunFail(runner, "Incorrect port indentation",
                    rule, "indent2.vhdl")
        TestRunOK(runner, "Case statement",
                  rule, "indent3.vhdl")
        TestRunFail(runner, "Type declaration",
                    rule, "indent4.vhdl")
        TestRunFail(runner, "Alias declaration",
                    rule, "indent5.vhdl")
        TestRunFail(runner, "Attribute declaration",
                    rule, "indent6.vhdl")
        TestRunOK(runner, "Attribute declaration and spec",
                  rule, "indent7.vhdl")
        TestRunFail(runner, "Attribute specification",
                    rule, "indent8.vhdl")
        TestRunFail(runner, "Use clause",
                    rule, "indent9.vhdl")
        TestRunFail(runner, "Configuration specification",
                    rule, "indent10.vhdl")
        TestRunFail(runner, "Disconnection specification",
                    rule, "indent11.vhdl")
