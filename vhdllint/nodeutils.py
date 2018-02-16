import ctypes
import libghdl.iirs as iirs
import libghdl.thin as thin
import libghdl.thinutils as thinutils


def _is_interface_port_generic(node):
    parent_kind = iirs.Get_Kind(iirs.Get_Parent(node))
    return (parent_kind in [iirs.Iir_Kind.Entity_Declaration,
                            iirs.Iir_Kind.Component_Declaration,
                            iirs.Iir_Kind.Block_Header])


def is_generic(node):
    """Return True iff argument node is a generic."""
    if iirs.Get_Kind(node) != iirs.Iir_Kind.Interface_Constant_Declaration:
        return False
    return _is_interface_port_generic(node)


def is_port(node):
    """Return True iff argument node is a port."""
    if iirs.Get_Kind(node) != iirs.Iir_Kind.Interface_Signal_Declaration:
        return False
    return _is_interface_port_generic(node)


def is_std_logic(typ):
    return typ == thin.Ieee.Std_Logic_Type.value


def is_std_logic_vector(typ):
    return iirs.Get_Base_Type(typ) == thin.Ieee.Std_Logic_Vector_Type.value


def is_std_logic_or_std_logic_vector(typ):
    return is_std_logic(typ) or is_std_logic_vector(typ)


def get_identifier_str(n):
    """Return the identifier (as it appears in the sources) for node n.

    The node n must have an identifier field.  There is no case conversion."""
    ident = iirs.Get_Identifier(n)
    id_len = thin.Get_Name_Length(ident)
    loc = iirs.Get_Location(n)
    fe = thin.Location_To_File(loc)
    pos = thin.Location_File_To_Pos(loc, fe)
    fptr = thin.Get_File_Buffer(fe)
    return ctypes.string_at(fptr + pos, id_len).decode('latin-1')


def is_predefined_node(n):
    k = iirs.Get_Kind(n)
    if k == iirs.Iir_Kind.Interface_Constant_Declaration \
       and iirs.Get_Identifier(n) == 0:
        return True
    if k == iirs.Iir_Kind.Function_Declaration \
       and iirs.Get_Implicit_Definition(n) < iirs.Iir_Predefined.PNone:
        return True
    return False


def is_one_stmt(chain):
    return chain != thin.Null_Iir \
        and iirs.Get_Chain(chain) == thin.Null_Iir


def is_one_alt(alts):
    assert not iirs.Get_Same_Alternative_Flag(alts)
    next_alt = iirs.Get_Chain(alts)
    return next_alt == thin.Null_Iir \
        or not iirs.Get_Same_Alternative_Flag(next_alt)


def is_same_line(loc1, loc2):
    """Return True iff loc1 and loc2 point to the same line in the
    same file."""
    fe = thin.Location_To_File(loc1)
    if fe != thin.Location_To_File(loc2):
        return False
    line = thin.Location_File_To_Line(loc1, fe)
    return line == thin.Location_File_To_Line(loc2, fe)


def extract_packages_from_context_clause(dsgn):
    """Return a list of package declarations from design unit dsgn (which must
    have been analyzed)."""
    res = []
    for n in thinutils.chain_iter(iirs.Get_Context_Items(dsgn)):
        if iirs.Get_Kind(n) != iirs.Iir_Kind.Use_Clause:
            continue
        cl = n
        while cl != thin.Null_Iir:
            name = iirs.Get_Selected_Name(cl)
            if iirs.Get_Kind(name) == iirs.Iir_Kind.Selected_By_All_Name:
                name = iirs.Get_Prefix(name)
            name = iirs.Get_Named_Entity(name)
            assert name != thin.Null_Iir, "unit not analyzed"
            if iirs.Get_Kind(name) == iirs.Iir_Kind.Package_Declaration:
                res.append(name)
            cl = iirs.Get_Use_Clause_Chain(cl)
    return res
