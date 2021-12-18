# -*- coding: utf-8 -*-

from settings import model, email_subject
import copy

# # # # # # # # # # # # # # # # # # # # # # # #
# set app array
# # # # # # # # # # # # # # # # # # # # # # # #

config = copy.deepcopy(model)

# # # step 0 - global variables of backup
'''
environment variables
backup_base       = '/tmp/example-server'
if you include base, you dont need include sub folder/files, recursive mode on!

'''
config[0] = 'example-server'# name of config or app (string) Will be used to create a folder backup name
config[1] = False           # delete local/temporary backup after copy to remote server (True|False)
config[2] = '/tmp'          # full path to backup temporary folder

config[3] = False # sendmail after finish backup, log and log.err in attach.
config[4] = ['admin@mail.com','webmaster@mail.com'] # array of email adress
config[5] = '%s %s' % (email_subject, config[0]) # Email subject

# options to compact file and dump of data base
config[6] = 'tar.gz'    # extension (string)
config[7] = '/bin/tar'  # full path to binary (string)
config[8] = '-cvzf'     # parameters to compress, better, faster, recursive, ...
config[9] = '/bin/gunzip -tv'   # full path to binary (string)
                                # parameters to check (t) verbose (v), insert password if protected

# # #
# section MySQL
'''
set this file if to make backup of MySQL DBs: ~/.my.cnf
https://dev.mysql.com/doc/refman/5.7/en/option-files.html
https://dev.mysql.com/doc/refman/8.0/en/option-files.html

chmod 600 ~/.my.cnf

content of file
    [mysqldump]
    user=root
    password=root-password

    # if config[13] = 'ALL', add lines:
    [mysqlshow]
    user=root
    password=root-password
'''
config[10] = False      # backup mysql (True|False)
config[11] = 'mysql'    # db server (mysql)
config[12] = '127.0.0.1'# host
config[13] = [None]     # if value is equal 'ALL', sensitive case!
                        # string ALL : all databases but you can ignore
                        # ignore list: array ['DataBase0','DataBase1',...]
                        # output: /tmp/example/mysql/database-name.tar.gz
config[14] = 'root' # user
config[15] = 'pass' # pass
config[16] = '~/.my.cnf' # config file to dump
config[17] = ['Database','sys','performance_schema','information_schema'] # ignore these databases, databases default
# end mysql


# # #
# compress section
config[20] = False # compact file and folder, recursive mode on.
config[21] = ['/etc/ssh/','/etc/samba/','/etc/apache2','/etc/mysql'] # include folder or file
config[22] = [] # do not include folder or file, https://man7.org/linux/man-pages/man1/tar.1.html
# end compress


# # #
# connection rsync/copy to localhost external disk, usb, smb mountpoint, others
config[30] = False # (True|False)
config[31] = '/usr/bin/rsync -avz -progress -partial' # binary and parameters
# incremental
config[32] = ['backup_base'] # source
config[33] = []              # do not include folder or file
config[34] = 'backup/incremental' # destination folder name
# frequency
config[35] = ['backup_base'] # source
config[36] = []              # not include
config[37] = 'backup/frequency' # destination folder name
# root / frequnecy / hour
config[38] = '/media/storage1' # root path
config[39] = 'week-full' # frequency of backup (once|daily|week-full|month-full)
config[40] = '01h13' # hour
# end rsync/copy


# # #
# connection aws s3 bucket
# copy backup to aws s3 bucket
config[50] = False                  # copy backup to remote host using aws s3 cp or custom parameters
config[51] = '/usr/local/bin/aws'   # path to binary
config[52] = 's3 sync'              # operator (string), cp, rm, sync, ls, see man aws s3 help
config[53] = '--storage-class STANDARD_IA' # aws s3 OP + parameters (string), --recursive
config[54] = 's3://aws-bucket-name' # s3 bucket name (string)
# incremental
config[55] = ['backup_base'] # source
config[56] = 'backup/incremental' # destination incremental
# frequency
config[57] = ['backup_base'] # list of objects
config[58] = 'backup/frequency' # destination folder at bucket
config[59] = 'week-full' # frequency of backup (once|daily|week-full|month-full)
config[60] = '8h00' # time. Crontab maybe can be variable minuites
# end connection aws s3 bucket


# # #
# connection ssh/rsync, copy backup_base to remote server
config[70] = True # copy backup to remote host using rsync ssh (True|False)
config[71] = '192.168.225.10' # server ip or hostname (string)
config[72] = '22' # ssh port (string)
config[73] = '/home/backup/home-users'   # destiny folder in the remote server (string)
config[74] = '-arvz --progress --partial' # rsync parameters (string)
config[75] = 'authorized' # authentication type (string), (password|pemfile|authorized)
# password - First connection have to be confirmed written "yes" in a command line.
# sshpass are required - $ sudo apt-get install sshpass
# ssh -p 222 backup@192.168.0.254
# The authenticity of host '([192.168.0.254]:222)' can't be established.
# ECDSA key fingerprint is bb:ee:cc:ee:aa:ff:gg.
# Are you sure you want to continue connecting (yes/no)?
config[76] = '/opt/server-pem-2015.pem' # pem file if [45] is pemfile (string)
config[77] = 'backup' # user (string) is required for any [45] option
config[78] = 'password' # password (string)
# incremental
config[80] = 'password' # password (string)
# frequency
config[86] = 'password' # password (string)
# end ssh/rsync


# # #
# section permission
config[100] = False
config[101] = 'user:group' # (string) owner:group for root backup folder, full path to and recursive mode
config[102] = '700' # (string) chmod for root backup folder.
# end
