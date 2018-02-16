"""Lexical rules.
   The checkers are called for each token in the files. The tokens include
   comments (there is a special token to represent a comment).

   Lexical rules include case of keywords, specific rules about comments,
   spaces around operators...
   """

from vhdllint.rule import Rule


class LexRule(Rule):
    def __init__(self, rulename):
        super(LexRule, self).__init__(rulename)

    def check(self, loc, filebuf, tok):
        """The check to be performed on a token."""
        assert False  # Must be redefined
