#!/usr/bin/env python
# -*- coding: utf-8 -*-


from threading import Thread
from struct import unpack, calcsize


class Timeout(Exception):
    """
    This class rises timeout exceptions
    """
    pass


class Service(object):
    """
    This base class represents a service
    """

    @classmethod
    def from_bytes(cls, buffer):
        """
        Unpack Service data buffer
        """
        format_size = calcsize(cls.PACK_FORMAT)
        return cls(*unpack(cls.PACK_FORMAT, buffer[:format_size]), buffer[format_size:])

    def __repr__(self):
        return "{}{}".format(type(self).__name__, vars(self))

    def handle(self, source_address, destination_address, exeption=None):
        """
        Method intended to be overriden by childs
        """
        pass


class CanNode(Thread):
    """
    This base class let a can node run in a single thread

    Attributes
    ----------
    driver: PythonCanDriver
        access low-level CAN bus
    address: int
        CAN node address
    services: list
        a list of services
    isRunning: boolean
        state of the CAN node
    """

    def __init__(self, driver, address):
        """
        Initialize Thread

        Parameters
        ----------
        driver : PythonCanDriver
            Relying can interface

        address : int
            Node CAN address
        """
        Thread.__init__(self)
        self.driver = driver
        self.address = address
        self.services = []
        self.isRunning = True

    def stop(self):
        """
        Set CanNode.isRunning boolean class variable to False
        """
        self.isRunning = False

    def add_service(self, handler):
        """
        Add service handler to the CAN node
        """
        self.services.append(handler)

    def run(self):
        """
        Override method from Thread to permanently read data on the CAN bus if CanNode.isRunning is True
        """
        while self.isRunning:
            identifier, data, dlc, flag, time = self.driver.receive()
            if identifier is None:
                continue
            self.handle_rx_frame(identifier, data, dlc, flag, time)
