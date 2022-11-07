#!/usr/bin/python
# ================================
# (C)2022 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d debug utilites
# v1.0
import datetime
import inspect
import os.path
import modo


class H3dDebug:
    def __init__(self, enable=True, file=None, indent=0, indent_str='    '):
        self.enable = enable
        self.indent = indent
        self.indent_str = indent_str
        self.log_path = ''
        self.file_init(file)

    def print_debug(self, message, enable=True, indent=0):
        if not self.enable:
            return
        if not enable:
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
        if not self.log_path:
            self.print_to_sys(message)
            return
        with open(self.log_path, 'a') as f:
            f.write(message)
            f.write('\n')

    @staticmethod
    def print_to_sys(message):
        print(message)

    def exit(self, message='debug exit'):
        self.print_debug(message)
        exit()

    def print_items(self, items, message=None, enable=True, indent=0):
        if not enable:
            return
        if message:
            self.print_debug(message, indent=indent)
        if not items:
            self.print_debug(items, indent=indent+1)
            return
        for i in items:
            if 'modo.item.' in str(type(i)):
                self.print_debug('<{}>'.format(i.name), indent=indent+1)
            else:
                self.print_debug('<{}>'.format(i), indent=indent+1)

    def file_init(self, file):
        if not self.enable:
            return
        if not file:
            return
        scene_path = modo.Scene().filename
        scene_dir = os.path.dirname(scene_path)
        log_path = os.path.join(scene_dir, file)
        with open(log_path, 'w'):
            # reinitialize log file
            pass
        self.log_path = log_path

    def print_fn_in(self, enable=True):
        if not enable:
            return
        caller = inspect.stack()[1][3]
        message = '{}(): in >>'.format(caller)
        self.print_debug(message)
        self.indent_inc()

    def print_fn_out(self, enable=True):
        if not enable:
            return
        caller = inspect.stack()[1][3]
        self.indent_dec()
        message = '{}(): out <<<'.format(caller)
        self.print_debug(message)

    def indent_inc(self, inc=1):
        self.indent += inc

    def indent_dec(self, dec=1):
        self.indent -= dec

    def reset_log(self):
        if not self.enable:
            return
        if not self.log_path:
            return
        f = open(self.log_path, 'w')
        f.close()


h3dd = H3dDebug(enable=True, file=modo.Scene().name.rsplit('.')[0]+'.txt')
is_print_fn_debug = True
