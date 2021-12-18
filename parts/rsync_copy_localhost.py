from external import cmd_run, dateformat, log_write

# connection rsync/copy to localhost external
# hard disk, usb, smb mountpoint, other

def rsync_copy_localhost(x, log, log_err, log_resume,backup_base, backup_mysql, backup_compress):
    if x[30]:
        print('! Rsync to local host external hard disk')
        '''
        nao é necessario copiar em TMP para depois o destino final
        localhost pode ser copiado diretamente para o destino final
        '''
        # mkdir increment destination
        cmd_destination_backup_app = 'mkdir -p %s/%s' % (x[38], x[34])
        cmd_run(cmd_destination_backup_app, log, log_err)

        # incremental format
        # all sections
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


        # frequency format
        # all sections
        backup_frequency = False
        if x[35]: # not empty

            # set frequency
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

    return True
