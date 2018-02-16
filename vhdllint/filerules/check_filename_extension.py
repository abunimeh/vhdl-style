import os.path
from vhdllint.filerules import FileRule
from vhdllint.rulesexec import TestRunOK, TestRunFail


class CheckFilenameExtension(FileRule):
    """Check the extension of the filename"""

    rulename = 'FileExt'

    def __init__(self, extensions=['.vhd', '.vhdl'], name=None):
        super(CheckFilenameExtension, self).__init__(name)
        self.extensions = extensions

    def check(self, loc, lines):
        filename = loc.filename
        (root, ext) = os.path.splitext(filename)
        if ext not in self.extensions:
            self.error(loc, 'bad filename extension')

    @staticmethod
    def test(runner):
        rule = CheckFilenameExtension()
        TestRunOK(runner, "Filename with correct extension",
                  rule, "hello.vhdl")
        TestRunFail(runner, "Filename with incorrect extension",
                    rule, "badext.txt")
