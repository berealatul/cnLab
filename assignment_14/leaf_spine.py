#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import math


class LeafSpineTopology(Topo):
    def __init__(self, spine_count=2, leaf_count=4, hosts_per_leaf=2, switch_radix=16):
        Topo.__init__(self)
        self.spine_count = spine_count
        self.leaf_count = leaf_count
        self.hosts_per_leaf = hosts_per_leaf
        self.switch_radix = switch_radix
        self._validate_topology()
        self._build_topology()
    
    def _validate_topology(self):
        leaf_ports_needed = self.spine_count + self.hosts_per_leaf + 1
        spine_ports_needed = self.leaf_count + 1
        
        if leaf_ports_needed > self.switch_radix:
            raise ValueError(f"Leaf switches need {leaf_ports_needed} ports but radix is {self.switch_radix}")
        if spine_ports_needed > self.switch_radix:
            raise ValueError(f"Spine switches need {spine_ports_needed} ports but radix is {self.switch_radix}")
    
    def _build_topology(self):
        spine_switches = []
        for i in range(self.spine_count):
            spine = self.addSwitch(f"spine{i+1}", cls=OVSSwitch, protocols='OpenFlow13')
            spine_switches.append(spine)
        
        leaf_switches = []
        for i in range(self.leaf_count):
            leaf = self.addSwitch(f"leaf{i+1}", cls=OVSSwitch, protocols='OpenFlow13')
            leaf_switches.append(leaf)
        
        for spine in spine_switches:
            for leaf in leaf_switches:
                self.addLink(spine, leaf, cls=TCLink, bw=10, delay='1ms')
        
        host_id = 1
        for i, leaf in enumerate(leaf_switches):
            for j in range(self.hosts_per_leaf):
                host = self.addHost(
                    f"h{host_id}",
                    mac=f"00:00:00:00:{i+1:02d}:{j+1:02d}",
                    ip=f"10.0.{i+1}.{j+1}/24"
                )
                self.addLink(host, leaf, cls=TCLink, bw=1, delay='0.5ms')
                host_id += 1


def calculate_optimal_topology(total_hosts, switch_radix=16):
    usable_radix = switch_radix - 1
    best_config = None
    min_switches = float('inf')
    
    for hosts_per_leaf in range(1, usable_radix):
        max_spines_per_leaf = usable_radix - hosts_per_leaf
        leaf_count = math.ceil(total_hosts / hosts_per_leaf)
        
        if leaf_count <= usable_radix:
            spine_count = max(1, math.ceil(leaf_count / max_spines_per_leaf))
            
            if leaf_count <= spine_count * usable_radix:
                total_switches = spine_count + leaf_count
                
                if total_switches < min_switches:
                    min_switches = total_switches
                    best_config = {
                        'spine_count': spine_count,
                        'leaf_count': leaf_count,
                        'hosts_per_leaf': hosts_per_leaf,
                        'total_switches': total_switches,
                        'switch_radix': switch_radix
                    }
    
    return best_config


def main():
    parser = argparse.ArgumentParser(description='Leaf-Spine Topology for Mininet')
    parser.add_argument('--spines', '-s', type=int, default=2, help='Number of spine switches')
    parser.add_argument('--leaves', '-l', type=int, default=4, help='Number of leaf switches')
    parser.add_argument('--hosts', type=int, default=2, help='Hosts per leaf switch')
    parser.add_argument('--radix', '-r', type=int, default=16, help='Switch radix/port count')
    parser.add_argument('--auto', '-a', type=int, help='Auto-calculate topology for N total hosts')
    parser.add_argument('--controller', '-c', type=str, help='Remote controller IP')
    
    args = parser.parse_args()
    setLogLevel('info')
    
    if args.auto:
        config = calculate_optimal_topology(args.auto, args.radix)
        if config:
            args.spines = config['spine_count']
            args.leaves = config['leaf_count']
            args.hosts = config['hosts_per_leaf']
            info(f"Auto-calculated: {config['spine_count']} spines, {config['leaf_count']} leaves, {config['hosts_per_leaf']} hosts/leaf\n")
        else:
            info("ERROR: Cannot fit topology in given radix\n")
            return
    
    try:
        topo = LeafSpineTopology(
            spine_count=args.spines,
            leaf_count=args.leaves,
            hosts_per_leaf=args.hosts,
            switch_radix=args.radix
        )
        
        if args.controller:
            controller = RemoteController('c0', ip=args.controller, port=6633)
            net = Mininet(topo=topo, controller=controller, switch=OVSSwitch, link=TCLink)
        else:
            net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink)
        
        net.start()
        info(f"\nTopology: {args.spines} spines, {args.leaves} leaves, {args.leaves * args.hosts} hosts\n")
        CLI(net)
        net.stop()
        
    except Exception as e:
        info(f"ERROR: {e}\n")


if __name__ == '__main__':
    main()
