from collections import namedtuple

import datetime
import os
import re

from lib.components import shared


SSHKey = namedtuple('SSHKey', ['file', 'type', 'fingerprint', 'size'])
SSHSession = namedtuple('SSHSession', ['username', 'active_since', 'ip'])


def _GenerateSSHSessions():
  return [
      SSHSession(
          username=username,
          active_since=str(
              datetime.datetime.strptime(
                  '{date} {time}'.format(date=date_since, time=time_since),
                  '%Y-%m-%d %H:%M')),
          ip=ip.strip('()'),
      )._asdict() for (username, _, date_since, time_since, ip) in [
        l.split() for l in shared.GetSysOutput('who -s').split('\n')
      ]
  ]


def _GenerateSSHKeys():
  return [
      SSHKey(
          file=fn,
          type=type,
          size=int(shared.GetSysOutput(
              '/usr/bin/ssh-keygen -lf {file}  | cut -d" " -f1'.format(
                  file=fn))),
          fingerprint=shared.GetSysOutput(
              '/usr/bin/ssh-keygen -lf {file}  | cut -d" " -f2'.format(
                  file=fn)),
      )._asdict() for (fn, type) in set([
          ('/etc/ssh/ssh_host_key.pub', 'RSA1'),
          ('/etc/ssh/ssh_host_rsa_key.pub', 'RSA2'),
          ('/etc/ssh/ssh_host_dsa_key.pub', 'DSA'),
          ('/etc/ssh/ssh_host_ecdsa_key.pub', 'ECDSA'),
          ('/etc/ssh/ssh_host_ed25519_key.pub', 'ED25519'),
      ])
      if os.path.exists(fn)
  ]


def GetStatuses():
  return {
    shared.Component.REMOTE: {
        'keys': _GenerateSSHKeys(),
        'sessions': _GenerateSSHSessions(),
    },
  }
