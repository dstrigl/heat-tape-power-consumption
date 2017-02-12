#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import rrdtool


# some internal time constants (in seconds)
minute = 1 * 60
hour   = 60 * minute
day    = 24 * hour
week   = 7 * day
month  = 30 * day
year   = 365 * day


times = { "6hours":  { "time":  6 * hour,
                       "step":  1 * minute,
                     },
          "12hours": { "time": 12 * hour,
                       "step":  1 * minute,
                     },
          "day":     { "time":  1 * day,
                       "step":  1 * minute,
                     },
          "2days":   { "time":  2 * day,
                       "step":  5 * minute,
                     },
          "3days":   { "time":  3 * day,
                       "step":  5 * minute,
                     },
          "week":    { "time":  7 * day,
                       "step":  5 * minute,
                     },
          "month":   { "time":  1 * month,
                       "step": 15 * minute,
                     },
          "year":    { "time":  1 * year,
                       "step":  1 * hour,
                     },
          #"3years":  { "time":  3 * year,
          #             "step":  3 * hour,
          #           },
          #
          # add more time definitions here!
          #
        }


graphs = [
    # ===================================================
    { "name": "htpc",
      "title": "Heizband Stromverbrauch",
      "vertical-label": "",
      "lower-limit" : -30,    # None = autoscaling
      "upper-limit" : 250,    # None = autoscaling
      "sources": [ # ------------------------------------
                   { "name": "Aussentemperatur",
                     "title": "Außentemperatur [°C]",
                     "color": "#025AFF",
                     "type": "area",
                   },
                   # ------------------------------------
                   { "name": "Spannung",
                     "title": "Spannung [V]",
                     "color": "#FFA902",
                     "type": "line",
                   },
                   # ------------------------------------
                   { "name": "Strom",
                     "title": "Strom [A]",
                     "color": "#A31E00",
                     "type": "line",
                   },
                   # ------------------------------------
                   { "name": "Leistung",
                     "title": "Leistung [W]",
                     "color": "#FF2802",
                     "type": "line",
                   },
                   # ------------------------------------
                   # add more sources here!
                 ]
    },
    # ===================================================
    { "name": "Heizband_Aussentemp",
      "title": "Heizband -- Aussentemperatur",
      "vertical-label": "",
      "lower-limit" : -30,    # None = autoscaling
      "upper-limit" :  40,    # None = autoscaling
      "sources": [ # ------------------------------------
                   { "name": "Aussentemperatur",
                     "title": "Außentemperatur [°C]",
                     "color": "#025AFF",
                     "type": "area",
                   },
                   # ------------------------------------
                   # add more sources here!
                 ]
    },
    # ===================================================
    { "name": "Heizband_Spannung",
      "title": "Heizband -- Spannung",
      "vertical-label": "",
      "lower-limit" :   0,    # None = autoscaling
      "upper-limit" : 250,    # None = autoscaling
      "sources": [ # ------------------------------------
                   { "name": "Spannung",
                     "title": "Spannung [V]",
                     "color": "#FFA902",
                     "type": "line",
                   },
                   # ------------------------------------
                   # add more sources here!
                 ]
    },
    # ===================================================
    { "name": "Heizband_Strom",
      "title": "Heizband -- Strom",
      "vertical-label": "",
      "lower-limit" : 0,    # None = autoscaling
      "upper-limit" : 5,    # None = autoscaling
      "sources": [ # ------------------------------------
                   { "name": "Strom",
                     "title": "Strom [A]",
                     "color": "#A31E00",
                     "type": "line",
                   },
                   # ------------------------------------
                   # add more sources here!
                 ]
    },
    # ===================================================
    { "name": "Heizband_Leistung",
      "title": "Heizband -- Leistung",
      "vertical-label": "",
      "lower-limit" :   0,    # None = autoscaling
      "upper-limit" : 500,    # None = autoscaling
      "sources": [ # ------------------------------------
                   { "name": "Leistung",
                     "title": "Leistung [W]",
                     "color": "#FF2802",
                     "type": "line",
                   },
                   # ------------------------------------
                   # add more sources here!
                 ]
    },
    # ===================================================
    #
    # add more graphs here!
    #
]


class RrdRender:

    # location of the RRD database file
    _filename = None

    def __init__(self, filename):
        """ ctr """
        if not os.path.isfile(filename):
            raise IOError("RRD file missing (%s)" % filename)
        self._filename = filename

    def render(self, path):
        """ paint the defined graphs under the given path """
        for timeName, timeData in times.items():
            for graph in graphs:

                tmp = []

                # add limits (upper and lower) if defined, otherwise the graphs are automatic scaled
                if graph.get("lower-limit") is not None:
                    tmp.extend(["--lower-limit", "%s" % str(graph["lower-limit"])])
                if graph.get("upper-limit") is not None:
                    tmp.extend(["--upper-limit", "%s" % str(graph["upper-limit"])])

                # add sources to paint (together with their style)
                for source in graph["sources"]:
                    tmp.append("DEF:%s=%s:%s:%s" % (source["name"], self._filename, source["name"], "AVERAGE"))
                for source in graph["sources"]:
                    if source["type"].lower() in ("outlining", "area"):
                        tmp.append("AREA:%s%s:%s" % (source["name"], source["color"], source["title"]))
                        if source["type"].lower() == "outlining":
                            #
                            # TODO
                            # tmp.append("LINE:%s%s" % (source["name"], ?))
                            #
                            pass
                    elif source["type"].lower() == "line":
                        tmp.append("LINE:%s%s:%s" % (source["name"], source["color"], source["title"]))
                    else: # invalid source type; only 'outlining', 'area' and 'line' are allowed!
                        raise ValueError("invalid source type (%s)" % source["type"])

                # TODO
                #tmp.append("VDEF:Aussentemp_min=Aussentemperatur,MINIMUM")
                #tmp.append("VDEF:Aussentemp_avg=Aussentemperatur,AVERAGE")
                #tmp.append("VDEF:Aussentemp_max=Aussentemperatur,MAXIMUM")
                #tmp.append("VDEF:Aussentemp_lst=Aussentemperatur,LAST")
                #tmp.append('COMMENT:Minimum ')
                #tmp.append('GPRINT:Aussentemp_min:%6.2lf °C')
                #tmp.append('COMMENT:Durchschnitt ')
                #tmp.append('GPRINT:Aussentemp_avg:%6.2lf °C')
                #tmp.append('COMMENT:Maximum ')
                #tmp.append('GPRINT:Aussentemp_max:%6.2lf °C')
                #tmp.append('COMMENT:Letzter Wert ')
                #tmp.append('GPRINT:Aussentemp_lst:%6.2lf °C')

                # create the graph
                rrdtool.graph(os.path.join(path, "%s_%s.png" % (graph["name"], timeName)),
                              "--imgformat", "PNG",
                              "--width", "800",
                              "--height", "400",
                              "--end", "now",
                              "--start", "end-%ds" % timeData["time"],
                              "--step", "%d" % timeData["step"],
                              "--vertical-label", graph["vertical-label"],
                              "--title", graph["title"],
                              "--color", "BACK#333333",
                              "--color", "CANVAS#333333",
                              "--color", "SHADEA#000000",
                              "--color", "SHADEB#111111",
                              "--color", "MGRID#CCCCCC",
                              "--color", "AXIS#FFFFFF",
                              "--color", "FRAME#AAAAAA",
                              "--color", "FONT#FFFFFF",
                              "--color", "ARROW#FFFFFF",
                              "--slope-mode",
                              *tmp)


__all__ = ["RrdRender"]
