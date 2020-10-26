# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.3'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import os
import sys
import socket
import logging
import argparse
import datetime
import threading
import configparser

from check_https_utils import PostgreSQL, send_msg, recv_msg
from webcache import WebCache
from tests_https import run_all_tests


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S',
    filename='https_evaluate.log',
    filemode='w')


# Status class it helps to monitor the state of the server 
class Status(object):
    def __init__(self):
        self.busy = False
        self.total = 0
        self.i = 0
        self.lock = threading.Lock()
    
    def put(self, busy, total, i):
        with self.lock:
            self.busy = busy
            self.total = total
            self.i = i
    
    def is_busy(self):
        with self.lock:
            busy = self.busy
        return busy
    
    def get(self):
        with self.lock:
            busy = self.busy
            total = self.total
            i = self.i
        return busy, total, i

    def reset(self):
        with self.lock:
            self.busy = False
            self.total = 1
            self.i = 1


def run_tests(dh, dp, status):
    status.put(True, 1, 0)
    date = datetime.datetime.now()
    db = PostgreSQL(host=dh, port=dp)
    wc = WebCache()
    municipalities = db.municipality_select_all()
    status.put(True, len(municipalities), 0)
    i = 0
    for name in municipalities:
        url = db.municipality_select_name(name)
        results = run_all_tests(url, wc)
        qualities = results['qualities']
        defects = results['defects']
        data = results['data']
        db.qualities_insert(url, date, qualities[0], qualities[1], qualities[2], qualities[3], qualities[4], qualities[5])
        db.defects_insert(url, date, defects[0], defects[1], defects[2])
        if data is not None:
            db.data_insert(url, date, data['html_raw'], data['html_rendered'], data['img'])
        else:
            db.data_insert(url, date, '', '', b'')
        i += 1
        status.put(True, len(municipalities), i)
    status.reset()


def main(args):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket to the port
    sock.bind((args.sh, args.sp))
    sock.settimeout(None)
    # Create a Status object (it monitors the status of the server)
    status = Status()
    # Main loop
    while True:
        request, addr = recv_msg(sock)
        if request == 'run':
            if status.is_busy():
                send_msg(sock, {'busy': True, 'total': 1, 'i': 1, 'msg':'The server is busy, use status to check...'}, addr)
            else:
                thread = threading.Thread(target = run_tests, args = (args.dh, args.dp, status))
                thread.start()
                send_msg(sock, {'busy': True, 'total': 1, 'i': 1, 'msg':'The server stated a new job, use status to check...'}, addr)
        elif request == 'status':
            busy, total, i = status.get()
            if busy:
                send_msg(sock, {'busy': busy, 'total': total, 'i': i, 'msg':'The server is running a test, use status to check...'}, addr)
            else:
                send_msg(sock, {'busy': busy, 'total': total, 'i': i, 'msg':'The server is free, use run to start a new test...'}, addr)
        else:
            send_msg(sock, {'busy': None, 'total': 1, 'i': 1, 'msg':'Unkown command (run|status)'}, addr)


if __name__ == '__main__':
    # Combine argparse with configparse
    # based on: http://blog.vwelch.com/2011/04/combining-configparser-and-argparse.html 
    # Turn off help, so we print all options in response to -h
    conf_parser = argparse.ArgumentParser(add_help=False, )
    conf_parser.add_argument('-cf', help='Specify config file', metavar='FILE')
    args, remaining_argv = conf_parser.parse_known_args()
    
    defaults = {
    'dh' : '192.168.1.252',
    'dp' : 5432,
    'sh' : '0.0.0.0',
    'sp' : 9876 
    }

    if args.cf:
        config = configparser.SafeConfigParser()
        config.read([args.cf])
        defaults = dict(config.items("Defaults"))
    
    # Don't surpress add_help here so it will handle -h
    parser = argparse.ArgumentParser(
        # Inherit options from config_parser
        parents=[conf_parser],
        # print script description with -h/--help
        #description=__doc__,
        description='Check https municipalities server',
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.set_defaults(**defaults)
    parser.add_argument('-dh', type=str, help='database hostname', default='192.168.1.252')
    parser.add_argument('-dp', type=int, help='database port', default=5432)
    parser.add_argument('-sh', type=str, help='server hostname', default='0.0.0.0')
    parser.add_argument('-sp', type=int, help='server port', default=9876)
    args = parser.parse_args(remaining_argv)
    #logging.info(args)
    main(args)
