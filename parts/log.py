#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys, argparse, settings, os
from slugify import slugify
from datetime import datetime
from external import cmd_run, sendmail, dateformat, log_write,\
        mysqlshow

parser = argparse.ArgumentParser()
parser.add_argument('integers', metavar='file.py', type=str, nargs='+', help='Python file, parameters to make backup. See example.py')
args = parser.parse_args()

print('\n! Section log')

def log_start(settings, x, cfg, backup_base, backup_log):
    '''
    mkdir path and folder of logs
    touch initial files
    return True
    '''
    print('  log mkdir')

    # log folder
    backup_log = '%s/%s' % (backup_base, 'log')
    backup_log_cmd = 'mkdir -p %s' % (backup_log)
    cmd_run(backup_log_cmd)

    # log files
    print('  Log clean files')
    clean_log = 'rm -f %s/*' % backup_log
    cmd_run(clean_log)

    print('  Log creating files')
    log = "%s/success.log" % backup_log
    log_err = "%s/error.log" % backup_log
    log_resume = "%s/resume.log" % backup_log
    log_write(log, 'Log')
    log_write(log_err, 'Log Err')
    log_write(log_resume, 'Resume')

    return log, log_err, log_resume


def log_finish(settings, x, cfg, backup_base, backup_log):
    end_time = datetime.now()
    duration = (end_time - start_time)
    print('! Start date-time: {}'.format(start_time.strftime(settings.touch_format)))
    print('! End date-time: {}'.format(end_time.strftime(settings.touch_format)))
    print('! Duration: {}'.format(duration))

    # touch end
    touch_log_end = "%s/%s%s" % (backup_log, settings.touch_end, end_time.strftime(settings.touch_format))
    touch_cmd = 'touch %s' % touch_log_end
    cmd_run(touch_cmd, log, log_err)

    # # # # # # # # # #
    # resume section
    print('> Calculating backup base size...')
    cmd = 'du -sh %s' % (backup_base)
    size_base = str(os.popen(cmd).read().replace('\n',''))
    print(size_base)

    # resume
    log_write(log_resume, ('\nSize mysql     : %s' % (size_mysql)))
    log_write(log_resume, ('Size postgresql: %s' % (size_postgresql)))
    log_write(log_resume, ('Size compress  : %s' % (size_compress)))
    log_write(log_resume, ('Size total     : %s\n' % (size_base)))
    log_write(log_resume, ('Start   : %s' % (start_time)))
    log_write(log_resume, ('Finish  : %s' % (end_time)))
    log_write(log_resume, ('Duration: %s' % (duration)))

    return True


def log_send_copy_to(x=None, log=None, log_err=None, backup_log=None, connection=None):
    '''
    send a copy of logs to connection
    when finish backup
    '''
    if x == None or connection == None:
        print('  fail')
        return False

    msg = ('\n! Log send copy to')
    print(msg)

    src = backup_log

    # connection aws s3 bucket
    if connection == 'aws-s3-bucket':
        print ('  connection AWS S3 Bucket')
        if x[50] == True and connection == 'aws-s3-bucket':
            msg = ('  AWS %s/%s' % (x[54],x[56]))
            print('\n'+msg)

            # incremental
            if backup_incremental != False:
                print('  ', backup_incremental)
                dst = u"%s/%s" % (x[56], 'log')
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)

            # frequency
            if backup_frequency != False:
                #msg = ('! AWS copy log files to %s/%s frequency' % (x[54],x[56]))
                #print('\n'+msg)
                print('  ', backup_frequency)
                dst = u"%s/%s" % (backup_frequency, 'log')
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
        else:
            print('  None')


    # connection rsync/copy localhost
    if x[30] == True and connection == 'rsync-copy-localhost':
        print('  connection rsync/copy localhost')

        # incremental
        backup_incremental = x[34]
        if backup_incremental != False:
            print('  format incremental')
            dst = u"%s/%s" % (x[38], x[34])
            cmd = "%s %s %s" % (x[31], src, dst)
            print('\n  copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

        # frequency
        backup_frequency = x[37] # path
        if backup_frequency != False:
            print('  format frequency')
            # frequency/<datet-time>/log ?

            dst = u"%s/%s" % (x[38], backup_frequency)  # root + path
            cmd = "%s %s %s" % (x[31], src, dst)
            print('\n  copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

    # TODO
    # connection ssh/rsync
    # connection ftp

    return True
