# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 06:06:29 2020

@author: -
"""

import re
import requests
import zipfile
import os
import io
from datetime import datetime
from requests.exceptions import InvalidURL
from _lzma import LZMAError

ignored_routes = ['/session',
                  '/plotfairy/unknown',
                  '/plotfairy/certification',
                  '/plotfairy/archive',
                  '/plotfairy/overlay',
                  '/plotfairy/stripchart',
                  '/start',
                  '/static',
                  '/urlshortener',
                  '/jsonfairy',
                  '/json/archive',
                  '/owa',
                  '/archive',
                  '/modify',
                  '/digest',
                  '/data',
                  '/extjs',
                  '/jsroot',
                  '/yui',
                  '/chooseSample',
                  '/browse']

global zipfile_checkpoint
global weblog_checkpoint

def savecheckpoint():
    with open('checkpoint.txt', 'w+') as w:
        w.write(zipfile_checkpoint +'\n')
        w.write(weblog_checkpoint)

def process(weblog_file):
    now = datetime.now()
    dt_string = now.strftime('%d/%m/%Y %H:%M:%S')
    print('Processing ' + weblog_file + ' ' + dt_string)
    try:
        with io.TextIOWrapper(zf.open(weblog_file), encoding="utf-8") as f:
            for i, _ in enumerate(f):
                pass
            print('Has ' + str(i + 1) + ' requests to rerun')
    except LZMAError:
        with open('failed_requests.txt', 'a+') as fre:
            fre.write('Corrupt log file: ' + weblog_file+'\n')
        return
    line_count = 0
    request_count = 0
    with io.TextIOWrapper(zf.open(weblog_file), encoding="utf-8") as f:
        for line in f:
            line_count = line_count + 1
        #     print('Done '+ str(i) + 'requests')
            match = re.findall('GET(.*)HTTP/1.1" (\d+)', line)
            if len(match) >= 1:
                requested_url = match[0][0]
                # status_code = match[0][1].strip()
                url_match_re = re.findall('/dqm/offline(/.*)\?',requested_url)
                if (len(url_match_re) >= 1):
                    url_match = url_match_re[0]
                    if url_match.strip().startswith(tuple(ignored_routes)):
                        pass
                    else:
                        parameters_string = requested_url.split(url_match)[1]
                        parameters_string = parameters_string[1:].split(';')
                        parameters = {}
                        for string in parameters_string:
                            key_value_pairs = string.strip().split('=')
                            if len(key_value_pairs) >= 2:
                                parameters[key_value_pairs[0]] = key_value_pairs[1]
                        url = 'http://0.0.0.0:8889' + url_match.strip()
                        try:
                            r = requests.get(url = url, params = parameters)
                        except InvalidURL:
                            # no idea what is this error, everything should work except maybe linux charsets
                            # so just write down here and move on
                            with open('failed_requests.txt', 'a+') as fre:
                                fre.write('Invalid URL: ' + url + ': ' + weblog_file + '-at line: ' + str(line_count)+'\n')
                            
                        request_count = request_count + 1
                        if r.status_code != 200:
                            with open('failed_requests.txt', 'a+') as fre:
                                fre.write(url + ': ' + str(r.status_code) + '\n' + 'File: ' + weblog_file + '\n' + 'Line: ' + line+'\n')
                                fre.write('#####'+'\n')
                else:
                    url_match = requested_url.replace('/dqm/offline', '')
                    if url_match.strip().startswith(tuple(ignored_routes)):
                        pass
                    else:
                        url = 'http://0.0.0.0:8889' + url_match.strip()
                        try:
                            r = requests.get(url = url)
                        except InvalidURL:
                            # no idea what is this error, everything should work except maybe linux charsets
                            # so just write down here and move on
                            with open('failed_requests.txt', 'a+') as fre:
                                fre.write('Invalid URL: ' + url + ': ' + weblog_file + '-at line: ' + str(line_count))
                            
                        request_count = request_count + 1
                        if r.status_code != 200:
                            with open('failed_requests.txt', 'a+') as fre:
                                fre.write(url + ': ' + str(r.status_code) + '\n' + 'File: ' + weblog_file + '\n' + 'Line: ' + line)
                                fre.write('#####'+'\n')
            
            if (line_count%10000 == 0):
                print('Done '+ str(line_count) + ' lines, ' + str(request_count) + ' requests')
        # i = 0
log_dir = '/afs/cern.ch/user/h/hlnguyen/public/weblog/'
zippeds = [os.path.join(log_dir, f) for f in os.listdir(log_dir)]

try:
    if os.path.isfile('checkpoint.txt'):
        with open('checkpoint.txt') as cp:
            zipfile_checkpoint = cp.readline().strip()
            weblog_checkpoint = cp.readline().strip()
        with zipfile.ZipFile(zipfile_checkpoint) as zf:
            if weblog_checkpoint != '#':
                namelist = zf.namelist()
                namelist = namelist[namelist.index(weblog_checkpoint) + 1:]
                for weblog_file in namelist:
                    weblog_checkpoint = weblog_file
                    process(weblog_file)
                    savecheckpoint()
            else:
                pass
        weblog_checkpoint = '#'
        zippeds = zippeds[zippeds.index(zipfile_checkpoint) + 1:]
    
    for zipped in zippeds:
        zipfile_checkpoint = zipped
        with zipfile.ZipFile(zipped) as zf:
            namelist = zf.namelist()
            for weblog_file in namelist:
                weblog_checkpoint = weblog_file
                process(weblog_file)
                savecheckpoint()
        weblog_checkpoint = '#'
    os.remove('checkpoint.txt')
except SystemExit:
    savecheckpoint()
         
# atexit.register(savecheckpoint)
                    
