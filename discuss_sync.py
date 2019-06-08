#!/home/sync_ml/collmex2mailman/bin/python
from gocept.collmex.collmex import Collmex
from gocept.collmex.model import Member
import configparser
import io 
import logging
import subprocess
import traceback


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()

log.addHandler(ch)


api = Collmex()
members = api.get_members(include_inactive=False)

DEFAULT_INI = """[default]
foo = 1
"""


wo_mail = 0
all_mems = []
mems_wo_mail = []

for mem in members:
    mail = mem.get('E-Mail')
    if mail is None:
        wo_mail += 1
        log.warn('Member <{} {}> has no mail address.'.format(
            mem.get('Vorname'), mem.get('Name')))
        mems_wo_mail.append('{} {}'.format(mem.get('Vorname'), mem.get('Name')))
        continue
    mconfig = configparser.ConfigParser()
    try:
        mconfig.readfp(io.StringIO(mem.get('Bemerkung')))
    except configparser.Error as exc:
        log.warn(
           'Member <{} {}> has invalid data in Bemerkung field.'
           '\n{}'.format(
               mem.get('Vorname'),
               mem.get('Name'), str(exc)
           )
        )
        mconfig.readfp(io.StringIO(DEFAULT_INI))    
    diskussion_opt_out = False
    if mconfig.has_section('mailinglists') and 'diskussion_opt_out' in [k for k,v in  mconfig.items('mailinglists')]:
        diskussion_opt_out = mconfig.getboolean('mailinglists', 'diskussion_opt_out', default=False)
    if not diskussion_opt_out:
        all_mems.append(mail)


#bestandsmember in datei einlesen
subprocess.call([
    '/var/lib/mailman/bin/list_members',
    '-o',
    'diskussion_current',
    'diskussion'])

with open('diskussion_current', 'r') as disk_cur_file:
    diskussion_current_members = [s.strip() for s in disk_cur_file.readlines()]


with open('diskussion_already_sub', 'r') as disk_alr_sub_file:
    diskussion_already_subscribed = [s.strip() for s in disk_alr_sub_file.readlines()]


#neue mitgliederliste aufbauen, jenige die schonmal hinzugefuegt wurden weglassen,
#denn diese haben wahrscheinlich unsubscribed
for m in all_mems:
    if m not in diskussion_current_members and m not in diskussion_already_subscribed:
        diskussion_current_members.append(m)
        diskussion_already_subscribed.append(m)

with open('diskussion_new_members', 'w') as disk_new_file:
    for m in diskussion_current_members:
       disk_new_file.write(m + '\n')


with open('diskussion_already_sub', 'w') as disk_alr_sub_file:
    for m in diskussion_already_subscribed:
       disk_alr_sub_file.write(m + '\n')


subprocess.call([
    '/var/lib/mailman/bin/sync_members',
    '-f',
    'diskussion_new_members',
    'diskussion'])

