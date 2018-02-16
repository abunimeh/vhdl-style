"""Synthesis rules.
   The files are analyzed. Checkers are called for each unit.

   Synthesis rules are rules specific to non-testbench files."""

from vhdllint.rule import Rule


class SynthesisRule(Rule):
    def __init__(self, rulename):
        super(SynthesisRule, self).__init__(rulename)

    def check(self, input, ast):
        """The check to be performed on an AST (a design unit)."""
        assert False  # Must be redefined
