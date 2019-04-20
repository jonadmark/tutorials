#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper


def installIPv4Rules(p4info_helper, switches):
    # IPv4 Rules for Switch S1
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.1.1', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:00:01:01', 'port': 1}
    )
    switches[0].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.2.2', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:02:02:00', 'port': 2}
    )
    switches[0].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.3.3', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:03:03:00', 'port': 3}
    )
    switches[0].WriteTableEntry(table_entry)

    # IPv4 Rules for Switch S2
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.1.1', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:01:01:00', 'port': 2}
    )
    switches[1].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.2.2', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:00:02:02', 'port': 1}
    )
    switches[1].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.3.3', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:03:03:00', 'port': 3}
    )
    switches[1].WriteTableEntry(table_entry)

    # IPv4 Rules for Switch S3
    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.1.1', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:01:01:00', 'port': 2}
    )
    switches[2].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.2.2', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:02:02:00', 'port': 3}
    )
    switches[2].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name='MyIngress.ipv4_lpm',
        match_fields={'hdr.ipv4.dstAddr': ('10.0.3.3', 32)},
        action_name='MyIngress.ipv4_forward',
        action_params={'dstAddr': '00:00:00:00:03:03', 'port': 1}
    )
    switches[2].WriteTableEntry(table_entry)


def createTunnel(p4info_helper, switches):
    # Tunnel Rules for Switch S1
    ## Update IPv4_lpm rule to create a tunnel ingress rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={"hdr.ipv4.dstAddr": ('10.0.2.2', 32)},
        action_name="MyIngress.myTunnel_ingress",
        action_params={"dst_id": 200}
    )
    switches[0].ModifyTableEntry(table_entry)

    ## Tunnel rule for forwarding traffic to host H2
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 200},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 2}
    )
    switches[0].WriteTableEntry(table_entry)

    ## Tunnel rule for forwarding traffic to host H1
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 100},
        action_name="MyIngress.myTunnel_egress",
        action_params={'dstAddr': '00:00:00:00:01:01', "port": 1}
    )
    switches[0].WriteTableEntry(table_entry)

    # Tunnel Rules for Switch S2
    ## Update IPv4_lpm rule to create a tunnel ingress rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={"hdr.ipv4.dstAddr": ('10.0.1.1', 32)},
        action_name="MyIngress.myTunnel_ingress",
        action_params={"dst_id": 100}
    )
    switches[1].ModifyTableEntry(table_entry)

    ## Tunnel rule for forwarding traffic to host H2
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 100},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 2}
    )
    switches[1].WriteTableEntry(table_entry)

    ## Tunnel rule for forwarding traffic to host H1
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 200},
        action_name="MyIngress.myTunnel_egress",
        action_params={'dstAddr': '00:00:00:00:02:02', "port": 1}
    )
    switches[1].WriteTableEntry(table_entry)

    # Tunnel Rules for Switch S3
    ## NOTHING TO DO


def updateTunnel(p4info_helper, switches):
    # Updated Tunnel Rules for Switch S1
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 200},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 3}  # THIS IS NEW
    )
    switches[0].ModifyTableEntry(table_entry)

    # Updated Tunnel Rules for Switch S2
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 100},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 3}
    )
    switches[1].ModifyTableEntry(table_entry)

    # Tunnel Rules for Switch S3
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 100},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 2}
    )
    switches[2].WriteTableEntry(table_entry)

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.myTunnel_exact",
        match_fields={"hdr.myTunnel.dst_id": 200},
        action_name="MyIngress.myTunnel_forward",
        action_params={"port": 3}
    )
    switches[2].WriteTableEntry(table_entry)


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print


def readTableRulesFromSwitches(p4info_helper, switches):
    for sw in switches:
        readTableRules(p4info_helper, sw)
        print "-----"


def printGrpcError(e):
    print "gRPC Error:", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    traceback = sys.exc_info()[2]
    print "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()

        switches = [s1, s2, s3]

        # PHASE 1: INSTALL THE P4 PROGRAM ON THE SWITCHES
        print '####################'
        print '# Starting Phase 1 #'
        print '####################'
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s1"
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s2"
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s3"

        readTableRulesFromSwitches(p4info_helper, switches)

        print 'Phase 1 finished, press [ENTER] to continue.'
        raw_input()

        # PHASE 2: INSTALL IPv4 FORWARDING RULES ON THE SWITCHES
        print '####################'
        print '# Starting Phase 2 #'
        print '####################'
        installIPv4Rules(p4info_helper, switches)

        readTableRulesFromSwitches(p4info_helper, switches)

        print 'Phase 2 finished, press [ENTER] to continue.'
        raw_input()

        # PHASE 3: CREATE A TUNNEL FOR TRAFFIC BETWEEN H1 AND H2 USING THE DEFAULT SHORTEST ROUTE
        print '####################'
        print '# Starting Phase 3 #'
        print '####################'
        createTunnel(p4info_helper, switches)

        readTableRulesFromSwitches(p4info_helper, switches)

        print 'Phase 3 finished, press [ENTER] to continue.'
        raw_input()

        # PHASE 4: UPDATE THE TUNNEL FOR H1-H2 TRAFFIC TO USE THE ALTERNATE S1-S3-S2 ROUTE
        print '####################'
        print '# Starting Phase 4 #'
        print '####################'
        updateTunnel(p4info_helper, switches)

        readTableRulesFromSwitches(p4info_helper, switches)

        print 'All steps have been finished, press [ENTER] to exit.'
        raw_input()

        ## THE END
        print 'THE END.'
    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/myprogram.p4info')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/myprogram.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
