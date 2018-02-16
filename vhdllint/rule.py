class Rule(object):
    def __init__(self, rulename):
        if rulename:
            self._rulename = rulename
        else:
            self._rulename = self.rulename
        self._run = None

    def set_runner(self, run):
        self._run = run

    def error(self, loc, msg):
        self._run.error("{0}:{1}:{2}: [{3}] {4}\n".format(
            loc.filename, loc.line, loc.col, self._rulename, msg))
