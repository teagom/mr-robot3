import re
import sys, argparse, settings, os
from slugify import slugify
from datetime import datetime
from external import cmd_run, sendmail, dateformat, log_write,\
        mysqlshow

print('\n! Section resume')

def resume_finish(settings, log, log_err, backup_base, backup_log, start_time):
    print('  finish')
    # end date-time
    end_time = datetime.now()
    duration = (end_time-start_time)
    print('  start date-time: {}'.format(start_time.strftime(settings.touch_format)))
    print('  finish date-time: {}'.format(end_time.strftime(settings.touch_format)))
    print('  duration: {}'.format(duration))

    # touch end
    touch_log_end = "%s/%s%s" % (backup_log, settings.touch_end, end_time.strftime(settings.touch_format))
    touch_cmd = 'touch %s' % touch_log_end
    cmd_run(touch_cmd, log, log_err)

    # # # # # # # # # #
    # resume section
    cmd = 'du -sh %s' % (backup_base)
    size_base = str(os.popen(cmd).read().replace('\n',''))
    print('  calculating backup base size...', size_base)

    return end_time, duration
