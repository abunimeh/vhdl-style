from vhdllint.syntaxrules import SyntaxNodeRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import vhdllint.nodeutils as nodeutils
import libghdl.elocations as elocations
import libghdl.iirs as iirs


class CheckEndLabel(SyntaxNodeRule):
    """Check no group nor group template declaration."""

    rulename = 'EndLabel'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_end(self, node, idnode):
        idn = iirs.Get_Identifier(idnode)
        if idn != 0 and not iirs.Get_End_Has_Identifier(node):
            self.error(
                Location.from_location(elocations.Get_End_Location(node)),
                "missing '{}' after 'end'".format(
                    nodeutils.get_identifier_str(idnode)))

    def check(self, input, node):
        k = iirs.Get_Kind(node)
        if k in [iirs.Iir_Kind.Entity_Declaration,
                 iirs.Iir_Kind.Package_Declaration,
                 iirs.Iir_Kind.Package_Body,
                 iirs.Iir_Kind.Architecture_Body,
                 iirs.Iir_Kind.Configuration_Declaration,
                 iirs.Iir_Kind.Protected_Type_Declaration,
                 iirs.Iir_Kind.For_Loop_Statement,
                 iirs.Iir_Kind.While_Loop_Statement,
                 iirs.Iir_Kind.Case_Statement,
                 iirs.Iir_Kind.If_Statement,
                 iirs.Iir_Kind.Block_Statement,
                 iirs.Iir_Kind.Sensitized_Process_Statement,
                 iirs.Iir_Kind.Process_Statement,
                 iirs.Iir_Kind.If_Generate_Statement,
                 iirs.Iir_Kind.For_Generate_Statement]:
            self.check_end(node, node)
        elif k in [iirs.Iir_Kind.Procedure_Body,
                   iirs.Iir_Kind.Function_Body]:
            idnode = iirs.Get_Subprogram_Specification(node)
            self.check_end(node, idnode)
        elif k == iirs.Iir_Kind.Type_Declaration:
            df = iirs.Get_Type_Definition(node)
            if iirs.Get_Kind(df) in [iirs.Iir_Kind.Physical_Type_Definition,
                                     iirs.Iir_Kind.Record_Type_Definition]:
                self.check_end(df, node)

    @staticmethod
    def test(runner):
        rule = CheckEndLabel()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Simple entity without end label",
                    rule, "endlabel1.vhdl")
