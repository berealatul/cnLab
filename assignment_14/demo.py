#!/usr/bin/env python3
"""
Leaf-Spine Topology Demo
========================

This script demonstrates the leaf-spine topology without requiring Mininet
to be run as root. It shows the topology construction and analysis.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from leaf_spine_topology import LeafSpineTopology, calculate_optimal_topology


def demo_topology_creation():
    """Demonstrate topology creation and analysis"""
    print("🏗️  Leaf-Spine Topology Creation Demo")
    print("=" * 50)
    
    # Create different topologies
    configs = [
        {'spines': 2, 'leaves': 4, 'hosts': 2, 'radix': 16, 'name': 'Small'},
        {'spines': 4, 'leaves': 6, 'hosts': 3, 'radix': 24, 'name': 'Medium'},
        {'spines': 6, 'leaves': 8, 'hosts': 4, 'radix': 32, 'name': 'Large'}
    ]
    
    for config in configs:
        print(f"\n📊 {config['name']} Topology Configuration:")
        print(f"   Spines: {config['spines']}, Leaves: {config['leaves']}")
        print(f"   Hosts per leaf: {config['hosts']}, Switch radix: {config['radix']}")
        
        try:
            topo = LeafSpineTopology(
                spine_count=config['spines'],
                leaf_count=config['leaves'],
                hosts_per_leaf=config['hosts'],
                switch_radix=config['radix']
            )
            
            # Analyze topology
            switches = topo.switches()
            hosts = topo.hosts()
            links = topo.links()
            
            total_hosts = config['leaves'] * config['hosts']
            spine_leaf_links = config['spines'] * config['leaves']
            host_leaf_links = total_hosts
            total_links = spine_leaf_links + host_leaf_links
            
            print(f"   ✅ Created successfully!")
            print(f"   📈 Stats: {len(switches)} switches, {len(hosts)} hosts, {len(links)} links")
            print(f"   🔗 Expected links: {spine_leaf_links} spine-leaf + {host_leaf_links} host-leaf = {total_links}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")


def demo_auto_calculation():
    """Demonstrate automatic topology calculation"""
    print("\n🧮 Auto-Calculation Demo") 
    print("=" * 50)
    
    test_cases = [
        {'hosts': 20, 'radix': 16},
        {'hosts': 50, 'radix': 24},
        {'hosts': 100, 'radix': 32},
        {'hosts': 200, 'radix': 48}
    ]
    
    for case in test_cases:
        print(f"\n🎯 Target: {case['hosts']} hosts with {case['radix']}-port switches")
        
        config = calculate_optimal_topology(case['hosts'], case['radix'])
        
        if config:
            print(f"   ✅ Solution found:")
            print(f"   📊 Spines: {config['spine_count']}, Leaves: {config['leaf_count']}")
            print(f"   🏠 Hosts per leaf: {config['hosts_per_leaf']}")
            print(f"   🔢 Total switches: {config['total_switches']}")
            print(f"   📈 Actual hosts: {config['leaf_count'] * config['hosts_per_leaf']}")
            
            # Calculate efficiency
            efficiency = case['hosts'] / (config['leaf_count'] * config['hosts_per_leaf']) * 100
            print(f"   ⚡ Efficiency: {efficiency:.1f}%")
        else:
            print(f"   ❌ No solution possible with {case['radix']}-port switches")


def demo_scaling_analysis():
    """Show scaling behavior with different radix values"""
    print("\n📈 Scaling Analysis Demo")
    print("=" * 50)
    
    print("\nHost capacity vs Switch radix:")
    print("-" * 40)
    
    radix_values = [8, 16, 24, 32, 48, 64]
    
    for radix in radix_values:
        # Find maximum hosts for this radix with reasonable topology
        max_hosts = 0
        best_config = None
        
        # Try different host counts
        for hosts in range(10, 500, 10):
            config = calculate_optimal_topology(hosts, radix)
            if config and config['total_switches'] <= 50:  # Reasonable switch count
                max_hosts = hosts
                best_config = config
            else:
                break
        
        if best_config:
            print(f"Radix-{radix:2d}: ~{max_hosts:3d} hosts ({best_config['spine_count']}S + {best_config['leaf_count']}L)")
        else:
            print(f"Radix-{radix:2d}: Limited capacity")


def demo_topology_properties():
    """Demonstrate topology properties and characteristics"""
    print("\n🔍 Topology Properties Demo")
    print("=" * 50)
    
    # Create a medium topology for analysis
    topo = LeafSpineTopology(spine_count=3, leaf_count=6, hosts_per_leaf=3, switch_radix=24)
    
    switches = topo.switches()
    hosts = topo.hosts()
    links = topo.links()
    
    # Analyze switch types
    spine_switches = [s for s in switches if s.startswith('spine')]
    leaf_switches = [s for s in switches if s.startswith('leaf')]
    
    print(f"\n📋 Topology Analysis:")
    print(f"   Total nodes: {len(switches)} switches + {len(hosts)} hosts = {len(switches) + len(hosts)}")
    print(f"   Switch breakdown: {len(spine_switches)} spines, {len(leaf_switches)} leaves")
    print(f"   Total links: {len(links)}")
    
    # Calculate network properties
    total_hosts = len(hosts)
    max_distance = 3  # Host -> Leaf -> Spine -> Leaf -> Host
    bisection_bandwidth = len(spine_switches) * 10  # 10 Gbps per spine-leaf link
    
    print(f"\n🌐 Network Properties:")
    print(f"   Maximum hop distance: {max_distance} hops")
    print(f"   Bisection bandwidth: {bisection_bandwidth} Gbps")
    print(f"   Oversubscription ratio: 1:1 (non-blocking)")
    print(f"   Fault tolerance: Can lose any 1 spine switch")
    
    # Show addressing scheme
    print(f"\n🏷️  Addressing Scheme:")
    sample_hosts = hosts[:6] if len(hosts) >= 6 else hosts
    for i, host in enumerate(sample_hosts):
        leaf_id = (i // 3) + 1  # Assuming 3 hosts per leaf
        host_id = (i % 3) + 1
        ip = f"10.0.{leaf_id}.{host_id}/24"
        mac = f"00:00:00:00:{leaf_id:02d}:{host_id:02d}"
        print(f"   {host}: IP={ip}, MAC={mac}")
    if len(hosts) > 6:
        print(f"   ... and {len(hosts) - 6} more hosts")


def main():
    """Run all demonstrations"""
    print("🚀 Leaf-Spine Topology Comprehensive Demo")
    print("=" * 60)
    print("This demo shows topology creation and analysis without requiring root privileges.\n")
    
    try:
        # Run all demo functions
        demo_topology_creation()
        demo_auto_calculation()
        demo_scaling_analysis()
        demo_topology_properties()
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nTo run the actual Mininet topology:")
        print("sudo python3 leaf_spine_topology.py --spines 2 --leaves 4 --hosts 2")
        print("\nTo see interactive examples:")
        print("sudo python3 examples.py")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
