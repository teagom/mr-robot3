# -*- coding: utf-8 -*-

from external import cmd_run, dateformat, log_write, p_lv0, p_lv1

# connection aws s3 bucket

p_lv0('Connection AWS S3 Bucket')

def aws_s3_bucket(x,log,log_err, log_resume, backup_base, backup_mysql, backup_compress):
    if x[50]:
        log_write(log_resume, ('AWS s3 bucket     : %s' % (x[54])))

        # # # # # # # #
        # aws s3 incremental section
        backup_incremental = False
        if x[55]:
            p_lv1('Incremental format')
            backup_incremental = x[56]

            # aws incremental + backup_base
            if 'backup_base' in x[55]:
                x[55].remove('backup_base') # remove string

                src = backup_base # add path
                dst = backup_incremental
                log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                p_lv1('Copy backup base to: %s' % backup_base)

            # aws + incremental + backup_mysql
            if 'backup_mysql' in x[55]:
                x[55].remove('backup_mysql')

                src = backup_mysql
                dst = u"%s/%s" % (backup_incremental, 'db-mysql')
                log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                p_lv1('backup mysql. Copy to AWS S3 Bucket: %s' % backup_mysql)

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
                p_lv1('compress - copy to %s' % x[54])

            # copy others objects to AWS
            if x[55]:
                for src in x[55]:
                    # src must have full path, start /
                    dst = u"%s%s" % (backup_incremental, src)
                    log_write(log_resume, ('AWS s3 incremental: %s' % (dst)))

                    cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                    cmd_run(cmd_aws, log, log_err)
                    p_lv1('Copy %s to %s' % (src, x[54]))


        # # # # # # # # # # # # #
        # aws frequency section
        backup_frequency = False
        if x[57]: # to check not empty src list
            p_lv1('Frequency format')

            # once backup
            if x[59] == 'once':
                backup_frequency = '%s/%s' % (x[58], dateformat('once', x[60]))

            # daily backup
            if x[59] == 'daily':
                backup_frequency = '%s/%s' % (x[58], dateformat('daily', x[60]))

            # weekly backup
            if x[59] == 'week-full':
                backup_frequency = '%s/%s' % (x[58], dateformat('week-full', x[60]))

            # monthly backup
            if x[59] == 'month-full':
                backup_frequency = '%s/%s' % (x[58], dateformat('month-full', x[60]))

            # frequency + base
            if 'backup_base' in x[57]:
                x[57].remove('backup_base') # remove string
                src = backup_base
                dst = backup_frequency
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                p_lv1('Copy backup base to: %s' % x[54])

            # frequency + mysql
            if 'backup_mysql' in x[57]:
                x[57].remove('backup_mysql')
                src = backup_mysql
                dst = u"%s/%s" % (backup_frequency, 'db-mysql')
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                p_lv1('Copy backup MySQL to: %s' % x[54])

            # frequency + compress
            if 'backup_compress' in x[57]:
                x[57].remove('backup_compress')
                src = backup_compress
                dst = u"%s/%s" % (backup_frequency, 'compress')
                log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                cmd_run(cmd_aws, log, log_err)
                p_lv1('Copy backup compress to %s' % x[54])

            # frequency + postgresql
            if 'backup_postgresql' in x[57]:
                x[57].append(backup_postgresql)
                x[57].remove('backup_postgresql')

            # copy others objects to AWS
            if x[57]:
                for src in x[57]:
                    p_lv1('Copy %s to:' % src)
                    dst = u"%s%s" % (backup_frequency, src)
                    log_write(log_resume, ('AWS s3 frequency  : %s' % (dst)))
                    cmd_aws = "%s %s %s %s %s/%s" % (x[51], x[52], x[53], src, x[54], dst)
                    cmd_run(cmd_aws, log, log_err)

