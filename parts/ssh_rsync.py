# -*- coding: utf-8 -*-

from external import cmd_run, log_write, p_lv0, p_lv1

def ssh_rsync(x, log, log_err, log_resume, backup_base, backup_mysql, backup_compress):
    p_lv0('Connection ssh/rsync')

    if x[70]: # method
        if x[75] == "password":
            p_lv1('Password authentication')
            cmd = "sshpass -p \"%s\" rsync %s -e \"ssh -p %s\" %s/* %s@%s:%s/." % (x[78], x[74], x[72], backup_base, x[77], x[71], x[73] )

        if x[75] == "pemfile":
            p_lv1('Pem file authentication')
            cmd = "rsync %s -e \"ssh -p %s -i %s\" %s/* %s@%s:%s/." % (x[74], x[72], x[46], backup_base, x[77], x[71], x[73])

        if x[75] == "authorized":
            p_lv1('Authorized / PubKey authentication')
            cmd = "rsync %s -e \"ssh -p %s \" %s/* %s@%s:%s/." % (x[74], x[72], backup_base, x[77], x[71], x[73])

        cmd_run(cmd, log, log_err)
        log_write(log_resume, ('output %s' % cmd))
