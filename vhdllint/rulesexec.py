import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.tokens as tokens
import libghdl.iirs as iirs
from utils import Location, TokLocation, fatal
from filerules import FileRule
from lexrules import LexRule
from syntaxrules import SyntaxRule, SyntaxNodeRule
from semrules import SemRule, SemNodeRule
from synthrules import SynthesisRule
import ctypes
import os.path
import sys


class RuleInput(object):
    def __init__(self, filename, fe):
        self.filename = filename
        self.fe = fe                # File entry
        self.filebuf = None
        self.ast = None
        self.units_ast = []         # List of units
        self.properties = []        # List of properties (from cmd line)
        self.comments = {}          # Comments indexed by line number


class RulesExec(object):
    def __init__(self, quiet=False):
        self._quiet = quiet
        self._file_rules = []
        self._lex_rules = []
        self._syntax_rules = []
        self._syntax_node_rules = []
        self._sem_rules = []
        self._sem_node_rules = []
        self._synth_rules = []
        self._nbr_errors = 0
        self._nbr_files = 0

    def add(self, rule):
        """Add a rule"""
        if isinstance(rule, FileRule):
            self._file_rules.append(rule)
        elif isinstance(rule, LexRule):
            self._lex_rules.append(rule)
        elif isinstance(rule, SyntaxRule):
            self._syntax_rules.append(rule)
        elif isinstance(rule, SyntaxNodeRule):
            self._syntax_node_rules.append(rule)
        elif isinstance(rule, SemRule):
            self._sem_rules.append(rule)
        elif isinstance(rule, SemNodeRule):
            self._sem_node_rules.append(rule)
        elif isinstance(rule, SynthesisRule):
            self._synth_rules.append(rule)
        else:
            fatal("unknown class for rule {0}".format(rule.rulename))
        rule.set_runner(self)

    def get_nbr_errors(self):
        return self._nbr_errors

    def get_nbr_files(self):
        return self._nbr_files

    def error(self, msg):
        self._nbr_errors += 1
        if not self._quiet:
            sys.stderr.write(msg)

    def execute(self, files):
        inputs = []
        props = ['synth']
        # First file
        for filename in files:
            if filename.startswith('--'):
                # Handle properties
                if filename == '--import':
                    props = ['import']
                elif filename == '--synth':
                    props = ['synth']
                elif filename == '--top':
                    props = ['synth', 'top']
                elif filename == '--tb':
                    props = ['tb']
                else:
                    fatal("unknown property '{0}'".format(filename))
                continue

            # Read the file
            fid = thin.Get_Identifier(filename.encode('utf-8'))
            fe = thin.Read_Source_File(0, fid)
            if fe == thin.No_Source_File_Entry:
                fatal('cannot open {0}'.format(filename))

            fbuf = thin.Get_File_Buffer(fe)
            flen = thin.Get_File_Length(fe)

            # Not very efficient (it copies the string), but let's use it
            # for now.
            filebuf = ctypes.string_at(fbuf, flen)

            input = RuleInput(filename, fe)
            input.filebuf = filebuf
            input.props = props
            inputs.append(input)

            if 'import' not in input.props:
                self._nbr_files += 1

                # Again, not very efficient (creates the substrings).
                flines = filebuf.splitlines(True)

                loc = Location(filename)
                for r in self._file_rules:
                    r.check(loc, flines)

        # Then tokens
        thin.Scanner.Flag_Comment.value = True
        for input in inputs:
            if 'import' not in input.props:
                thin.Scanner.Set_File(input.fe)
                filebuf = input.filebuf
                while True:
                    thin.Scanner.Scan()
                    tok = thin.Scanner.Current_Token.value
                    loc = TokLocation(input.filename,
                                      thin.Scanner.Get_Current_Line(),
                                      thin.Scanner.Get_Token_Column(),
                                      thin.Scanner.Get_Token_Position(),
                                      thin.Scanner.Get_Position())
                    if tok == tokens.Tok.Comment:
                        input.comments[loc.line] = (loc.start, loc.end)
                    for r in self._lex_rules:
                        r.check(loc, filebuf, tok)
                    if tok == tokens.Tok.Eof:
                        break
                thin.Scanner.Close_File()
        if not (self._syntax_rules or self._syntax_node_rules
                or self._sem_rules or self._sem_node_rules
                or self._synth_rules):
            return

        # Then syntax
        # The parser doesn't handle comments
        thin.Scanner.Flag_Comment.value = False
        # Keep extra locations
        thin.Flags.Flag_Elocations.value = True
        # Keep all parenthesis
        thin.Parse.Flag_Parse_Parenthesis.value = True
        # Be sure to initialize std and work (and only once).
        # Humm, not very elegant.
        if thin.Get_Libraries_Chain() == thin.Null_Iir:
            thin.analyze_init()
        for input in inputs:
            thin.Scanner.Set_File(input.fe)
            loc = Location(input.filename)
            input.ast = thin.Parse.Parse_Design_File()
            if 'import' not in input.props:
                for r in self._syntax_rules:
                    r.check(input, input.ast)
                if self._syntax_node_rules:
                    for n in thinutils.nodes_iter(input.ast):
                        for r in self._syntax_node_rules:
                            r.check(loc, n)
            thin.Scanner.Close_File()

        # Then semantic
        if self._sem_rules or self._sem_node_rules or self._synth_rules:
            # Reduce Canon
            thin.Canon.Flag_Concurrent_Stmts.value = False
            thin.Canon.Flag_Configurations.value = False
            thin.Canon.Flag_Associations.value = False
            # First add all units in the work library, so that they they are
            # known by the analyzer.
            for input in inputs:
                unit_ast = iirs.Get_First_Design_Unit(input.ast)
                while unit_ast != thin.Null_Iir:
                    # Detach the unit from its design file
                    next_unit_ast = iirs.Get_Chain(unit_ast)
                    iirs.Set_Chain(unit_ast, thin.Null_Iir)
                    # Add
                    thin.Add_Design_Unit_Into_Library(unit_ast, False)
                    input.units_ast.append(unit_ast)
                    unit_ast = next_unit_ast
            # Handle all unit
            for input in inputs:
                if 'import' not in input.props:
                    for unit in input.units_ast:
                        if iirs.Get_Library_Unit(unit) == thin.Null_Iir:
                            # Over-written.
                            # FIXME: remove from the list ?
                            continue
                        # Be sure the unit was analyzed. It could have been
                        # already analyzed if referenced. And a unit cannot be
                        # analyzed twice.
                        if iirs.Get_Date_State(unit) == iirs.Date_State.Parse:
                            thin.Finish_Compilation(unit, False)
                            iirs.Set_Date_State(unit, iirs.Date_State.Analyze)
                        for r in self._sem_rules:
                            r.check(input, unit)
                        for n in thinutils.nodes_iter(unit):
                            for r in self._sem_node_rules:
                                r.check(input, n)

            for input in inputs:
                if 'synth' in input.props:
                    for unit in input.units_ast:
                        if iirs.Get_Library_Unit(unit) == thin.Null_Iir:
                            # Over-written.
                            continue
                        for r in self._synth_rules:
                            r.check(input, unit)


