from vhdllint.synthrules import SynthesisRule
from vhdllint.rulesexec import TestRunOK, TestRunFail
import libghdl.thin as thin
import libghdl.thinutils as thinutils
import libghdl.iirs as iirs
import vhdllint.nodeutils as nodeutils
from vhdllint.utils import Location


class CheckProcesses(SynthesisRule):
    """Check processes: only processes with a sensitivity list."""

    rulename = 'SynthProcesses'

    def __init__(self, name=None):
        super(self.__class__, self).__init__(name)

    def is_edge_condition(self, cond):
        k = iirs.Get_Kind(cond)
        if k != iirs.Iir_Kind.Function_Call:
            # TODO: allow 'event ?
            return (None, None)
        imp = iirs.Get_Implementation(cond)
        if imp == thin.Ieee.Rising_Edge.value:
            edge = True
        elif imp == thin.Ieee.Falling_Edge.value:
            edge = False
        else:
            return (None, None)
        assoc = iirs.Get_Parameter_Association_Chain(cond)
        return (iirs.Get_Actual(assoc), edge)

    def is_register(self, stmt):
        cond = iirs.Get_Condition(stmt)
        (clk, edge) = self.is_edge_condition(cond)
        if clk:
            return (clk, None)
        else:
            # TODO: asynchronous reset
            return (None, None)

    def in_sensitivity(self, lst, sig):
        sig = thin.Iirs_Utils.Strip_Denoting_Name(sig)
        for el in thinutils.list_iter(lst):
            el = thin.Iirs_Utils.Strip_Denoting_Name(el)
            # FIXME: handle suffix
            if el == sig:
                return True
        k = iirs.Get_Kind(sig)
        if k == iirs.Iir_Kind.Slice_Name \
           or k == iirs.Iir_Kind.Indexed_Name \
           or k == iirs.Iir_Kind.Selected_Element:
            if self.in_sensitivity(lst, iirs.Get_Prefix(sig)):
                return True
        return False

    def check_register(self, proc, clk, rst):
        slist = iirs.Get_Sensitivity_List(proc)
        if not self.in_sensitivity(slist, clk):
            self.error(Location.from_node(proc),
                       "clock not in sensitivity list")
        if thin.Lists.Get_Nbr_Elements(slist) != 1:
            self.error(Location.from_node(proc),
                       "too many signals in sensitivity list")

    def check_process(self, proc):
        stmt = iirs.Get_Sequential_Statement_Chain(proc)
        if nodeutils.is_one_stmt(stmt) \
           and iirs.Get_Kind(stmt) == iirs.Iir_Kind.If_Statement:
            (clk, rst) = self.is_register(stmt)
            if clk is not None:
                self.check_register(proc, clk, rst)
                return
        slist = iirs.Get_Sensitivity_List(proc)
        clist = thin.Lists.Create_Iir_List()
        thin.Canon.Extract_Sequential_Statement_Chain_Sensitivity(
            iirs.Get_Sequential_Statement_Chain(proc), clist)
        for el in thinutils.list_iter(clist):
            if not self.in_sensitivity(slist, el):
                self.error(Location.from_node(el),
                           "signal not in sensitivity list")
        thin.Lists.Destroy_Iir_List(clist)

    def check(self, input, unit):
        for n in thinutils.concurrent_stmts_iter(unit):
            k = iirs.Get_Kind(n)
            if k == iirs.Iir_Kind.Process_Statement:
                self.error(Location.from_node(n),
                           "non-sentized process not allowed in synth unit")
            elif k == iirs.Iir_Kind.Sensitized_Process_Statement:
                self.check_process(n)
            else:
                # Check for non-postponed ?
                pass

    @staticmethod
    def test(runner):
        rule = CheckProcesses()
        TestRunOK(runner, "simple FF",
                  rule, ['--synth', "synthproc1.vhdl"])
        TestRunFail(runner, "non-sensitized process",
                    rule, ['--synth', "synthproc2.vhdl"])
        TestRunOK(runner, "simple combinational",
                  rule, ['--synth', "synthproc3.vhdl"])
        TestRunFail(runner, "missing signal in sensitivity list",
                    rule, ['--synth', "synthproc4.vhdl"])
