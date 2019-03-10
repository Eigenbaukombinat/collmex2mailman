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
unmoderated = []
moderated = []
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
    except ConfigParser.Error as exc:
        log.warn(
           'Member <{} {}> has invalid data in Bemerkung field.'
           '\n{}'.format(
               mem.get('Vorname'),
               mem.get('Name'), str(exc)
           )
        )
        mconfig.readfp(io.StringIO(DEFAULT_INI))    
    unmod = False
    if mconfig.has_section('mailinglists'):
        unmod = mconfig.getboolean('mailinglists', 'can_post_to_mitglieder')
    if unmod:
        unmoderated.append(mail)
    else:
        moderated.append(mail)
    all_mems.append(mail)

with open('current_members', 'w') as cm:
    for m in all_mems:
        cm.write(m + '\n')

subprocess.call([
    '/var/lib/mailman/bin/sync_members',
    '-f',
    'current_members',
    'mitglieder'])

for m in moderated:
    subprocess.call([
        '/var/lib/mailman/bin/withlist',
        '-r',
        'set_mod',
        'mitglieder',
        '-s',         
        m])
        
for m in unmoderated:
    subprocess.call([
        '/var/lib/mailman/bin/withlist',
        '-r',
        'set_mod',
        'mitglieder',
        '-u',
        m])
        
if wo_mail > 0:
    log.warn('Found {} members without mail addresses:'.format(wo_mail))
    for mem in mems_wo_mail:
        log.warn(mem)
log.warn('List now has {} members, {} of them unmoderated.'.format(len(all_mems), len(unmoderated)))
