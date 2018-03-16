mitgliedersync
==============

Scripts to sync members of "collmex verein" to mailman mailinglists.


Installation
------------

virtualenv --python=python2 .
bin/pip install -r requirements.txt


Setup
-----

You will need to edit the scripts for now to adapt them to your lists.
There are two scripts which do different things:

* membersync.py

Does forcefully subscribe all members to a list. This is for moderated 
lists which cannot be unsubscribed. You can unmoderate members in collmex
"Bemerkungen" field with a configuration (ini-style):

```ini
[mailinglists]
can_post_to_mitglieder = True
```

* discuss_sync.py

For subscribing new members to a mailinglist. The subscribed members are
remembered and not subscribed again if they unsubscibe. The "Bemerkungen"
field can be used for opting out of this list:

```ini
[mailinglists]
diskussion_opt_out = True
```
