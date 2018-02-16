"""Syntactic rules.
   The files are first parsed (but semantic analysis is not done). checkers
   are called for each file, with the unanalyzed AST.

   Syntactic rules include indentations, naming conventions for some
   identifiers..."""

from vhdllint.rule import Rule


class SyntaxRule(Rule):
    def __init__(self, rulename):
        super(SyntaxRule, self).__init__(rulename)

    def check(self, input, ast):
        """The check to be performed on an AST (a design file)."""
        assert False  # Must be redefined


class SyntaxNodeRule(Rule):
    def __init__(self, rulename):
        super(SyntaxNodeRule, self).__init__(rulename)

    def check(self, input, node):
        """The check to be performed on each node."""
        assert False  # Must be redefined
