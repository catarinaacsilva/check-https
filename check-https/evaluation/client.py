# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.2'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import os
import sys
import time
import socket
import argparse
from check_https_utils import send_msg, recv_msg, progress_bar


def main(args):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_msg(sock, args.command, (args.sh, args.sp))
    reply, addr = recv_msg(sock)
    
    if args.command == 'status':
        if reply['busy'] == True:
            progress_bar(reply['i'], reply['total'], 'Done...')
            while reply['busy'] == True:
                time.sleep(10)
                send_msg(sock, args.command, (args.sh, args.sp))
                reply, addr = recv_msg(sock)
                progress_bar(reply['i'], reply['total'], 'Done...')
            progress_bar(1,1, 'Done...')
        else:
            print(reply['msg'])
    else:
        print(reply['msg'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check https municipalities client')
    parser.add_argument('-sh', type=str, help='server hostname', default='localhost')
    parser.add_argument('-sp', type=int, help='server port', default=9876)
    parser.add_argument('command', metavar='cmd', type=str, help='a command to send to the server')
    args = parser.parse_args()
    main(args)
