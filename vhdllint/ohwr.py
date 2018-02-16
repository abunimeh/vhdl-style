#!/usr/bin/env python

# VHDL linter for OHWR coding style

import sys
import rulesexec
import libghdl.thin
import libghdl.iirs as iirs

# Import all rules
from filerules.check_line_length import CheckLineLength
from filerules.check_no_blank_line_at_eof import CheckNoBlankLineAtEOF
from filerules.check_missing_newline import CheckMissingNewline
from filerules.check_no_tab import CheckNoTAB
from filerules.check_no_trailing_spaces import CheckNoTrailingSpaces
from filerules.check_newline import CheckNewline
from filerules.check_header import CheckHeader
from filerules.check_charset import CheckCharSet
from lexrules.check_keyword_case import CheckKeywordCase
from lexrules.check_comments import CheckComments
from lexrules.check_spaces import CheckSpaces
from syntaxrules.check_attribute_decl import CheckAttributeDecl
from syntaxrules.check_attribute_name import CheckAttributeName
from syntaxrules.check_entity_simple import CheckEntitySimple
from syntaxrules.check_enum_char_lit import CheckEnumCharLit
from syntaxrules.check_guarded_signals import CheckGuardedSignals
from syntaxrules.check_disconnection import CheckDisconnection
from syntaxrules.check_simple_block import CheckSimpleBlock
from syntaxrules.check_group import CheckGroup
from syntaxrules.check_ports_mode import CheckPortsMode
from syntaxrules.check_config_spec import CheckConfigSpec
from syntaxrules.check_file_name import CheckFileName
from syntaxrules.check_one_unit import CheckOneUnit
from syntaxrules.check_generics import CheckGenerics
from syntaxrules.check_ports_name import CheckPortsName
from syntaxrules.check_basic_indent import CheckBasicIndent
from syntaxrules.check_name_decl import CheckNameDecl
from syntaxrules.check_ieee_packages import CheckIeeePackages
from syntaxrules.check_signals_name import CheckSignalsName
from syntaxrules.check_context_use import CheckContextUse
from syntaxrules.check_end_label import CheckEndLabel
from syntaxrules.check_parenthesis import CheckParenthesis
from syntaxrules.check_process_label import CheckProcessLabel
from syntaxrules.check_subprg_is_layout import CheckSubprgIsLayout
from syntaxrules.check_complex_stmt_layout import CheckComplexStmtLayout
from syntaxrules.check_instantiation import CheckInstantiation
from syntaxrules.check_entity_layout import CheckEntityLayout
from syntaxrules.check_context_clauses import CheckContextClauses

# [VHDLVersion] [M] VHDL standard version
# There is no specific rule, the analyzer will catch errors
libghdl.thin.set_option("--std=93c")

# Create rules
rules = rulesexec.RulesExec()

# List of rules (v1.0):

# File rules

# [FileName] [M] Name of VHDL file
rules.add(CheckFileName(extension='.vhd'))

# [FileContent] [R] Content of a VHDL file
rules.add(CheckOneUnit(name='FileContent', patterns=['EA', 'C', 'P', 'PB']))

# [FileHeader] [M] Header comment of a VHDL file
# TODO: template
rules.add(CheckHeader(name='FileHeader'))

# [LineLength] [M] Source line length
rules.add(CheckLineLength(132))

# [EndOfLine] [M] End of line
rules.add(CheckNewline(name='EndOfLine'))

# [Language] [M] Language for comments and identifiers (I)
# Inspection

# [CharSet] [M] Character set
rules.add(CheckCharSet())

# [NoTAB] [M] No tabulation
rules.add(CheckNoTAB(name='NoTAB'))

# [LastLine] [M] Last line in a file
rules.add(CheckNoBlankLineAtEOF(name='LastLine'))
rules.add(CheckMissingNewline(name='LastLine'))

# [TrailingSpaces] [M] Trailing spaces
rules.add(CheckNoTrailingSpaces(name='TrailingSpaces'))

# Format rules

# [Comments] [M] Comment style
rules.add(CheckComments())

# [Indentation] [M] Indentation
rules.add(CheckBasicIndent(name='Indentation'))

# [WhiteSpaces] [M] Spaces
rules.add(CheckSpaces(name='Spaces'))

# [Context] [M] Context clauses
rules.add(CheckContextClauses())

# [UseClause] [M] Place of use clause
rules.add(CheckContextUse())

# [EntityLayout] [M] Layout of entity declaration
rules.add(CheckEntityLayout())

