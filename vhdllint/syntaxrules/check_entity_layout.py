from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import vhdllint.utils as utils
from vhdllint.utils import Location
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.elocations as elocations


class CheckEntityLayout(SyntaxRule):
    """Check layout of entity declarations.
       Ports and generics must be declared one per line,
       name, ':', subtype indication and ':=' must be aligned."""

    rulename = 'EntityLayout'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_declarations(self, decl):
        decl_col = -1
        colon_col = -1
        subtype_col = -1
        assign_col = -1
        line = -1
        while decl != thin.Null_Iir:
            loc = elocations.Get_Start_Location(decl)
            fe, ln, co = utils.Location_To_File_Line_Col(loc)
            if ln <= line:
                self.error(Location.from_node(decl),
                           "one generic/port per line")
            else:
                if co != decl_col and decl_col >= 0:
                    self.error(Location.from_node(decl),
                               "name is not aligned with previous one")

                # Check alignment of ':'
                colon_loc = elocations.Get_Colon_Location(decl)
                _, ln1, colon_co = utils.Location_To_File_Line_Col(colon_loc)
                if colon_co != colon_col and colon_col >= 0:
                    self.error(Location.from_node(decl),
                               "':' is not aligned with previous one")
                colon_col = colon_co

                # Check alignment of subtype.
                st = iirs.Get_Subtype_Indication(decl)
                if st != thin.Null_Iir:
                    st_loc = thinutils.leftest_location(st)
                    _, ln1, st_co = utils.Location_To_File_Line_Col(st_loc)
                    if st_co != subtype_col and subtype_col >= 0:
                        self.error(Location.from_node(decl),
                                   "subtype is not aligned with previous one")
                    subtype_col = st_co

                # Check alignment of ':='
                assign_loc = elocations.Get_Assign_Location(decl)
                if assign_loc != thin.No_Location:
                    _, ln1, assign_co = \
                        utils.Location_To_File_Line_Col(assign_loc)
                    if assign_co != assign_col and assign_col >= 0:
                        self.error(Location.from_node(decl),
                                   "':=' is not aligned with previous one")
                    assign_col = assign_co
            decl_col = co
            line = ln
            decl = iirs.Get_Chain(decl)

    def check(self, input, ast):
        for du in thinutils.chain_iter(iirs.Get_First_Design_Unit(ast)):
            ent = iirs.Get_Library_Unit(du)
            if iirs.Get_Kind(ent) != iirs.Iir_Kind.Entity_Declaration:
                continue
            gen = iirs.Get_Generic_Chain(ent)
            if gen != thin.Null_Iir:
                self.check_declarations(gen)
            ports = iirs.Get_Port_Chain(ent)
            if ports != thin.Null_Iir:
                self.check_declarations(ports)
                port = ports
                while port != thin.Null_Iir:
                    if not iirs.Get_Has_Mode(port):
                        self.error(Location.from_node(port),
                                   "in/out/inout required for port")
                    port = iirs.Get_Chain(port)

    @staticmethod
    def test(runner):
        rule = CheckEntityLayout()
        TestRunOK(runner, "arch without instantiation",
                  rule, "hello.vhdl")
        TestRunOK(runner, "Simple entity",
                  rule, "entitylayout1.vhdl")
        TestRunFail(runner, "':=' not correctly aligned",
                    rule, "entitylayout2.vhdl")
        TestRunFail(runner, "':' not correctly aligned",
                    rule, "entitylayout3.vhdl")
        TestRunFail(runner, "subtype not correctly aligned",
                    rule, "entitylayout4.vhdl")
        TestRunFail(runner, "identifier list",
                    rule, "entitylayout5.vhdl")
        TestRunFail(runner, "missing mode for port",
                    rule, "entitylayout6.vhdl")
        TestRunOK(runner, "Simple entity with a bit_vector",
                  rule, "entitylayout7.vhdl")
