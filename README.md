# gsuite-utils

This repo is created for investigating 

1. how the Google Apps Admin SDK - Reports API
2. how the Google Calendar API

Please see [Quick Start: Google Apps Admin SDK - Reports API](https://developers.google.com/admin-sdk/reports/v1/quickstart/python) for the steps about 

1. enabling API access
2. create OAuth client ID and credential (client_secret.json)

## Locally Installing / Testing 

**Copy client_secret.json to gsuit_utils/**

**Linux**

    virtualenv env
    . env/bin/activate
    pip install -e .
    python gdrive_utils/gdrive.py
    python gdrive_utils/gcalendar.py
    # for running pytest
    pip install -r requirements-test.txt
    # for full testing with tox and building wheel
    ./test.sh

**Windows**

    virtualenv env
    env\Scripts\activate
    pip install -e .
    python gdrive_utils\gdrive.py
    python gdrive_utils\gcalendar.py
    # for running pytest
    pip install -r requirements-test.txt
    # for full testing with tox and building wheel
    test.bat
