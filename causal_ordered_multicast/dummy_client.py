#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8
# udpcli.py 20080524 AF

import sys, socket

if __name__ == '__main__':
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
        buff = sys.argv[3]
    except IndexError:
        print 'use: %s addr port buff' % sys.argv[0]
        sys.exit(1)

    fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fd.sendto(buff, (addr, port))
