#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys, argparse, settings, os
from slugify import slugify
from datetime import datetime
from external import cmd_run, sendmail, log_write, mysqlshow, p_lv0, p_lv2

parser = argparse.ArgumentParser()
parser.add_argument('integers', metavar='file.py', type=str, nargs='+', help='Python file, parameters to make backup. See example.py')
args = parser.parse_args()


# main code
for cfg in args.integers:

    # import
    module = __import__(cfg.replace('.py', ''))
    x = module.config

    print()
    print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # #')
    print('# Mr Robot3 Backup. Dump DBs, comppress and incremental #')
    print('# Running %s ' % cfg)
    print('# # # # # # # # # # # # # # # # # # # # # # # # # # # # #')

    # avoid to use 100% of CPU, set NICE at settings.
    # set os.nice()
    print('\n! Current nice:', os.nice(0))
    if settings.nice:
        os.nice(settings.nice) # set new nice
        print('> New nice:', os.nice(0)) # get nice

    # test smtp
    if settings.smtp_test:
        print('\n! Testing SMTP settings...')
        sendmail(x[4], x[0], False, False, False, True, False)
        sys.exit('> Break script. Set SMTP test to False to continue.')

    # # # # # # # # # # # # # # # # # # # # # # # #
    # create destination folder and logs
    # root folder to app backup
    # *** WARNING! CAN NOT BE '/' , can delete ALL servers FILE!
    # default '/tmp'

    backup_base = '%s/%s' % (x[2], x[0])

    if x[2] == '/' or x[2] == '' or not backup_base:
        sys.exit('> *** WARNING! Backup base dir config[2] can not be / or empty!')

    if x[0] == '/' or x[0] == '' or not backup_base:
        sys.exit('> *** WARNING! Backup base dir config[0] can not be / or empty!')

    if backup_base == '/' or backup_base == '' or not backup_base:
        sys.exit('> *** WARNING! Backup base dir can not be / or empty!')

    # create a temporary app backup folder
    print('\n! Creating backup folder struct: %s' % backup_base)
    backup_base_cmd = 'mkdir -p %s' % (backup_base)
    cmd_run(backup_base_cmd)

    # log folder
    backup_log = '%s/%s' % (backup_base, 'log')
    backup_log_cmd = 'mkdir -p %s' % (backup_log)
    cmd_run(backup_log_cmd)

    from parts.log import log_start
    log, log_err, log_resume = log_start(settings, x, cfg, backup_base, backup_log)

    # resume
    log_write(log_resume, ('Backup tmp dir: %s' % (backup_base)))
    log_write(log_resume, ('Config file   : %s' % (cfg)))
    log_write(log_resume, ('Recurrence    : %s\n' % (x[59])))
    # resume
    size_base = 0
    size_mysql = 0
    size_postgresql = 0
    size_compress = 0

    # touch start file
    start_time = datetime.now()
    touch_log_start = "%s/%s%s" % (backup_log, settings.touch_start, start_time.strftime(settings.touch_format))
    log_write(touch_log_start,'Start')

    # Set all sections to False
    backup_compress = False
    backup_mysql =  False
    backup_postgresql =  False

    # # #
    # dump data base and compress
    if x[10]:
        print('\n! Backup Data Base')

        # postgres
        if x[11] == 'postgres':
            print('\n! PostgreSQL: Dump and compress')

            # DB backup file name
            outputfile_db_tmp = u'%s/db.sql' % (destiny_backup_app)
            outputfile_db = u'%s/db.%s' % (destiny_backup_app, x[6])

            dump = 'export PGPASSWORD=%s\npg_dump --username=%s -h %s %s > %s' % (x[15], x[14], x[12], x[13], outputfile_db_tmp)

            # size
            cmd = 'du -sh %s' % (backup_postgresql)
            size_postgresql = str(os.popen(cmd).read().replace('\n',''))
            p_lv2('Calculating backup postgresql size:%s' % size_postgresql)


        # mysql
        if x[11] == 'mysql':
            print('\n! Mysql: Dump and compress')

            dest = 'db-mysql'  # TODO: add to settings, custom folder name
            backup_mysql = '%s/%s' % (backup_base, dest)
            cmd_backup_mysql = 'mkdir -p %s' % (backup_mysql)
            cmd_run(cmd_backup_mysql)

            # to check 'ALL' at postion zero of array
            if x[13][0] == 'ALL':
                db_list = mysqlshow(log, log_err, x[17])
            else:
                db_list = x[13] # list of DB names, array.

            # make backup of database list of not empty
            if db_list:
                for db in db_list:
                    # backup DB, output dbname.sql.
                    outputfile_db_tmp = u'%s/%s.sql' % (backup_mysql, db)
                    mysqldump_cmd = 'mysqldump --defaults-extra-file=%s -h %s %s --result-file=%s' % (x[16], x[12], db, outputfile_db_tmp)
                    cmd_run(mysqldump_cmd, log, log_err)

                    # compact sql file
                    # output dbname.tar.gz
                    outputfile_db = u'%s/%s.%s' % (backup_mysql, db, x[6])
                    compact = '%s %s %s %s' % (x[7], x[8], outputfile_db, outputfile_db_tmp)
                    # lixo final code
                    cmd_run(compact, log, log_err)

                    # delete sql tmp file
                    cmd_run('rm -f %s' % (outputfile_db_tmp), log, log_err)

                    # test tar.gz file
                    if x[9]:
                        test_cmd = '%s %s' % (x[9], outputfile_db)
                        cmd_run(test_cmd, log, log_err)

            # mysql size
            cmd = 'du -sh %s' % (backup_mysql)
            size_mysql = str(os.popen(cmd).read().replace('\n',''))
            p_lv2('Calculating backup mysql size: %s' % size_mysql)
        else:
            p_lv2('No Mysql database to make backup.')


    # # #
    # compress file and folder section
    if x[20]:
        print('\n! Compress Section file and folder')

        dest = 'compress'
        backup_compress = '%s/%s' % (backup_base, dest)
        backup_compress_cmd = 'mkdir -p %s' % (backup_compress)
        cmd_run(backup_compress_cmd)

        # exclude list
        exclude = ''
        for xx in x[22]:
            exclude += "--exclude=\"%s\" " % xx

        # include list
        for xx in x[21]:
            include = "%s" % xx
            name = slugify(xx)

            # output file
            backup_compress_file = u'%s/%s.%s' % (backup_compress, name, x[6])
            compress_cmd = "%s %s %s %s %s" % (x[7], exclude, x[8], backup_compress_file, include)
            cmd_run(compress_cmd, log, log_err)

            if x[9]:
                test = '%s %s' % (x[9], backup_compress_file)
                cmd_run(test, log, log_err)

        # size
        cmd = 'du -sh %s' % (backup_compress)
        size_compress = str(os.popen(cmd).read().replace('\n',''))
        p_lv2('Calculating compress section size: %s' % size_compress)


    # # #
    # set permission
    # change permission before transfer to preserve
    # permission at remove server.
    if x[100] and x[101]:
        c = "chown %s %s -R" % (x[101], backup_base)
        cmd_run(c, log, log_err)

    if x[100] and x[102]:
        c = "chmod %s %s -R" % (x[102], backup_base)
        cmd_run(c, log, log_err)

    # # #
    # connection
    # rsync copy localhost
    from parts.rsync_copy_localhost import rsync_copy_localhost
    rsync_copy_localhost(x, log, log_err, log_resume, backup_base, backup_mysql, backup_compress)
    # aws s3 bucket
    from parts.aws_s3_bucket import aws_s3_bucket
    aws_s3_bucket(x, log, log_err, log_resume, backup_base, backup_mysql, backup_compress)
    # ssh-rsync
    from parts.ssh_rsync import ssh_rsync
    ssh_rsync(x, log, log_err, log_resume, backup_base, backup_mysql, backup_compress)

    # # #
    # resume end
    from parts.resume import resume_finish
    end_time, duration = resume_finish(settings, log, log_err, backup_base, backup_log, start_time)
    # write resume to log
    log_write(log_resume, ('\nSize mysql     : %s' % (size_mysql)))
    log_write(log_resume, ('Size postgresql: %s' % (size_postgresql)))
    log_write(log_resume, ('Size compress  : %s' % (size_compress)))
    log_write(log_resume, ('Size total     : %s\n' % (size_base)))
    log_write(log_resume, ('Start   : %s' % (start_time)))
    log_write(log_resume, ('Finish  : %s' % (end_time)))
    log_write(log_resume, ('Duration: %s' % (duration)))

    # # #
    # log section
    from parts.log import log_send_copy_to
    log_send_copy_to(x, log, log_err, backup_log, 'aws-s3-bucket')
    log_send_copy_to(x, log, log_err, backup_log, 'rsync-copy-localhost')

    # # #
    # sendmail report section
    # if log.err not empty then sendmail to report
    if x[3] == True and not os.stat("%s" % log_err).st_size == 0:
        msg = ('Send backup report mail to admin')
        p_lv0(msg)
        log_write(log, msg)
        sendmail(x[4], x[0], x[5], log_err, log, False, log_resume)

    # # #
    # delete after read log files
    if x[1] == True:
        msg = ('Delete temporary folder or external disk backup')
        p_lv0(msg)
        log_write(log, msg)
        clean = 'rm -rf %s' % (backup_base)
        cmd_run(clean)
