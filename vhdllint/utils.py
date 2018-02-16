import sys
import libghdl.iirs as iirs
import libghdl.thin as thin


def Location_To_File_Line_Col(loc):
    fe = thin.Location_To_File(loc)
    line = thin.Location_File_To_Line(loc, fe)
    col = thin.Location_File_Line_To_Col(loc, fe, line)
    return (fe, line, col)


class Location(object):
    def __init__(self, filename, line=1, col=1):
        self.filename = filename
        self.line = line
        self.col = col

    def new(self, line, col=1):
        return Location(self.filename, line, col)

    @classmethod
    def from_location(cls, loc):
        fe, line, col = Location_To_File_Line_Col(loc)
        fid = thin.Get_File_Name(fe)
        return cls(thin.Get_Name_Ptr(fid), line, col)

    @classmethod
    def from_node(cls, n):
        return Location.from_location(iirs.Get_Location(n))


class TokLocation(Location):
    def __init__(self, filename, line, col, start, end):
        super(TokLocation, self).__init__(filename, line, col)
        self.start = start
        self.end = end


def fatal(msg):
    sys.stderr.write("fatal: {0}\n".format(msg))
    sys.exit(2)
