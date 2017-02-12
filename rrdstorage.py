#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rrdtool


step = 60       # data are expected each minute (60 sec)
heartbeat = 90  # heartbeat of the RRD database (in sec)

# rrdtool allows only up to 19 chars
dataSources = ( # 1234567890123456789
                 "Aussentemperatur",    # [°C]
                 "Spannung",            # [V]
                 "Strom",               # [A]
                 "Leistung",            # [W]
)


class RrdStorage:

    # location of the RRD database file
    _filename = None

    def __init__(self, filename):
        """ ctr """
        if not os.path.isfile(filename):
            self._createRRD(filename)
        self._filename = filename

    def _createRRD(self, filename):
        """ create an empty RRD database which fits our requirements """

        # setup the data sources for our RRD
        dss = []
        for source in sorted(dataSources):
            dss.append("DS:%s:GAUGE:%d:%s:%s" %
                       (source, heartbeat,
                       "U",  # min
                       "U",  # max
                       ))
        #print(dss)

        # setup how our RRD will archive the data
        rras = []
        '''
        # 1 days-worth of one-minute samples => 60 * 24 / 1 = 1440
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (1, 1440))
        # 7 days-worth of five-minute samples => 60 * 24 * 7 / 5 = 2016
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (5, 2016))
        # 30 days-worth of fifteen-minute samples => 60 * 24 * 30 / 15 = 2880
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (15, 2880))
        # 1 year-worth of one-hour samples => 60 * 24 * 365 / 60 = 8760
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (60, 8760))
        # 3 year-worth of three-hour samples => 60 * 24 * 365 * 3 / 180 = 8760
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (180, 8760))
        '''
        # 1 year-worth of one-minute samples => 60 * 24 * 365 = 525600
        rras.append("RRA:AVERAGE:0.5:%d:%d" % (1, 525600))
        #print(rras)

        # now create the RRD database
        rrdtool.create(filename, "--step", str(step), *(dss + rras))

    def add(self, values):
        """ adds the provided values to the RRD database """
        if not os.path.isfile(self._filename):
            raise IOError("RRD file missing (%s)" % self._filename)
        tmp = []
        for source in sorted(dataSources):
            if source not in values:
                tmp.append("U")
            else:
                tmp.append(str(values[source]))
        #print("N:%s" % ':'.join(tmp))
        # update the RRD database
        rrdtool.update(self._filename, "N:%s" % ':'.join(tmp))

    def info(self):
        """ returns the header information of the RRD database """
        return rrdtool.info(self._filename)


__all__ = ["RrdStorage"]