def execute_and_report(rules, files):
    # Can initialize the library, once the options were set (this will in
    # particular create the standard package).
    thin.analyze_init()

    # Do the checks
    rules.execute(files)

    # Final report
    nbr_files = rules.get_nbr_files()
    print('{0} file{1} checked'.format(
        nbr_files, '' if nbr_files < 2 else 's'))

    nbr_errors = rules.get_nbr_errors()
    if nbr_errors == 0:
        print('No error')
        sys.exit(0)
    else:
        print('{0} error(s)'.format(nbr_errors))
        sys.exit(1)


def main(argv, rules):
    optind = 0
    for i in range(1, len(argv)):
        arg = argv[i]
        if arg[0] != '-':
            optind = i
            break
        if arg in ['-h', '--help']:
            print("usage: {} files...".format(argv[0]))
            sys.exit(0)
        elif arg in ['--import', '--synth', '--tb', '--top']:
            optind = i
            break
        elif thin.set_option(arg) != 0:
            print('unknown option {0}'.format(arg))
            print('try: {0} --help'.format(sys.argv[0]))
            sys.exit(2)

    if optind == 0:
        print('no input file')
        sys.exit(2)

    execute_and_report(rules, argv[optind:])


class TestRun(RulesExec):
    def __init__(self, ruleexec, comment, rule, files):
        super(TestRun, self).__init__(quiet=ruleexec._quiet)
        print('  test: {0}'.format(comment))
        if isinstance(files, str):
            files = [files]
        basedir = os.path.join(os.path.dirname(__file__), 'testfiles')
        files = map(lambda f: f if f.startswith('--') else
                    os.path.join(basedir, f), files)
        # Be sure the work library is empty.  This is brut force.
        work = thin.Work_Library.value
        if work != thin.Null_Iir:
            for f in thinutils.chain_iter(iirs.Get_Design_File_Chain(work)):
                thin.Purge_Design_File(f)
            iirs.Set_Design_File_Chain(work, thin.Null_Iir)
        self.add(rule)
        self.execute(files)
        if not self.is_ok():
            ruleexec._nbr_errors += 1
            sys.stderr.write("ERROR: {0}: test failed\n".format(rule.rulename))

    def is_ok(self):
        return False


class TestRunOK(TestRun):
    def is_ok(self):
        return self.get_nbr_errors() == 0


class TestRunFail(TestRun):
    def is_ok(self):
        return self.get_nbr_errors() != 0
