#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d debug utilites
# v1.0

import sys
import datetime
import inspect
import os.path
import modo
import lx

sys.path.append('{}\\scripts'.format(lx.eval('query platformservice alias ? {kit_h3d_item_replace_tools:}')))
from h3d_kit_constants import *
from h3d_utils import h3du


class H3dDebug:
    def __init__(self, enable=True, file=None, indent=0, indent_str='    '):
        self.enable = enable
        self.initial_indent = int(indent)
        self.indent = self.initial_indent
        self.indent_str = indent_str
        self.log_path = ''
        self.file_init(file)

    def print_debug(self, message, indent=0):
        if not self.enable:
            return
        self.indent += indent
        curtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        message_upd = '{}{} {}'.format(curtime, self.indent_str * self.indent, message)
        if self.log_path:
            self.print_to_file(message_upd)
        else:
            self.print_to_sys(message_upd)
        self.indent -= indent

    def print_to_file(self, message):
        if not self.enable:
            return
        if not self.log_path:
            self.print_to_sys(message)
            return
        with open(self.log_path, 'a') as f:
            f.write(message)
            f.write('\n')

    def print_to_sys(self, message):
        if not self.enable:
            return
        print(message)

    def exit(self, message='debug exit'):
        if not self.enable:
            return
        self.print_debug(message)
        exit()

    def print_items(self, items, message=None, indent=0):
        if not self.enable:
            return
        if message:
            self.print_debug(message, indent=indent)
        if not items:
            self.print_debug(items, indent=indent + 1)
            return
        for i in items:
            if 'modo.item.' in str(type(i)):
                self.print_debug('<{}>'.format(i.name), indent=indent + 1)
            else:
                self.print_debug('<{}>'.format(i), indent=indent + 1)

    def file_init(self, file):
        if not file:
            return
        scene_path = modo.Scene().filename
        scene_dir = os.path.dirname(scene_path)
        log_path = os.path.join(scene_dir, file)
        self.log_path = log_path
        if not self.enable:
            return
        self.log_reset()

    def print_fn_in(self):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        message = '{}(): in >>>>'.format(caller)
        self.print_debug(message)
        self.indent_inc()

    def print_fn_out(self):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        self.indent_dec()
        message = '<<<< out: {}()'.format(caller)
        self.print_debug(message)

    def indent_inc(self, inc=1):
        if not self.enable:
            return
        self.indent += inc

    def indent_dec(self, dec=1):
        if not self.enable:
            return
        self.indent -= dec

    def log_reset(self):
        if not self.log_path:
            return
        with open(self.log_path, 'w'):
            # reinitialize log file
            pass
        self.indent = self.initial_indent


do_save_log = h3du.get_user_value(USER_VAL_NAME_SAVE_LOG)
h3dd = H3dDebug(enable=do_save_log, file=modo.Scene().name.rsplit('.')[0] + '.txt')
