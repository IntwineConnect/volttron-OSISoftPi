# OSISoftPI-VOLTTRON-Agent
Agent for the VOLTTRON framework to read data from the OSIsoft PI Server via the PI Web API.

This agent uses the OSIsoft PI Web API to communicate with a PI data server.  Basic Auth is used for authentication and is specified in the config file.

To use this agent first populate the config file with the URL of the PI server along with the Basic Auth username and password. Points to monitor can be added to the 'points' list in the config file. Each point has a name and webId.  The webId is a long string provided by the PI API to uniquely identify each point.

The agent currently uses a single data rate for polling, set by the HEARTBEAT_PERIOD within settings.py

Each poll will result in the publication of the data to the pubsub bus. Below is an example. The top-level topic is configurable within the config file.  The second level topic is based on the name provided in the config file.  The message will include units, value, and a timestamp formatted using the ISO8601 standard with time in UTC.

Topic: 'PIWebAPI\Power_Total'
Message: {'units': 'kW', 'timestamp': '2017-10-04Z14:49:27.455001', 'value': 33.0}

To package:
./scripts/core/pack_install.sh OSISoftPI-VOLTTRON-Agent/ OSISoftPI-VOLTTRON-Agent/config pie

To start:
volttron-ctl start --tag pie

To remove:
volttron-ctl remove --tag pie
