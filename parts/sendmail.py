def sendmail():
    # # # # # # # # # #
    # sendmail report section
    # if log.err not empty then sendmail to report
    if x[3] == True and not os.stat("%s" % log_err).st_size == 0:
        msg = ('! Send backup report mail to admin')
        print('\n'+msg)
        log_write(log, msg)
        sendmail(x[4], x[0], x[5], log_err, log, False, log_resume)


def finish():
    # # # # # # # # # #
    # delete after read log files
    if x[1] == True:
        msg = ('! Delete temporary folder or external disk backup')
        print('\n'+msg)
        log_write(log, msg)
        clean = 'rm -rf %s' % (backup_base)
        cmd_run(clean, log, log_err)
