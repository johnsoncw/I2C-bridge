#!/usr/bin/env python
# encoding: utf-8
"""
Created by Chris Johnson, 2015.

This module helps with debug tracing.
Copyright (C) 2015  Chris Johnson

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


def tracer(message, newline=True):
    if newline:
        print(message)
    else:
        print(message, end="")


def trace_data(msg, data):
    tracer(msg, False)
    op = b" " + data
    for b in op[1:]:
        tracer(format(b, '02x') + " ", False)
    tracer(" ")


def trace_write_data(data):
    trace_data("    >> ", data)


def trace_read_data(data):
    trace_data("      << ", data)
