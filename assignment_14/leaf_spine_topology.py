#!/usr/bin/env python3
"""
Custom Leaf-Spine Topology for Mininet
========================================

This module implements a scalable leaf-spine topology that can be configured
with different switch radix values. The topology follows the standard leaf-spine
architecture commonly used in data centers.

Author: Network Lab Assignment
Date: December 2025
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import math


class LeafSpineTopology(Topo):
    """
    Custom Leaf-Spine Topology Class
    
    This topology creates a leaf-spine architecture where:
    - Spine switches are at the top tier (core)
    - Leaf switches are at the bottom tier (access)
    - Each leaf switch connects to ALL spine switches
    - Hosts connect only to leaf switches
    
    Parameters:
    -----------
    spine_count : int
        Number of spine switches
    leaf_count : int  
        Number of leaf switches
    hosts_per_leaf : int
        Number of hosts connected to each leaf switch
    switch_radix : int
        Port capacity of switches (affects scaling)
    """
    
    def __init__(self, spine_count=2, leaf_count=4, hosts_per_leaf=2, switch_radix=16):
        """
        Initialize the leaf-spine topology
        
        Args:
            spine_count: Number of spine switches
            leaf_count: Number of leaf switches  
            hosts_per_leaf: Hosts per leaf switch
            switch_radix: Maximum ports per switch
        """
        Topo.__init__(self)
        
        self.spine_count = spine_count
        self.leaf_count = leaf_count
        self.hosts_per_leaf = hosts_per_leaf
        self.switch_radix = switch_radix
        
        # Validate topology constraints
        self._validate_topology()
        
        # Build the topology
        self._build_topology()
    
    def _validate_topology(self):
        """Validate that the topology can be built with given radix"""
        # Each leaf needs ports for: spine connections + hosts + management
        leaf_ports_needed = self.spine_count + self.hosts_per_leaf + 1
        
        # Each spine needs ports for: leaf connections + management  
        spine_ports_needed = self.leaf_count + 1
        
        if leaf_ports_needed > self.switch_radix:
            raise ValueError(f"Leaf switches need {leaf_ports_needed} ports but radix is {self.switch_radix}")
            
        if spine_ports_needed > self.switch_radix:
            raise ValueError(f"Spine switches need {spine_ports_needed} ports but radix is {self.switch_radix}")
            
        info(f"✓ Topology validation passed for radix-{self.switch_radix}\n")
    
    def _build_topology(self):
        """Build the complete leaf-spine topology"""
        info("Building Leaf-Spine Topology...\n")
        
        # Create spine switches
        spine_switches = self._create_spine_switches()
        
        # Create leaf switches  
        leaf_switches = self._create_leaf_switches()
        
        # Connect spines to leaves (full mesh)
        self._connect_spine_to_leaf(spine_switches, leaf_switches)
        
        # Create and connect hosts to leaves
        self._create_and_connect_hosts(leaf_switches)
        
        info(f"✓ Topology built successfully!\n")
        info(f"  - {self.spine_count} spine switches\n")
        info(f"  - {self.leaf_count} leaf switches\n") 
        info(f"  - {self.leaf_count * self.hosts_per_leaf} hosts\n")
        info(f"  - {self.spine_count * self.leaf_count} spine-leaf links\n")
    
    def _create_spine_switches(self):
        """Create spine tier switches"""
        spine_switches = []
        
        for i in range(self.spine_count):
            spine_name = f"spine{i+1}"
            spine_switch = self.addSwitch(
                spine_name,
                cls=OVSSwitch,
                protocols='OpenFlow13'
            )
            spine_switches.append(spine_switch)
            info(f"  + Created spine switch: {spine_name}\n")
            
        return spine_switches
    
    def _create_leaf_switches(self):
        """Create leaf tier switches"""
        leaf_switches = []
        
        for i in range(self.leaf_count):
            leaf_name = f"leaf{i+1}"
            leaf_switch = self.addSwitch(
                leaf_name, 
                cls=OVSSwitch,
                protocols='OpenFlow13'
            )
            leaf_switches.append(leaf_switch)
            info(f"  + Created leaf switch: {leaf_name}\n")
            
        return leaf_switches
    
    def _connect_spine_to_leaf(self, spine_switches, leaf_switches):
        """Create full mesh connectivity between spine and leaf tiers"""
        info("Connecting spine-leaf full mesh...\n")
        
        link_count = 0
        for spine in spine_switches:
            for leaf in leaf_switches:
                # Add high-bandwidth link with low latency
                self.addLink(
                    spine, leaf,
                    cls=TCLink,
                    bw=10,  # 10 Gbps
                    delay='1ms',
                    loss=0
                )
                link_count += 1
                
        info(f"  + Created {link_count} spine-leaf links\n")
    
    def _create_and_connect_hosts(self, leaf_switches):
        """Create hosts and connect them to leaf switches"""
        info("Creating and connecting hosts...\n")
        
        host_id = 1
        for i, leaf in enumerate(leaf_switches):
            for j in range(self.hosts_per_leaf):
                # Create host with meaningful name
                host_name = f"h{host_id}"
                host = self.addHost(
                    host_name,
                    cpu=0.1,  # 10% CPU allocation
                    mac=f"00:00:00:00:{i+1:02d}:{j+1:02d}",  # Structured MAC
                    ip=f"10.0.{i+1}.{j+1}/24"  # Structured IP addressing
                )
                
                # Connect host to leaf with 1Gbps link
                self.addLink(
                    host, leaf,
                    cls=TCLink, 
                    bw=1,  # 1 Gbps
                    delay='0.5ms',
                    loss=0
                )
                
                info(f"  + Created host {host_name} -> leaf{i+1}\n")
                host_id += 1


def calculate_optimal_topology(total_hosts, switch_radix=16):
    """
    Calculate optimal topology parameters for given constraints
    
    Args:
        total_hosts: Total number of hosts needed
        switch_radix: Switch port capacity
        
    Returns:
        dict: Optimal topology configuration
    """
    # Reserve 1 port per switch for management
    usable_radix = switch_radix - 1
    
    # For leaf switches: ports needed for spines + hosts
    # For spine switches: ports needed for leaves
    
    # Try different configurations
    best_config = None
    min_switches = float('inf')
    
    for hosts_per_leaf in range(1, usable_radix):
        max_spines_per_leaf = usable_radix - hosts_per_leaf
        
        # Calculate required leaves
        leaf_count = math.ceil(total_hosts / hosts_per_leaf)
        
        # Calculate required spines (each spine can handle leaf_count leaves)
        if leaf_count <= usable_radix:
            spine_count = max(1, math.ceil(leaf_count / max_spines_per_leaf))
            
            # Verify spine capacity
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
    """Main function to create and run the topology"""
    parser = argparse.ArgumentParser(description='Leaf-Spine Topology for Mininet')
    parser.add_argument('--spines', '-s', type=int, default=2,
                       help='Number of spine switches (default: 2)')
    parser.add_argument('--leaves', '-l', type=int, default=4, 
                       help='Number of leaf switches (default: 4)')
    parser.add_argument('--hosts', type=int, default=2,
                       help='Hosts per leaf switch (default: 2)')
    parser.add_argument('--radix', '-r', type=int, default=16,
                       help='Switch radix/port count (default: 16)')
    parser.add_argument('--auto', '-a', type=int,
                       help='Auto-calculate topology for N total hosts')
    parser.add_argument('--controller', '-c', type=str, default=None,
                       help='Remote controller IP (default: None)')
    
    args = parser.parse_args()
    
    # Auto-calculate topology if requested
    if args.auto:
        info(f"Auto-calculating topology for {args.auto} hosts...\n")
        config = calculate_optimal_topology(args.auto, args.radix)
        if config:
            args.spines = config['spine_count']
            args.leaves = config['leaf_count'] 
            args.hosts = config['hosts_per_leaf']
            info(f"Optimal configuration: {config}\n")
        else:
            info("ERROR: Cannot fit topology in given radix\n")
            return
    
    # Set log level
    setLogLevel('info')
    
    try:
        # Create topology
        topo = LeafSpineTopology(
            spine_count=args.spines,
            leaf_count=args.leaves,
            hosts_per_leaf=args.hosts,
            switch_radix=args.radix
        )
        
        # Create network
        if args.controller:
            controller = RemoteController('c0', ip=args.controller, port=6633)
            net = Mininet(topo=topo, controller=controller, switch=OVSSwitch,
                         link=TCLink, autoSetMacs=True)
        else:
            net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, 
                         autoSetMacs=True)
        
        # Start network
        info("Starting network...\n")
        net.start()
        
        # Print topology info
        info("\n" + "="*50 + "\n")
        info("LEAF-SPINE TOPOLOGY READY\n")
        info("="*50 + "\n")
        info(f"Spine switches: {args.spines}\n")
        info(f"Leaf switches: {args.leaves}\n") 
        info(f"Total hosts: {args.leaves * args.hosts}\n")
        info(f"Switch radix: {args.radix}\n")
        info("\nUse 'pingall' to test connectivity\n")
        info("Use 'iperf h1 h2' to test bandwidth\n")
        info("="*50 + "\n")
        
        # Start CLI
        CLI(net)
        
    except Exception as e:
        info(f"ERROR: {e}\n")
    finally:
        if 'net' in locals():
            net.stop()


if __name__ == '__main__':
    main()
