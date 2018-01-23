########################################################################
# Copyright (c) 2017-2018, Intwine Connect, LLC.                       #
# This file is licensed under the BSD-3-Clause                         #
# See LICENSE for complete text                                        #
########################################################################
from __future__ import absolute_import

from .piwebapi import PIWebAPI

import logging
import sys

from volttron.platform.vip.agent import Agent, Core, PubSub, compat, RPC
from volttron.platform.agent import utils

from . import settings

utils.setup_logging()
_log = logging.getLogger(__name__)


class piWebAPIAgent(Agent):
    def __init__(self, config_path, **kwargs):
        super(piWebAPIAgent, self).__init__(**kwargs)
        self._agent_id = 'piWebAPIAgent'
        self.pi = None
        self.to_monitor = []
        self.publish_topic = ""

        # Load default configuration from the config file
        self.default_config = utils.load_config(config_path)

        self.vip.config.set_default("config", self.default_config)
        self.vip.config.subscribe(self.configure, actions=["NEW", "UPDATE"], pattern="config")

    def configure(self, config_name, action, contents):
        config = self.default_config.copy()
        config.update(contents)
        try:
            self.publish_topic = str(config["publish_topic"])
        except ValueError as e:
            _log.error("ERROR PROCESSING CONFIGURATION: {}".format(e))

    @Core.receiver("onstart")
    def starting(self, sender, **kwargs):
        self.publish_topic = self.default_config['publish_topic']
        server = self.default_config['server']
        self.pi = PIWebAPI(server['url'], (server['un'], server['pw']))
        if self.pi:
            _log.info("Connected to OSIsoft PI Server: " + server['url'])
        points = self.default_config['points']
        for point in points:
            self.to_monitor.append(self.pi.monitor_point(point['name'], point['webId']))

    @Core.periodic(settings.HEARTBEAT_PERIOD)
    def publish_heartbeat(self):
        if self.pi:
            headers = {
                'AgentID': self._agent_id,
            }
            for point in self.to_monitor:
                point.read_latest_value()
                self.vip.pubsub.publish(peer='pubsub',
                                        topic=self.publish_topic + "/" + point.readable_name,
                                        message=point.get_serializable(),
                                        headers=headers)
        else:
            print "No Connection to a PI server..."


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(piWebAPIAgent)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
