#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import rrdstorage
import rrdrender
from datetime import datetime
from timeit import default_timer as timer
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
#from pymodbus.client.sync import ModbusUdpClient as ModbusClient
#import pprint


rrd_file    = "/media/QNAP/raspberrypi/htpc_data.rrd"
log_file    = "/media/QNAP/raspberrypi/htpc_log.txt"
render_path = "/media/QNAP/raspberrypi"

wago_ip     = "192.168.11.30"

# --------------------------------------------------
#                Name                Modbus address
MODBUS_ADDR = { "Spannung"         : 12288,
                "Strom"            : 12290,
                "Leistung"         : 12292,
                "Aussentemperatur" : 12294,
}


def read_modbus_float(client, addr):
    rr = client.read_holding_registers(addr, 2)
    #print(rr.registers)
    w0 = rr.registers[0]
    w1 = rr.registers[1]
    return struct.unpack('>f', struct.pack('>HH', w1, w0))[0]


def main():
    try:
        # read values from WAGO PLC
        start = timer()
        client = ModbusClient(wago_ip, port=502)
        try:
            client.connect()
            values = {}
            for name, addr in MODBUS_ADDR.items():
                v = read_modbus_float(client, addr)
                #print("%s: %.2f" % (name, v))
                values.update({name: v})
        finally:
            client.close()
        end = timer()
        #pprint.pprint(values)

        # add values to the RRD
        st = rrdstorage.RrdStorage(rrd_file)
        st.add(values)

        # create log entry
        with open(log_file, 'a') as file:
            s = ["%s: %.3f" % (key, values[key]) for key in sorted(values)]
            file.write("[%s] OK : query took %.3f sec [ %s ]\n" %
                       (datetime.now().isoformat(), (end - start), ", ".join(s)))
        print("query took %.3f sec [ %s ]" % ((end - start), ", ".join(s)))

        # create the graphs
        rd = rrdrender.RrdRender(rrd_file)
        rd.render(render_path)

    except Exception as e:
        with open(log_file, 'a') as file:
            file.write("[%s] ERR: %s\n" % (datetime.now().isoformat(), str(e)))
        print("error: %s\n" % str(e))


if __name__ == "__main__":
    main()
