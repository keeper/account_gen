#!/usr/bin/python3
import argparse
import pathlib
import os

MIN_ID = 10000
MAX_ID = 30000
GID = 10000


def usage_msg():
    return '''\
  This script creates user account against
  the user_list put into the course directory.

  COURSE dir is located at ./courses/COURSE
  COURSE dir must be created with following files:

  user_list: The student id list.

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


def main():
    # check opt
    parser = argparse.ArgumentParser(
        description='Creates user account',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=usage_msg())

    parser.add_argument('course', metavar='COURSE', type=str, nargs=1,
                        help='course name directory')

    args = parser.parse_args()

    # open file
    course = args.course[0]
    course_dir = './courses/' + course
    user_list = course_dir + '/user_list'
    ta_list = course_dir + '/ta_list'

    uid = get_max_uid(MIN_ID, MAX_ID) + 1

    with open(user_list) as f:
        for line in f:
            stu_id = ''
            email = '@student.nsysu.edu.tw'
            try:
                stu_id, email = line.strip().split()
            except:
                stu_id = line.strip()
                email = stu_id + email
            # TODO: create account
            cmd = 'useradd -m -d /home/{0}/{1} -g {2} -u {3} {1}'.format(
                  course, stu_id, GID, uid)
            print (cmd)
            uid = uid + 1

    with open(ta_list) as f:
        for line in f:
            ta_id, email = line.strip().split()
            # TODO: mail to TA


if __name__ == "__main__":
    main()
