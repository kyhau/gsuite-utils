# gsuite-utils

[![Build Status](https://travis-ci.org/kyhau/gsuite-utils.svg?branch=master)](https://travis-ci.org/kyhau/gsuite-utils)

This repo contains simple scripts using 

1. Google Apps Admin SDK (Reports API) to retreive last N google drive activities
1. Google Calendar API to retrieve my next N calendar events (accepted invitations)
1. Google Groups and GroupsSettings

Please see [Google Apps Admin SDK - Reports API](https://developers.google.com/admin-sdk/reports/v1/quickstart/python) 
or [Google Calendar API](https://developers.google.com/google-apps/calendar/quickstart/python) for the steps about 

1. enabling API access
2. create OAuth client ID and credential (client_secret.json)

## Locally Installing / Testing 

**Copy client_secret.json to gsuite_utils/**

**Linux**

    virtualenv env
    . env/bin/activate
    pip install -e .
    
    python gsuite_utils/gdrive.py
    python gsuite_utils/gcalendar.py
    
    # for running pytest
    pip install -r requirements-build.txt
    
    # for full testing with tox and building wheel
    tox -r

**Windows**

    virtualenv env
    env\Scripts\activate
    pip install -e .
    
    python gsuite_utils\gdrive.py
    python gsuite_utils\gcalendar.py
    
    # for running pytest
    pip install -r requirements-build.txt
    
    # for full testing with tox and building wheel
    tox -r
