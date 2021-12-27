# -*- coding: utf-8 -*-

import os, sys, subprocess
from datetime import datetime
from settings import debug_log, debug_cmdrun, smtp_sender, smtp_port, smtp_server, smtp_username, smtp_password, report_log_success

from smtplib import SMTP_SSL as SMTP
from email.message import EmailMessage

# print level 0
def p_lv0(msg):
    print('\n!',msg)

# print level 1
def p_lv1(msg):
    print('  +',msg)

# print level 2
def p_lv2(msg):
    print('    ',msg)

def p_lv3(msg):
    print('      ',msg)


def log_write(file=False, value=False):
    '''
    basic information of backup
    '''
    if not file or not value:
        return False

    if debug_log:
        p_lv1('log write')
        p_lv3('You are seeing this message because debug_log is True')
        p_lv3('Writing in %s' % file)

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
    p_lv1('cmd run')

    if debug_cmdrun:
        p_lv2('You are seeing this message because debug_cmdrun is True')
        p_lv2(cmd)

    pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = pipe.communicate()
    # res = tuple (stdout, stderr)

    if pipe.returncode == 0:
        msg = u"\n+ command: %s" % (cmd)
        log_write(log, msg)
        p_lv2('+ Success')

        if res[0]:
            for line in res[0].decode(encoding='utf-8').split('\n'):
                log_write(log, line)

        if res[1]:
            for line in res[1].decode(encoding='utf-8').split('\n'):
                log_write(log, line)

    # error
    else:
        msg = u"\n+ command: %s" % (cmd)
        log_write(log_err, msg)

        if res[0]:
            p_lv2('- Error')
            for line in res[0].decode(encoding='utf-8').split('\n'):
                p_lv3(line)
                log_write(log_err, line)

        if res[1]:
            p_lv2('- Error')
            for line in res[1].decode(encoding='utf-8').split('\n'):
                p_lv3(line)
                log_write(log_err, line)


def sendmail(to, app, subject=False, attach0=False, attach1=False, smtp_test=False, log_resume=False):
    '''
    to      : array of email address
    attach0 : error log
    attach1 : sucess log
    log_resume: resume text log file
    '''
    p_lv0('Send backup report mail to admin')

    destination = []
    for x in to:
        destination.append(x)

    if not destination:
        p_lv1('Error trying send a mail. Check settings.')
        p_lv1('[to] are empty. To check config[4]')
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
        p_lv1('-Error trying send a mail. Check settings.')
        p_lv1("-Error: ", e)
        return False
    else:
        p_lv1("Email sent")
        return True

# date format
def dateformat(freq, hour):
    '''
        return date format based in frequency set
    '''
    if hour == False:
        if freq == 'daily':
            return "%s" % (datetime.now().strftime("%A-%d-%b-%Y").lower()) # sunday-28-dez-2014
        if freq == 'month-full':
            return "%s" % (datetime.now().strftime("%d").lower()) # 28
        if freq == 'week-full':
            return '%s' % (datetime.now().strftime("%A").lower()) # sunday
        if freq == 'once':
            return  'once'
    else:
        if freq == 'daily':
            return "%s_%s" % (datetime.now().strftime("%A-%d-%b-%Y").lower(), hour) # sunday-28-dez-2014_14h00
        if freq == 'month-full':
            return "%s-%s" % (datetime.now().strftime("%d").lower(), hour) # 28-14h00m
        if freq == 'week-full':
            return '%s-%s' % (datetime.now().strftime("%A").lower(), hour) # sunday-14h00m
        if freq == 'once':
            return  hour # 14h00m (hour-min)


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
