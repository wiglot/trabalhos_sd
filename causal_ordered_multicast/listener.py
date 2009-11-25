#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding: utf-8
# mcsrv.py 20080524 AF

import sys, struct, socket

def mcast_server(addr, port):
    fd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    fd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind udp port
    fd.bind(('', port))

    # set mcast group
    mreq = struct.pack('4sl', socket.inet_aton(addr), socket.INADDR_ANY)
    fd.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    try:
        while 1:
            data, addr = fd.recvfrom(1024)
            print '%s bytes from %s: %s' % (len(data), addr, data)
    except KeyboardInterrupt:
        print 'done'
        sys.exit(0)

if __name__ == '__main__':
    try:
        addr = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        addr = '225.0.0.1'
        port = 1905
    finally:
        print 'running server on %s:%d' % (addr, port)
        mcast_server(addr, port)
