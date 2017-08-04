#!/bin/env python3
#
# build/install gdb with python support
# then in gdb or .gdbinit:
# source ~/path/flowdump.py

import gdb

class FlowDump(gdb.Command):
    """Dumps execution flow of the program.

Usage: flowdump [max_depth]
Use -1 as max_depth for unlimited depth.
Dumping will stop after you reached next line in the outer (caller) frame relative to your current position.
Typical usage: set breakpoint somewhere, then run flowdump. You will stop in the upper frame rigth after your breakpoint.
"""
    def __init__(self):
        super (FlowDump, self).__init__ ('flowdump', gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        # if no max_depth given, use 0
        if len(argv) > 0:
            max_depth = int(argv[0])
        else:
            max_depth = 0

        # calculate address of the next line in outer function
        frame = gdb.selected_frame()
        pc_older = frame.older().pc()
        symtabline = gdb.find_pc_line(pc_older)
        pc_older_next = symtabline.last + 1

        depth = 0

        stack = []
        stack.append(frame)

        # get current 'pagination'
        if gdb.parameter('pagination') == True:
            pagination = 'on'
        else:
            pagination = 'off'
        gdb.execute('set pagination off')


        try:
            # while our addres not equal to the address of the next line in outer function
            while pc_older_next != gdb.selected_frame().pc():
                pc = gdb.selected_frame().pc()

                if max_depth == 0:
                    gdb.execute('next')
                elif max_depth == -1:
                    # if unlimited depth defined
                    gdb.execute('step')
                else:
                    # if we still on the current frame, then do nothing
                    if gdb.selected_frame() == stack[-1]:
                        pass
                    # if we frame up
                    elif len(stack) > 1 and gdb.selected_frame() == stack[-2]:
                        depth = depth - 1
                        stack.pop()
                    # if we frame down
                    else:
                        depth = depth + 1
                        stack.append(gdb.selected_frame())

                    if depth < max_depth:
                        gdb.execute('step')
                    else:
                        gdb.execute('next')

        except RuntimeError as e:
            error("%s" % e)
            #raise

        # restore 'pagination'
        gdb.execute('set pagination ' + pagination)

FlowDump()
