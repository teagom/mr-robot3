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
    print('\n> Current nice:', os.nice(0))
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
    # backup_base = '/tmp/example'

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

    # log files
    print('\n! Clean log files')
    clean_log = 'rm -f %s/*' % backup_log
    cmd_run(clean_log)

    print('\n! Creating log files')
    log = "%s/success.log" % backup_log
    log_err = "%s/error.log" % backup_log
    log_resume = "%s/resume.log" % backup_log
    log_write(log, 'Log')
    log_write(log_err, 'Log Err')
    log_write(log_resume, 'Resume')

    # touch start file
    start_time = datetime.now()
    touch_log_start = "%s/%s%s" % (backup_log, settings.touch_start, start_time.strftime(settings.touch_format))
    log_write(touch_log_start,'Start')

    # resume
    log_write(log_resume, ('Backup tmp dir: %s' % (backup_base)))
    log_write(log_resume, ('Config file   : %s' % (cfg)))
    log_write(log_resume, ('Recurrence    : %s\n' % (x[59])))

    # resume
    size_base = 0
    size_mysql = 0
    size_postgresql = 0
    size_compress = 0

    # # # # # # # # # # # # # # # # # # # # # # # #
    # dump data base and compress
    if x[10]:

        '''
        Folder struct
        backup_base       = '/tmp/example'
        backup_mysql      = '/tmp/example/db-mysql'
                                                    /db-name0.tar.gz
                                                    /db-name1.tar.gz
                                                    /db-nameN.tar.gz
        backup_postgresql = '/tmp/example/db-postgresql'
                                                    /db-name0.tar.gz
                                                    /db-name1.tar.gz
                                                    /db-nameN.tar.gz
        '''

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
            print('> Calculating backup postgresql size...', size_postgresql)


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
            print('> Calculating backup mysql size...', size_mysql)
        else:
            print('\n> No Mysql database to make backup.')


    # # # # # # # # # # # # # # # # # # # # # # # #
    # compress file and folder section
    if x[20]:
        '''
        struct of folder
        backup_base          = '/tmp/example'
        backup_compress      = '/tmp/example/compress'
        backup_compress_file = '/tmp/example/compress/home.tar.gz'
        backup_compress_file = '/tmp/example/compress/www.tar.gz'
        backup_compress_file = '/tmp/example/compress/etc.tar.gz'
        '''
        print('\n! Compress file and folder')

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
        print('> Calculating compress section size...', size_compress)


    # # # # # # # # # # # # # # # # # # # # # # # #
    # set permission
    # change permission before transfer to preserve
    # permission at remove server.
    if x[100] and x[101]:
        c = "chown %s %s -R" % (x[101], backup_base)
        cmd_run(c, log, log_err)

    if x[100] and x[102]:
        c = "chmod %s %s -R" % (x[102], backup_base)
        cmd_run(c, log, log_err)


    # # # # # # # # # # # # # # # # # # # # # # # #
    # connection rsync/copy to localhost external
    # hard disk, usb, smb mountpoint, other
    if x[30]:
        print('! Rsync to local host external hard disk')
        '''
        nao é necessario copiar em TMP para depois o destino final
        localhost pode ser copiado diretamente para o destino final
        '''

        # mkdir increment destination
        cmd_destination_backup_app = 'mkdir -p %s/%s' % (x[38], x[34])
        cmd_run(cmd_destination_backup_app, log, log_err)

        # # #
        # incremental section
        backup_incremental = False
        if x[32]:
            backup_incremental = x[34]

            # backup_base section
            if 'backup_base' in x[32]:
                x[32].remove('backup_base') # remove string

                src = backup_base # add path
                dst = backup_incremental
                log_write(log_resume, (' Connection Rsync/Copy incremental: %s' % (dst)))

                cmd = "%s %s %s/%s" % (x[31] , backup_base , x[38], x[34])
                print('\n! Copy backup: %s' % cmd)
                cmd_run(cmd, log, log_err)

            # backup_mysql section
            if 'backup_mysql' in x[32]:
                x[32].remove('backup_mysql')

                src = backup_mysql
                dst = u"%s/%s" % (backup_incremental, 'db-mysql')
                log_write(log_resume, (' Connection rsync/copy incremental: %s' % (dst)))

                #cmd = "%s %s %s" % (x[31] , backup_mysql, dst)
                cmd = "%s %s %s/%s" % (x[31] , backup_mysql, x[38], x[34])
                print('\n! Copy backup mysql: %s' % cmd)
                cmd_run(cmd, log, log_err)

            # backup_postgresq section
            # todo

            # compress section
            if 'backup_compress' in x[32]:
                x[32].remove('backup_compress')

                src = backup_compress
                dst = u"%s/%s/." % (x[38], backup_incremental)
                log_write(log_resume, (' Connection rsync/copy incremental: %s' % (dst)))

                cmd = "%s %s %s" % (x[31] , src, dst)
                print('\n! Copy backup compress: %s' % cmd)
                cmd_run(cmd, log, log_err)

            # copy others objects
            if x[32]:
                for src in x[32]:
                    dst = u"%s/%s" % (x[38], backup_incremental)
                    log_write(log_resume, ('Connection rsync/copy incremental: %s' % (dst)))

                    exclude = ""
                    for xx in x[33]:
                        exclude += "--exclude=\'%s\' " % xx

                    cmd = "%s %s %s %s" % (x[31], exclude, src, dst)
                    print('\n! Copy objects: %s' % cmd)
                    cmd_run(cmd, log, log_err)

        # # #
        # frequency section
        backup_frequency = False
        if x[35]: # not empty
            # once backup
            if x[39] == 'once':
                backup_frequency = '%s/%s/%s' % (x[38], x[37], dateformat('once', x[40]))

            # daily backup
            if x[39] == 'daily':
                backup_frequency = '%s/%s' % (x[38], x[37], dateformat('daily', x[40]))

            # weekly backup
            if x[39] == 'week-full':
                backup_frequency = '%s/%s/%s' % (x[38], x[37], dateformat('week-full', x[40]))

            # monthly backup
            if x[39] == 'month-full':
                backup_frequency = '%s/%s/%s' % (x[38], x[37], dateformat('month-full', x[40]))

            # mkdir frequency destination
            cmd = 'mkdir -p %s' % (backup_frequency)
            cmd_run(cmd, log, log_err)

            # backup_base section
            if 'backup_base' in x[35]:
                x[35].remove('backup_base') # remove string
                src = backup_base
                dst = backup_frequency
                log_write(log_resume, (' Connection Rsync/Copy frequency: %s' % (dst)))
                cmd = "%s %s/* %s/." % (x[31] , src , dst)
                print('\n! Copy backup: %s' % cmd)
                cmd_run(cmd, log, log_err)


            # backup_mysql section
            if 'backup_mysql' in x[35]:
                x[35].remove('backup_mysql')

                src = backup_mysql
                dst = u"%s/%s" % (backup_frequency, 'db-mysql')

                cmd = 'mkdir -p %s' % (dst)
                cmd_run(cmd, log, log_err)

                log_write(log_resume, (' Connection rsync/copy frequency: %s' % (dst)))
                cmd = "%s %s %s" % (x[31] , backup_mysql, dst)
                print('\n! Copy backup mysql: %s' % cmd)
                cmd_run(cmd, log, log_err)

            # backup_postgresq section
            # todo

            # compress section
            if 'backup_compress' in x[32]:
                x[32].remove('backup_compress')
                src = backup_compress
                dst = u"%s/%s/." % (x[38], backup_frequency)
                log_write(log_resume, (' Connection rsync/copy incremental: %s' % (dst)))

                cmd = "%s %s %s" % (x[31] , src, dst)
                print('\n! Copy backup compress: %s' % cmd)
                cmd_run(cmd, log, log_err)

            # copy others objects
            if x[32]:
                for src in x[32]:
                    dst = u"%s/%s" % (x[38], backup_incremental)
                    log_write(log_resume, ('Connection rsync/copy incremental: %s' % (dst)))

                    exclude = ""
                    for xx in x[33]:
                        exclude += "--exclude=\'%s\' " % xx

                    cmd = "%s %s %s %s" % (x[31], exclude, src, dst)
                    print('\n! Copy objects: %s' % cmd)
                    cmd_run(cmd, log, log_err)


    # # # # # # # # # # # # # # # # # # # # # # # #
    # ssh/rsync to remote server
    if x[40]:
        print('\n! Rsync / ssh to remote server')

        if x[45] == "password":
            rsync = "sshpass -p \"%s\" rsync %s -e \"ssh -p %s\" %s %s@%s:%s" % ( x[48] , x[44] , x[42] , backup_base , x[47] , x[41] , x[43] )

        if x[45] == "pemfile":
            rsync = "rsync %s -e \"ssh -p %s -i %s\" %s %s@%s:%s" % ( x[44] , x[42] , x[46] , backup_base , x[47] , x[41] , x[43] )

        if x[45] == "authorized":
            rsync = "rsync %s -e \"ssh -p %s \" %s %s@%s:%s" % ( x[44] , x[42] , backup_base , x[47] , x[41] , x[43] )

        cmd_run(rsync, log, log_err)
        log_write(log_resume, ('Backup rsync: %s' % (backup_base)))


    # # # # # # # # # # # # # # # # # # # # # # # #
    # aws s3 bucket
    if x[50]:
        print('\n! AWS S3 Bucket')
        log_write(log_resume, ('AWS s3 bucket     : %s' % (x[54])))

        '''
        command
            # output s3://bucket-name/incremental
            # output s3://bucket-name/<frequency>

        backup_base          = '/tmp/example'
        backup_compress      = '/tmp/example/compress'
        backup_compress_file = '/tmp/example/compress/home.tar.gz'
        backup_compress_file = '/tmp/example/compress/www.tar.gz'
        backup_compress_file = '/tmp/example/compress/etc.tar.gz'
        '''
        # # # # # # # #
        # aws s3 incremental section
        backup_incremental = False
        if x[55]:
            backup_incremental = x[56]

            # aws incremental + backup_base
            if 'backup_base' in x[55]:
                x[55].remove('backup_base') # remove string

                src = backup_base # add path
                dst = backup_incremental
                log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup base to AWS S3 Bucket: %s' % backup_base)

            # aws + incremental + backup_mysql
            if 'backup_mysql' in x[55]:
                x[55].remove('backup_mysql')

                src = backup_mysql
                dst = u"%s/%s" % (backup_incremental, 'db-mysql')
                log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup mysql to AWS S3 Bucket: %s' % backup_mysql)

            # aws + incremental + backup_postgresql
            # todo

            # incremental + compress
            if 'backup_compress' in x[55]:
                x[55].remove('backup_compress')

                src = backup_compress
                dst = u"%s/%s" % (backup_incremental, 'compress')
                log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup compress to AWS S3 Bucket: %s' % backup_compress)

            # copy others objects to AWS
            if x[55]:
                for src in x[55]:
                    # src must have full path, start /
                    dst = u"%s%s" % (backup_incremental, src)
                    log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                    cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                    cmd_run(cmd_aws, log, log_err)
                    print('\n! Copy other backup to AWS S3 Bucket: %s' % src)


        # # # # # # # # # # # # #
        # aws frequency section
        backup_frequency = False
        if x[57]: # to check not empty src list

            # once backup
            if x[59] == 'once':
                backup_frequency = '%s/%s' % (x[58], dateformat('once'), x[60])

            # daily backup
            if x[59] == 'daily':
                backup_frequency = '%s/%s' % (x[58], dateformat('daily'), x[60])

            # weekly backup
            if x[59] == 'week-full':
                backup_frequency = '%s/%s' % (x[58], dateformat('week-full'), x[60])

            # monthly backup
            if x[59] == 'month-full':
                backup_frequency = '%s/%s' % (x[58], dateformat('month-full'), x[60])

            # frequency + base
            if 'backup_base' in x[57]:
                x[57].remove('backup_base') # remove string
                src = backup_base
                dst = backup_frequency
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup base to AWS S3 Bucket: %s' % backup_base)

            # frequency + mysql
            if 'backup_mysql' in x[57]:
                x[57].remove('backup_mysql')
                src = backup_mysql
                dst = u"%s/%s" % (backup_frequency, 'db-mysql')
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup mysql to AWS S3 Bucket: %s' % backup_mysql)

            # frequency + compress
            if 'backup_compress' in x[57]:
                x[57].remove('backup_compress')

                src = backup_compress
                dst = u"%s/%s" % (backup_frequency, 'compress')
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                print('\n! Copy backup compress to AWS S3 Bucket: %s' % backup_compress)

            # frequency + postgresql
            if 'backup_postgresql' in x[57]:
                x[57].append(backup_postgresql)
                x[57].remove('backup_postgresql')

            # copy others objects to AWS
            if x[57]:
                for src in x[57]:
                    print('\n! Copy other backup to AWS S3 Bucket: %s' % src)
                    # src must have full path, start /
                    dst = u"%s%s" % (backup_frequency, src)
                    log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                    cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                    cmd_run(cmd_aws, log, log_err)

    # end date-time
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
    cmd = 'du -sh %s' % (backup_base)
    size_base = str(os.popen(cmd).read().replace('\n',''))
    print('> Calculating backup base size...', size_base)

    log_write(log_resume, ('\nSize mysql     : %s' % (size_mysql)))
    log_write(log_resume, ('Size postgresql: %s' % (size_postgresql)))
    log_write(log_resume, ('Size compress  : %s' % (size_compress)))
    log_write(log_resume, ('Size total     : %s\n' % (size_base)))
    log_write(log_resume, ('Start   : %s' % (start_time)))
    log_write(log_resume, ('Finish  : %s' % (end_time)))
    log_write(log_resume, ('Duration: %s' % (duration)))

    # # # # # # # # # #
    # log section

    # connection aws
    if x[50]:
        # incremental
        if backup_incremental != False:
            msg = ('! AWS copy log files to %s/%s' % (x[54],x[56]))
            print('\n'+msg)
            src = backup_log
            dst = u"%s/%s" % (x[56], 'log')
            cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
            cmd_run(cmd_aws, log, log_err)

        # frequency
        if backup_frequency != False:
            msg = ('! AWS copy log files to %s/%s frequency' % (x[54],x[56]))
            print('\n'+msg)
            src = backup_log
            dst = u"%s/%s" % (backup_frequency, 'log')
            cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
            cmd_run(cmd_aws, log, log_err)


    # connection rsync/copy log
    if x[20]:
        # incremental
        if backup_incremental != False:
            src = backup_log
            dst = u"%s/%s" % (x[38], x[34])
            cmd = "%s %s %s" % (x[31], src, dst)
            print('\n! Copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

        # frequency
        if backup_frequency != False:
            src = backup_log
            dst = u"%s/%s" % (x[38], x[34])
            cmd = "%s %s %s" % (x[31], src, dst)
            print('\n! Copy objects: %s' % cmd)
            cmd_run(cmd, log, log_err)

    # todo
    # connection ssh/rsync
    # connection ftp

    # # # # # # # # # #
    # sendmail report section
    # if log.err not empty then sendmail to report
    if x[3] == True and not os.stat("%s" % log_err).st_size == 0:
        msg = ('! Send backup report mail to admin')
        print('\n'+msg)
        log_write(log, msg)
        sendmail(x[4], x[0], x[5], log_err, log, False, log_resume)


    # # # # # # # # # #
    # delete after read log files
    if x[1] == True:
        msg = ('! Delete temporary folder or external disk backup')
        print('\n'+msg)
        log_write(log, msg)
        clean = 'rm -rf %s' % (backup_base)
        cmd_run(clean, log, log_err)
