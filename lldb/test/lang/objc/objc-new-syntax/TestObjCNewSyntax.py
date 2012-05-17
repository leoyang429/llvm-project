"""Test that the Objective-C syntax for dictionary/array literals and indexing works"""

import os, time
import unittest2
import lldb
import platform

from distutils.version import StrictVersion

from lldbtest import *

class ObjCNewSyntaxTestCase(TestBase):

    mydir = os.path.join("lang", "objc", "objc-new-syntax")

    @expectedFailurei386
    @dsym_test
    def test_expr_with_dsym(self):
        self.buildDsym()
        self.expr()

    @expectedFailurei386
    @dwarf_test
    def test_expr_with_dwarf(self):
        self.buildDwarf()
        self.expr()

    def setUp(self):
        # Call super's setUp().
        TestBase.setUp(self)
        # Find the line number to break inside main().
        self.line = line_number('main.m', '// Set breakpoint 0 here.')

    def applies(self):
        if platform.system() != "Darwin":
            return False
        if StrictVersion('12.0.0') > platform.release():
            return False

        return True

    def common_setup(self):
        exe = os.path.join(os.getcwd(), "a.out")
        self.runCmd("file " + exe, CURRENT_EXECUTABLE_SET)

        # Break inside the foo function which takes a bar_ptr argument.
        self.expect("breakpoint set -f main.m -l %d" % self.line, BREAKPOINT_CREATED,
            startstr = "Breakpoint created")

        self.runCmd("run", RUN_SUCCEEDED)

        # The stop reason of the thread should be breakpoint.
        self.expect("thread list", STOPPED_DUE_TO_BREAKPOINT,
            substrs = ['stopped',
                       'stop reason = breakpoint'])

        # The breakpoint should have a hit count of 1.
        self.expect("breakpoint list -f", BREAKPOINT_HIT_ONCE,
            substrs = [' resolved, hit count = 1'])

    def expr(self):
        if not self.applies():
            return

        self.common_setup()

        self.expect("expr -o -- immutable_array[0]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["foo"])

        self.expect("expr -o -- mutable_array[0]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["foo"])

        self.expect("expr -o -- mutable_array[0] = @\"bar\"", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["bar"])

        self.expect("expr -o -- mutable_array[0]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["bar"])

        self.expect("expr -o -- immutable_dictionary[@\"key\"]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["value"])

        self.expect("expr -o -- mutable_dictionary[@\"key\"]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["value"])

        self.expect("expr -o -- mutable_dictionary[@\"key\"] = @\"object\"", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["object"])

        self.expect("expr -o -- mutable_dictionary[@\"key\"]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["object"])

        self.expect("expr -o -- @[ @\"foo\", @\"bar\" ]", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSArray", "foo", "bar"])

        self.expect("expr -o -- @{ @\"key\" : @\"object\" }", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSDictionary", "key", "object"])

        self.expect("expr -o -- @'a'", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", str(ord('a'))])

        self.expect("expr -o -- @1", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "1"])

        self.expect("expr -o -- @1l", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "1"])

        self.expect("expr -o -- @1ul", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "1"])

        self.expect("expr -o -- @1ll", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "1"])

        self.expect("expr -o -- @1ull", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "1"])

        self.expect("expr -o -- @123.45", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "123.45"])
        self.expect("expr -o -- @123.45f", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "123.45"])

        self.expect("expr -o -- @( 1 + 3 )", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSNumber", "4"])
        self.expect("expr -o -- @(\"Hello world\" + 6)", VARIABLES_DISPLAYED_CORRECTLY,
            substrs = ["NSString", "@\"world\""])

            
if __name__ == '__main__':
    import atexit
    lldb.SBDebugger.Initialize()
    atexit.register(lambda: lldb.SBDebugger.Terminate())
    unittest2.main()