# [ComplexStmtLayout] [M] Layout of complex statements
rules.add(CheckComplexStmtLayout())

# [SubprgIsLayout] [M] Layout of is keyword in subprogram
rules.add(CheckSubprgIsLayout())

# [EndLabel] [M] Presence of the label after end
rules.add(CheckEndLabel())

# [Instantiation] [M] Layout of instantiation
rules.add(CheckInstantiation())

# [ProcessLabel] [M] Label of processes
rules.add(CheckProcessLabel())

# [Parenthesis] [M] Use of parenthesis in expressions
rules.add(CheckParenthesis())

# Identifiers

# [Keywords] [M] Keywords case
rules.add(CheckKeywordCase())

# [Identifiers] [M] Identifiers case (I)
# Inspection

# [Underscores] [M] Use of underscore in identifiers (I)
# Inspection

# [ReferenceName] [M] Reference

# [ArchNames] [M] Architectures name
rules.add(CheckNameDecl(kind=iirs.Iir_Kind.Architecture_Body,
                        predicate=(lambda n: n == 'arch'),
                        name='ArchNames'))

# [Constants] [M] Constants name
rules.add(CheckNameDecl(kind=iirs.Iir_Kind.Constant_Declaration,
                        predicate=(lambda n: len(n) >= 3
                                   and n[:2] == 'c_'
                                   and n[2:].isupper()),
                        name='Constants'))

# [GenericsName] [M] Generics name
rules.add(CheckGenerics(name='GenericsName'))

# [PortsName] [M] Ports name
rules.add(CheckPortsName(name='PortsName'))

# [SignalsName] [M] Signals name
rules.add(CheckSignalsName(name='SignalsName'))

# [TypesName] [M] Types name
rules.add(CheckNameDecl(kind=iirs.Iir_Kind.Type_Declaration,
                        predicate=(lambda n: len(n) >= 3 and n[:2] == 't_'),
                        name='TypesName'))
rules.add(CheckNameDecl(kind=iirs.Iir_Kind.Subtype_Declaration,
                        predicate=(lambda n: len(n) >= 3 and n[:2] == 't_'),
                        name='TypesName'))

# [PackagesName] [M] Packages name
rules.add(CheckNameDecl(kind=iirs.Iir_Kind.Package_Declaration,
                        predicate=(lambda n: len(n) >= 4 and n[-4:] == '_pkg'),
                        name='PackagesName'))

# Language subset

# [VHDLVersion] [M] VHDL standard version
# Set by a switch

# [IEEEPkg] [M] Use of IEEE packages
rules.add(CheckIeeePackages(extra_pkg=['math_real',
                                       'std_logic_misc',
                                       'std_logic_textio'],
                            name='IEEEPkg'))

# [NoUserAttributes] [M] Attribute declarations not allowed
# Allow attributes for synthesis tools.
rules.add(CheckAttributeDecl
          (name="NoUserAttributes",
           allowed=['keep', 'shreg_extract', 'opt_mode', 'resource_sharing',
                    'altera_attribute']))

# [NoUserAttrName] [M] Attribute names
rules.add(CheckAttributeName())

# [EntityItems] [M] Entity declarative items
rules.add(CheckEntitySimple())

# [NoCharEnumLit] [M] Character as enumeration literal
rules.add(CheckEnumCharLit())

# [GuardedSignals] [M] Guarded signals
rules.add(CheckGuardedSignals())

# [Disconnection] [M] Disconnection Specification
rules.add(CheckDisconnection())

# [BlockStatement] [M] Block statements
rules.add(CheckSimpleBlock())

# [GroupDeclaration] [M] Group and group template
rules.add(CheckGroup())

# [PortMode] [M] Buffer and linkage mode
rules.add(CheckPortsMode())

# [ConfigSpec] [M] Configuration specification
rules.add(CheckConfigSpec())

# Synthesis rules

# [RemovedSynth] [M] Language features not allowed for synthesis

# [PortsType] [M] Type of top-level ports

# [GenericType] [M] Type of top-levels generics

# [WrapperUnit] [R] Wrapper of top-level units

# [RegisterTemplate] [R] Process for a register.

# [AsyncReset] [M] Asynchronous reset

# [RegisterReset] [M] Register reset

# [SignalAttribute] [M] Signal attributes

# [VectorDirection] [M] Direction of indexes

# [EmptyArray] [M] Minimal length of arrays

# [ClockResetPorts] [M] Clock and reset ports

# [ClocksUse] [M] Usage of clocks

# [FSMCoding] [R] FSM code style

rulesexec.execute_and_report(rules, sys.argv[1:])
