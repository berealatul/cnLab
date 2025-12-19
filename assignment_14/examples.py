#!/usr/bin/env python3
"""
Leaf-Spine Topology Examples
============================

This script demonstrates different configurations of the leaf-spine topology
with various scaling scenarios based on switch radix.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from leaf_spine_topology import LeafSpineTopology, calculate_optimal_topology
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.node import OVSSwitch


def run_small_topology():
    """Run a small leaf-spine topology (2 spines, 4 leaves, 2 hosts/leaf)"""
    info("\n" + "="*60 + "\n")
    info("EXAMPLE 1: SMALL LEAF-SPINE TOPOLOGY\n") 
    info("="*60 + "\n")
    info("Configuration: 2 spines, 4 leaves, 2 hosts per leaf\n")
    info("Total hosts: 8, Switch radix: 16\n")
    
    topo = LeafSpineTopology(spine_count=2, leaf_count=4, hosts_per_leaf=2, switch_radix=16)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    
    info("Starting network...\n")
    net.start()
    
    info("Testing connectivity...\n")
    result = net.pingAll()
    info(f"Ping test result: {result}% packet loss\n")
    
    CLI(net)
    net.stop()


def run_medium_topology():
    """Run a medium leaf-spine topology (4 spines, 8 leaves, 3 hosts/leaf)"""
    info("\n" + "="*60 + "\n") 
    info("EXAMPLE 2: MEDIUM LEAF-SPINE TOPOLOGY\n")
    info("="*60 + "\n")
    info("Configuration: 4 spines, 8 leaves, 3 hosts per leaf\n")
    info("Total hosts: 24, Switch radix: 16\n")
    
    topo = LeafSpineTopology(spine_count=4, leaf_count=8, hosts_per_leaf=3, switch_radix=16)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    
    info("Starting network...\n")
    net.start()
    
    info("Testing connectivity...\n")
    result = net.pingAll()
    info(f"Ping test result: {result}% packet loss\n")
    
    CLI(net)
    net.stop()


def run_large_topology():
    """Run a large leaf-spine topology with higher radix switches"""
    info("\n" + "="*60 + "\n")
    info("EXAMPLE 3: LARGE LEAF-SPINE TOPOLOGY\n")
    info("="*60 + "\n") 
    info("Configuration: 8 spines, 16 leaves, 4 hosts per leaf\n")
    info("Total hosts: 64, Switch radix: 32\n")
    
    topo = LeafSpineTopology(spine_count=8, leaf_count=16, hosts_per_leaf=4, switch_radix=32)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
    
    info("Starting network...\n") 
    net.start()
    
    info("Testing connectivity between random hosts...\n")
    h1 = net.get('h1')
    h32 = net.get('h32') 
    h64 = net.get('h64')
    
    info("Ping h1 -> h32: ")
    result1 = net.ping([h1, h32], timeout=1)
    info(f"{result1}\n")
    
    info("Ping h1 -> h64: ")
    result2 = net.ping([h1, h64], timeout=1)
    info(f"{result2}\n")
    
    CLI(net)
    net.stop()


def run_auto_calculated_topology():
    """Demonstrate auto-calculation of topology for a given number of hosts"""
    info("\n" + "="*60 + "\n")
    info("EXAMPLE 4: AUTO-CALCULATED TOPOLOGY\n")
    info("="*60 + "\n")
    
    # Calculate optimal topology for 50 hosts with radix-24 switches
    total_hosts = 50
    radix = 24
    
    info(f"Auto-calculating topology for {total_hosts} hosts with radix-{radix} switches...\n")
    config = calculate_optimal_topology(total_hosts, radix)
    
    if config:
        info(f"Optimal configuration found:\n")
        info(f"  - Spine switches: {config['spine_count']}\n")
        info(f"  - Leaf switches: {config['leaf_count']}\n") 
        info(f"  - Hosts per leaf: {config['hosts_per_leaf']}\n")
        info(f"  - Total switches: {config['total_switches']}\n")
        info(f"  - Actual hosts: {config['leaf_count'] * config['hosts_per_leaf']}\n")
        
        # Create and run the topology
        topo = LeafSpineTopology(
            spine_count=config['spine_count'],
            leaf_count=config['leaf_count'], 
            hosts_per_leaf=config['hosts_per_leaf'],
            switch_radix=radix
        )
        
        net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, autoSetMacs=True)
        
        info("Starting auto-calculated network...\n")
        net.start()
        
        # Test a few random connections
        info("Testing random connectivity...\n")
        h1 = net.get('h1')
        h25 = net.get('h25')  
        h50 = net.get('h50')
        
        if h25 and h50:
            result1 = net.ping([h1, h25], timeout=1)
            result2 = net.ping([h1, h50], timeout=1)
            info(f"h1 <-> h25: {result1}\n")
            info(f"h1 <-> h50: {result2}\n")
        
        CLI(net)
        net.stop()
    else:
        info("ERROR: Could not calculate valid topology for given constraints\n")


def show_scaling_analysis():
    """Show scaling analysis for different radix values"""
    info("\n" + "="*60 + "\n")
    info("SCALING ANALYSIS\n") 
    info("="*60 + "\n")
    
    host_targets = [20, 50, 100, 200, 500]
    radix_values = [16, 24, 32, 48, 64]
    
    info("Optimal configurations for different host counts and radix values:\n")
    info("-" * 80 + "\n")
    info(f"{'Hosts':<8} {'Radix':<8} {'Spines':<8} {'Leaves':<8} {'H/L':<6} {'Switches':<10}\n")
    info("-" * 80 + "\n")
    
    for hosts in host_targets:
        for radix in radix_values:
            config = calculate_optimal_topology(hosts, radix)
            if config:
                info(f"{hosts:<8} {radix:<8} {config['spine_count']:<8} "
                     f"{config['leaf_count']:<8} {config['hosts_per_leaf']:<6} "
                     f"{config['total_switches']:<10}\n")
            else:
                info(f"{hosts:<8} {radix:<8} {'N/A':<8} {'N/A':<8} {'N/A':<6} {'N/A':<10}\n")
        info("-" * 80 + "\n")


def main():
    """Main function to run examples"""
    setLogLevel('info')
    
    info("Leaf-Spine Topology Examples\n")
    info("Choose an example to run:\n")
    info("1. Small topology (8 hosts, radix-16)\n")  
    info("2. Medium topology (24 hosts, radix-16)\n")
    info("3. Large topology (64 hosts, radix-32)\n")
    info("4. Auto-calculated topology (50 hosts, radix-24)\n")
    info("5. Show scaling analysis\n")
    info("6. Run all examples\n")
    
    try:
        choice = input("Enter your choice (1-6): ").strip()
        
        if choice == '1':
            run_small_topology()
        elif choice == '2':
            run_medium_topology() 
        elif choice == '3':
            run_large_topology()
        elif choice == '4':
            run_auto_calculated_topology()
        elif choice == '5':
            show_scaling_analysis()
        elif choice == '6':
            show_scaling_analysis()
            run_small_topology()
            run_medium_topology()
            run_auto_calculated_topology()
        else:
            info("Invalid choice. Please run again.\n")
            
    except KeyboardInterrupt:
        info("\nExiting...\n")
    except Exception as e:
        info(f"Error: {e}\n")


if __name__ == '__main__':
    main()
