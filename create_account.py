#!/usr/bin/python3
import argparse
import pathlib
import os
import random
import string
import mailer
import sys
import time

MIN_ID = 10000
MAX_ID = 30000
GID = 10000
IMAGE_NAME = 'ubuntu-gccv2:14.04'
PASS_SIZE = 6


def usage_msg():
    return '''\
  This script creates user account against
  the user_file put into the course directory.

  COURSE dir is located at ./courses/COURSE
  COURSE dir must be created with following files:

  user_file: The student id list.

      Custom e-mail address may entered into
      this file also.
      If custom e-mail address is not specified
      e-mail "STUDENT_ID@student.nsysu.edu.tw"
      is used.

      The syntax is:
          STUDENT_ID [E-MAIL]
      Example:
          m963040003
          m963040004
          m963040005 cooldavid@gmail.com
          m963040006

  ta_list: The TA name and e-mail list.

      The syntax is:
          E-MAIL TA_NAME
      Example:
          m973040002@student.nsysu.edu.tw Wei-Min,Chen
          cooldavid.ta@cooldavid.org Guo-Fu,Tseng
          chungfu27@hotmail.com Chung-Fu

    '''


def send_mail(username, passwd, ta_list, dst_mail, dryrun):
    ta_mail_list = ['"{1}" <{0}>'.format(_[0], _[1]) for _ in ta_list]
    message = mailer.Message(From=ta_mail_list[0],
                             To=dst_mail,
                             CC=ta_mail_list)
    subject = 'New password for ' + username
    body = ('We have setup a new account for {0} on OSLab Homework server\n'
            'Server address: hw.oslab.cse.nsysu.edu.tw.\n'
            'Your account: {0}\n'
            'Your new password: {1}\n').format(username, passwd)
    message.Subject = subject
    message.Body = body
    print ('Sending mail to ' + username)
    if not dryrun:
        mailer.Mailer().send(message)
        # sleep for a few seconds after send mail
        time.sleep(3)
    return


def get_max_uid(min_id, max_id):
    uid_list = []
    with open('/etc/passwd') as f:
        for line in f:
            uid = int(line.split(':')[2])
            if uid >= min_id and uid <= max_id:
                uid_list.append(uid)
    if not uid_list:
        return min_id
    return max(uid_list)


def create_user(user_file, ta_list, course_name, start_uid, dryrun):
    uid = start_uid
    user_list = []
    with open(user_file) as f:
        for line in f:
            stu_id = ''
            email = '@student.nsysu.edu.tw'
            try:
                stu_id, email = line.strip().split()
            except:
                stu_id = line.strip()
                email = stu_id + email
            # create account
            user_home = '/home/{0}/{1}'.format(course_name, stu_id)
            bash_file = user_home + '/.bashrc'
            create_cmd = 'useradd -m -d {0} -u {1} -g {2} {3}'.format(
                user_home, uid, GID, stu_id)
            # inject docker command
            docker_cmd = '"docker run -t -i -v {0}:/home/user {1} /bin/bash"'.format(
                         user_home, IMAGE_NAME)
            docker_cmd = 'echo {0} >> {1}'.format(docker_cmd, bash_file)
            uid = uid + 1
            # create password
            passwd = ''.join(random.choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits)
                for _ in range(PASS_SIZE))
            passwd_cmd = 'echo -e "{0}:{1}" | chpasswd'.format(stu_id, passwd)
            user_list.append((stu_id, passwd))
            if dryrun:
                print (create_cmd)
                print (docker_cmd)
                print (passwd_cmd)
            else:
                os.system('{0} && {1} && {2}'.format(
                    create_cmd, docker_cmd, passwd_cmd))
            send_mail(stu_id, passwd, ta_list, email, dryrun)

    return user_list


def get_ta_list(ta_file):
    ta_list = []
    with open(ta_file) as f:
        for line in f:
            email, ta_id = line.strip().split()
            ta_list.append((email, ta_id))
    return ta_list


def create_pass_file(pass_file, user_list):
    with open(pass_file, 'w') as f:
        for user, passwd in user_list:
            f.write('{0} {1}\n'.format(user, passwd))


def main():
    # check opt
    parser = argparse.ArgumentParser(
        description='Creates user account',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage_msg())

    parser.add_argument('course', metavar='COURSE', type=str, nargs=1,
                        help='course name directory')

    parser.add_argument('-d', '--dryrun', default=False, action='store_true',
                        help='dry run, output running command and do nothing')

    args = parser.parse_args()
    if os.geteuid() != 0 and not args.dryrun:
        print ("Please use root to run this script")
        return -1

    # open file
    course = args.course[0]
    course_dir = './courses/' + course
    user_file = course_dir + '/user_list'
    ta_file = course_dir + '/ta_list'
    pass_file = course_dir + '/pass'

    uid = get_max_uid(MIN_ID, MAX_ID) + 1
    ta_list = get_ta_list(ta_file)
    user_list = create_user(user_file, ta_list, course, uid, args.dryrun)
    if not args.dryrun:
        create_pass_file(pass_file, user_list)


if __name__ == "__main__":
    main()
