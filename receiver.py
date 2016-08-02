#!/usr/bin/env python3

from housepy import config, osc

def message_handler(location, address, data):
    pass
receiver = osc.Receiver(config['port'], message_handler, blocking=True)

