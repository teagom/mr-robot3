#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, subprocess
from datetime import datetime
from settings import debug, smtp_sender, smtp_port, smtp_server, smtp_username, smtp_password, report_log_success

from smtplib import SMTP_SSL as SMTP
from email.message import EmailMessage


def log_write(file=False, value=False):
    '''
    basic information of backup
    '''
    if not file or not value:
        return False

    if debug:
        print('\nYou are seeing this message because debug is True')
        print('> Writing in', file)

    # open file
    of = open(file, 'a')
    if of:
        of.write(value + '\n')
        of.close()
        return True
    else:
        sys.exit('- Log write error.')


def cmd_run(cmd, log=False, log_err=False):
    '''
    subprocess
    return  result to variable
    cmd:    string command bash
    '''
    if debug:
        print('\nYou are seeing this message because debug is True')
        print('>',cmd)

    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = pipe.communicate()
    # res = tuple (stdout, stderr)

    if pipe.returncode == 0:
        msg = u"\n+ command: %s" % (cmd)
        log_write(log, msg)

        if res[0]:
            for line in res[0].decode(encoding='utf-8').split('\n'):
                print(line)
                log_write(log, line)

        if res[1]:
            for line in res[1].decode(encoding='utf-8').split('\n'):
                print(line)
                log_write(log, line)

    # error
    else:
        msg = u"\n+ command: %s" % (cmd)
        log_write(log_err, msg)

        if res[0]:
            for line in res[0].decode(encoding='utf-8').split('\n'):
                print(line)
                log_write(log_err, line)

        if res[1]:
            for line in res[1].decode(encoding='utf-8').split('\n'):
                print(line)
                log_write(log_err, line)


def sendmail(to, app, subject=False, attach0=False, attach1=False, smtp_test=False, log_resume=False):
    '''
    to      : array of email address
    attach0 : error log
    attach1 : sucess log
    log_resume: resume text log file
    '''
    destination = []
    for x in to:
        destination.append(x)

    if not destination:
        print('- Error trying send a mail. Check settings.')
        print('- [To] are empty. To check config[5]')
        return False

    # new message
    msg = EmailMessage()

    if smtp_test == True:
        msg.set_content('Mr-Robot3 SMTP Test configuration', 'plain')
        msg['Subject'] = "Mr.Robot3 %s" % app
        msg['From'] = smtp_sender

    if smtp_test == False:
        # read attach
        contentattach = ''

        fp = open(log_resume,'rb')
        contentattach += '------------------ Resume begin\n'
        for l in fp.readlines():
            contentattach += u"%s" % l.decode(encoding="utf-8")
        contentattach += '------------------ Resume end'
        fp.close()

        if attach0 and not os.stat("%s" % attach0).st_size == 0:
            fp = open(attach0,'rb')
            contentattach += '\n\n------------------ Error begin\n'
            for l in fp.readlines():
                contentattach += u"%s" % l.decode(encoding="utf-8")
            contentattach += '\n------------------ Error end'
            fp.close()

        # settings
        if report_log_success:
            if attach1 and not os.stat("%s" % attach1).st_size == 0:
                fp = open(attach1,'rb')
                contentattach += '\n\n------------------ Success begin\n'
                for l in fp.readlines():
                    contentattach += u"%s" % l.decode(encoding="utf-8")
                contentattach += '\n------------------ Success end'
                fp.close()

        msg.set_content(contentattach,'plain')
        msg['Subject'] = subject
        msg['From'] = smtp_sender

    try:
        conn = SMTP(smtp_server, smtp_port)
        conn.set_debuglevel(False)
        conn.login(smtp_username, smtp_password)
        conn.sendmail(smtp_sender, destination, msg.as_string())
        conn.close()
    except Exception as e:
        print('- Error trying send a mail. Check settings.')
        print("- Error: ", e)
        return False
    else:
        print("+ Email sent!")
        return True

# date format
def dateformat(o):
    '''
        return date format based in frequency set
    '''
    if o == 'daily':
        return datetime.now().strftime("%A-%d_%m_%Y-%HH%MM").lower() # sunday-28_07_2014-14h00m (weekday_day of month-month-year_hour-min)

    if o == 'month-full':
        return datetime.now().strftime("%d-%HH%MM") # 28-14h00m (day of month_hour_min)

    if o == 'week-full':
        return datetime.now().strftime("%A-%HH%MM").lower() # sunday-14h00m (weekday_hour-min)

    if o == 'once':
        return datetime.now().strftime("%HH%MM") # 14h00m (hour-min)


def mysqlshow(log, log_err, ignore_list):
    # get ALL databases
    cmd='mysqlshow'
    r = subprocess.check_output(cmd, shell=True)
    '''
    clean string
    mysqshow output:
        +--------------------+  0
        | Database           |  1
        +--------------------+  2
        | classicmodels      |  ...
        | information_schema |
        | mysql              |
        | performance_schema |
        | my_app             |
        | sys                |
        | test               |
        | hello_world        |
        +--------------------+  last-1
    ignore line 0,1,2 and last
    create a list of databases
    '''
    ignore = [0,1,2] # positions + last
    ignore.append(len(str(r).split('\\n'))-1)

    c = 0 # postions counter
    db_list = []
    for rr in str(r).split('\\n'):
        #print line,value
        #print(c, str(rr)) # debug

        if not c in ignore:
            if rr.find('+'):
                rr = rr.replace('|','')
                dbname = rr.replace(' ','')

                # BD ignore list
                if not dbname in ignore_list:
                    db_list.append(dbname)
                    #print(c, str(rr)) # debug
        c += 1
    return db_list
