"""Semantic rules.
   The files are parsed and analyzed. Checkers are called for each file.

   Semantic rules include checks on types, use of packages..."""

from vhdllint.rule import Rule


class SemRule(Rule):
    def __init__(self, rulename):
        super(SemRule, self).__init__(rulename)

    def check(self, loc, dsgn):
        """The check to be performed on an AST (a design unit)."""
        assert False  # Must be redefined


class SemNodeRule(Rule):
    def __init__(self, rulename):
        super(SemNodeRule, self).__init__(rulename)

    def check(self, loc, node):
        """The check to be performed on each node."""
        assert False  # Must be redefined
