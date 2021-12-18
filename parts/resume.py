# -*- coding: utf-8 -*-

import os
from datetime import datetime
from external import cmd_run, p_lv1, p_lv2

print('\n! Section resume')

def resume_finish(settings, log, log_err, backup_base, backup_log, start_time):
    end_time = datetime.now()
    duration = (end_time-start_time)
    p_lv1('start date-time: {}'.format(start_time.strftime(settings.touch_format)))
    p_lv1('finish date-time: {}'.format(end_time.strftime(settings.touch_format)))
    p_lv1('duration: {}'.format(duration))

    # touch end
    touch_log_end = "%s/%s%s" % (backup_log, settings.touch_end, end_time.strftime(settings.touch_format))
    touch_cmd = 'touch %s' % touch_log_end
    cmd_run(touch_cmd, log, log_err)

    # resume section
    cmd = 'du -sh %s' % (backup_base)
    size_base = str(os.popen(cmd).read().replace('\n',''))
    p_lv2('calculating backup base size: %s' % size_base)

    return end_time, duration
