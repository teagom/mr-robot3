# -*- coding: utf-8 -*-

import re
import sys, argparse, settings, os
from slugify import slugify
from datetime import datetime
from external import cmd_run, sendmail, dateformat, log_write,\
        mysqlshow, p_lv0, p_lv1, p_lv2, p_lv3

parser = argparse.ArgumentParser()
parser.add_argument('integers', metavar='file.py', type=str, nargs='+', help='Python file, parameters to make backup. See example.py')
args = parser.parse_args()

p_lv0('Section log')

def log_start(settings, x, cfg, backup_base, backup_log):
    '''
    mkdir path and folder of logs
    touch initial files
    return True
    '''
    p_lv1('Start')

    # log folder
    p_lv2('mkdir folder')
    backup_log = '%s/%s' % (backup_base, 'log')
    backup_log_cmd = 'mkdir -p %s' % (backup_log)
    cmd_run(backup_log_cmd)

    # log files
    p_lv2('Clean file and folder')
    clean_log = 'rm -f %s/*' % backup_log
    cmd_run(clean_log)

    p_lv2('creating files')
    log = "%s/success.log" % backup_log
    log_err = "%s/error.log" % backup_log
    log_resume = "%s/resume.log" % backup_log
    log_write(log, 'Log')
    log_write(log_err, 'Log Err')
    log_write(log_resume, 'Resume')

    return log, log_err, log_resume


def log_finish(settings, x, cfg, backup_base, backup_log):
    p_lv1('Finish')

    end_time = datetime.now()
    duration = (end_time - start_time)
    p_lv2('Start date-time: {}'.format(start_time.strftime(settings.touch_format)))
    p_lv2('End date-time: {}'.format(end_time.strftime(settings.touch_format)))
    p_lv2('Duration: {}'.format(duration))

    # touch end
    touch_log_end = "%s/%s%s" % (backup_log, settings.touch_end, end_time.strftime(settings.touch_format))
    touch_cmd = 'touch %s' % touch_log_end
    cmd_run(touch_cmd, log, log_err)

    # # # # # # # # # #
    # resume section
    cmd = 'du -sh %s' % (backup_base)
    size_base = str(os.popen(cmd).read().replace('\n',''))
    p_lv2('Backup base size: %s' % size_base)

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

    p_lv1('Send copy to')
    src = backup_log

    # connection aws s3 bucket
    if connection == 'aws-s3-bucket':
        p_lv2('connection AWS S3 Bucket')

        if x[50] == True and connection == 'aws-s3-bucket':
            p_lv2('AWS %s/%s' % (x[54],x[56]))

            # incremental
            if x[56] != False:
                p_lv2('Incremental')
                dst = u"%s/%s" % (x[56], 'log')
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
            # frequency
            if x[58] != False:
                p_lv2('Frequency')
                dst = u"%s/%s" % (x[58], 'log')
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)

    # connection rsync/copy localhost
    if x[30] == True and connection == 'rsync-copy-localhost':
        p_lv2('connection rsync/copy localhost')

        # incremental
        backup_incremental = x[34]
        if backup_incremental != False:
            p_lv3('incremental')
            dst = u"%s/%s" % (x[38], x[34])
            cmd = "%s %s %s" % (x[31], src, dst)
            p_lv3('copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

        # frequency
        backup_frequency = x[37] # path
        if backup_frequency != False:
            p_lv3('frequency')
            dst = u"%s/%s" % (x[38], backup_frequency)  # root + path
            cmd = "%s %s %s" % (x[31], src, dst)
            p_lv3('copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

    # TODO
    # connection ssh/rsync
    # connection ftp

    return True
