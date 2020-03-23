#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import can
import logging

logger = logging.getLogger(__name__)


class PythonCanDriver:
    """
    This class act as a *CAN* bus interface in order to communicate with the *Xcom-CAN*, it is **NOT**
    intended to access it directly.

    Attributes
    ----------
    can_bus : can.interface.Bus
        low-level device specific CAN interface
    """

    def __init__(self, bitrate, bustype='kvaser'):
        """
        Initialize PythonCanDriver.can_bus with the specified bitrate for a *Kvaser* interface if running on Windows,
        otherwise you must specify your bustype interface such as *SocketCAN* (not tested yet)

        Parameters
        ----------
        bitrate
            CAN bus speed
        """
        if os.name == 'nt':
            self.can_bus = can.interface.Bus(bustype=bustype, channel=0, bitrate=bitrate)
        else:
            self.can_bus = can.interface.Bus(bitrate=bitrate)

    def receive(self, timeout=100):
        """
        Read a message on the CAN bus, waiting block

        Parameters
        ----------
        timeout : float
            milli seconds to wait for a message (default 100ms)

        Returns
        -------
        tuple
            identifier, data, dlc, flag, timestamp
        """
        message = self.can_bus.recv(timeout=timeout / 1000)
        if message is None:
            return None, None, None, None, None
        else:
            logger.debug("<- rx : id 0x" + str(format(message.arbitration_id, '08x')) + " | data 0x" + str(
                bytes(message.data).hex()) + " | DLC " + str(message.dlc))
            return message.arbitration_id, message.data, message.dlc, None, message.timestamp

    def send(self, identifier, data, is_extended_id=False):
        """
        Send a message on the CAN bus

        Parameters
        ----------
        identifier : int
            The frame identifier used for arbritration on the bus

        data : bytearray
            The data parameter of a CAN message, length from 0 to 8 bytes

        is_extended_id : bool
            Set usage of CAN2.0A (Standard, 11 bits identifier) of CAN2.0B (extended, 29 bits identifier)
        """
        message = can.Message(arbitration_id=identifier, data=data, is_extended_id=is_extended_id)
        logger.debug("-> tx : id 0x" + str(format(message.arbitration_id, '08x')) + " | data 0x" + str(
            bytes(message.data).hex()) + " | DLC " + str(message.dlc))
        self.can_bus.send(message)
