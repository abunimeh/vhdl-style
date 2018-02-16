from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs


class CheckOneUnit(SyntaxRule):
    """Check each file contains one module.

    A module is either a design unit, or an entity and its architecture, or
    an entity, its architecture and its configuration.

    :param patterns: is the list of allowed units; each letter represents
       a kind of unit:
       E: Entity, A: Architecture, P: Package, B: package Body,
       C: Configuration.
    """

    rulename = 'OneModule'

    def __init__(self, name=None, patterns=['E', 'EA', 'EAC',
                                            'A', 'P', 'PB', 'C']):
        super(self.__class__, self).__init__(name)
        self.patterns = patterns

    def check_entity(self, units):
        ent = iirs.Get_Library_Unit(units[0])
        assert iirs.Get_Kind(ent) == iirs.Iir_Kind.Entity_Declaration
        arch = iirs.Get_Library_Unit(units[1])
        if iirs.Get_Kind(arch) != iirs.Iir_Kind.Architecture_Body:
            self.error(Location.from_node(arch),
                       "second unit of a file must be an architecture")
            return
        arch_ent = iirs.Get_Entity_Name(arch)
        if iirs.Get_Kind(arch_ent) != iirs.Iir_Kind.Simple_Name:
            # Strictly speaking, a selected name is allowed.
            self.error(Location.from_node(arch_ent),
                       "weird entity name in architecture")
            return
        if iirs.Get_Identifier(arch_ent) != iirs.Get_Identifier(ent):
            self.error(Location.from_node(arch_ent),
                       "unrelated architecture after entity")
            return
        if len(units) == 2:
            return
        conf = iirs.Get_Library_Unit(units[2])
        if iirs.Get_Kind(conf) != iirs.Iir_Kind.Configuration_Declaration:
            self.error(Location.from_node(arch),
                       "third unit must be a configuration")
        # TODO: check it is related to the architecture
        if len(units) > 3:
            self.error(Location.from_node(units[3]),
                       "too many units in a file")

    def check_package(self, units):
        decl = iirs.Get_Library_Unit(units[0])
        assert iirs.Get_Kind(decl) == iirs.Iir_Kind.Package_Declaration
        bod = iirs.Get_Library_Unit(units[1])
        if iirs.Get_Kind(bod) != iirs.Iir_Kind.Package_Body:
            self.error(Location.from_node(bod),
                       "second unit of a file must be a package body")
            return
        if iirs.Get_Identifier(bod) != iirs.Get_Identifier(decl):
            self.error(Location.from_node(bod),
                       "unrelated package body after package declaration")
            return
        if len(units) > 2:
            self.error(Location.from_node(units[2]),
                       "too many units in a file")

    def check(self, input, ast):
        assert iirs.Get_Kind(ast) == iirs.Iir_Kind.Design_File
        units = thinutils.chain_to_list(iirs.Get_First_Design_Unit(ast))
        pattern = ''
        letter = {iirs.Iir_Kind.Entity_Declaration: 'E',
                  iirs.Iir_Kind.Architecture_Body: 'A',
                  iirs.Iir_Kind.Configuration_Declaration: 'C',
                  iirs.Iir_Kind.Package_Declaration: 'P',
                  iirs.Iir_Kind.Package_Body: 'B'}
        pattern = ''.join([letter[iirs.Get_Kind(iirs.Get_Library_Unit(u))]
                           for u in units])
        if pattern not in self.patterns:
            self.error(Location(input.filename),
                       "sequence of units not allowed")
        if len(units) <= 1:
            # Always ok to have one unit. Zero unit is not allowed by vhdl.
            return
        first = iirs.Get_Library_Unit(units[0])
        if iirs.Get_Kind(first) == iirs.Iir_Kind.Entity_Declaration:
            self.check_entity(units)
        elif iirs.Get_Kind(first) == iirs.Iir_Kind.Package_Declaration:
            self.check_package(units)
        else:
            self.error(Location.from_node(first),
                       "first unit must be either an entity or a package")

    @staticmethod
    def test(runner):
        rule = CheckOneUnit()
        TestRunOK(runner, "File with an entity and an architecture",
                  rule, "hello.vhdl")
        TestRunOK(runner, "File with one unit (entity)",
                  rule, "onemodule1.vhdl")
        TestRunOK(runner, "File with one unit (architecture)",
                  rule, "onemodule2.vhdl")
        TestRunFail(runner, "File with unrelated architecture",
                    rule, "onemodule3.vhdl")
        TestRunOK(runner, "File with package and its body",
                  rule, "onemodule4.vhdl")
        TestRunFail(runner, "File with package and unrelated body",
                    rule, "onemodule5.vhdl")
        TestRunFail(runner, "File two packages",
                    rule, "onemodule6.vhdl")
        TestRunFail(runner, "File more than a package and its body",
                    rule, "onemodule7.vhdl")
        TestRunOK(runner, "File with entity, arch and configuration",
                  rule, "onemodule8.vhdl")
