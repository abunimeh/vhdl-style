from vhdllint.syntaxrules import SyntaxRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
from vhdllint.utils import Location
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs
import libghdl.std_names as std_names
import vhdllint.utils as utils


class CheckContextClauses(SyntaxRule):
    """Check that context clauses are organized by groups.
       No library clause for 'std' or 'work'."""

    rulename = 'Context'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def check_group(self, clauses):
        lib = None
        pos = -1
        for cl in clauses:
            pos += 1
            n = cl['node']
            if cl['kind'] == 'library':
                # Check there is an empty line before.
                if pos != 0:
                    prev_line = clauses[pos - 1]['line']
                    cur_line = cl['line']
                    if prev_line >= cur_line - 1:
                        self.error(Location.from_node(n),
                                   "empty line required before library clause")
                if pos == len(clauses) - 1 \
                   or clauses[pos + 1]['kind'] == 'library':
                        self.error(Location.from_node(n),
                                   "library clause not followed by use")
                if cl['name'] == std_names.Name.Ieee and lib is not None:
                    self.error(Location.from_node(n),
                               "library for 'ieee' must be the first")
                lib = cl['name']
            elif cl['kind'] == 'use':
                if cl['library'] == std_names.Name.Std:
                    # Special case
                    if lib is not None and lib != std_names.Name.Ieee:
                        self.error(Location.from_node(n),
                                   "use for std package must be in the "
                                   "ieee group")
                    if pos < len(clauses) - 1 \
                       and clauses[pos + 1]['line'] < cl['line'] + 2:
                        self.error(Location.from_node(n),
                                   "use for std package must be followed "
                                   "by a blank line")
                    # TODO: check it doesn't appear before library ieee.
                else:
                    if lib is None:
                        self.error(Location.from_node(n),
                                   "missing library clause for use clause")
                    elif cl['library'] == std_names.Name.Work:
                        # More checks needed: should be a separate group.
                        pass
                    elif cl['library'] != lib:
                        self.error(Location.from_node(n),
                                   "use clause not below the corresponding "
                                   "library clause")

    def extract_library(self, n):
        name = iirs.Get_Identifier(n)
        if iirs.Get_Has_Identifier_List(n):
            self.error(Location.from_node(n),
                       "library must be alone")
        if name == std_names.Name.Std:
            self.error(Location.from_node(n),
                       "do not use library clause for 'std'")
        elif name == std_names.Name.Work:
            self.error(Location.from_node(n),
                       "do not use library clause for 'work'")
        loc = iirs.Get_Location(n)
        _, ln, _ = utils.Location_To_File_Line_Col(loc)
        return [{'kind': 'library',
                 'node': n,
                 'name': name,
                 'line': ln}]

    def extract_use(self, n):
        if iirs.Get_Use_Clause_Chain(n):
            self.error(Location.from_node(n),
                       "there must be an one package per use")
        name = iirs.Get_Selected_Name(n)
        if iirs.Get_Kind(name) != iirs.Iir_Kind.Selected_By_All_Name:
            self.error(Location.from_node(n),
                       "missing .all after package name")
            return []
        prefix = iirs.Get_Prefix(name)
        if iirs.Get_Kind(prefix) != iirs.Iir_Kind.Selected_Name:
            self.error(Location.from_node(n),
                       "use-d name must be a selected name")
            return []
        lib_prefix = iirs.Get_Prefix(prefix)
        if iirs.Get_Kind(lib_prefix) != iirs.Iir_Kind.Simple_Name:
            self.error(Location.from_node(n),
                       "use-d prefix name must be a simple name")
            return []
        loc = iirs.Get_Location(n)
        _, ln, _ = utils.Location_To_File_Line_Col(loc)
        return [{'kind': 'use',
                 'node': n,
                 'name': iirs.Get_Identifier(prefix),
                 'library': iirs.Get_Identifier(lib_prefix),
                 'line': ln}]

    def check(self, input, file):
        for unit in thinutils.chain_iter(iirs.Get_First_Design_Unit(file)):
            # Extract the list of clauses
            clauses = []
            for cl in thinutils.chain_iter(iirs.Get_Context_Items(unit)):
                k = iirs.Get_Kind(cl)
                if k == iirs.Iir_Kind.Library_Clause:
                    clauses.extend(self.extract_library(cl))
                elif k == iirs.Iir_Kind.Use_Clause:
                    clauses.extend(self.extract_use(cl))
                else:
                    assert False, "unknown context clause"
            if clauses:
                self.check_group(clauses)

    @staticmethod
    def test(runner):
        rule = CheckContextClauses()
        TestRunOK(runner, "File without ieee",
                  rule, "hello.vhdl")
        TestRunOK(runner, "simple use of textio",
                  rule, "contextclauses1.vhdl")
        TestRunFail(runner, "incorrect library clause for work",
                    rule, "contextclauses2.vhdl")
        TestRunFail(runner, "incorrect library clause for std",
                    rule, "contextclauses3.vhdl")
        TestRunOK(runner, "more complex example",
                  rule, "contextclauses4.vhdl")
        TestRunFail(runner, "missing empty line before library clause",
                    rule, "contextclauses5.vhdl")
        TestRunFail(runner, "multiple libraries for the same clause",
                    rule, "contextclauses6.vhdl")
