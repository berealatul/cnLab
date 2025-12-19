#!/usr/bin/env python3
"""
Leaf-Spine Topology Visualizer
==============================

This script provides a text-based visualization of the leaf-spine topology
to help understand the structure and connections.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from leaf_spine_topology import LeafSpineTopology, calculate_optimal_topology


def draw_topology(spine_count, leaf_count, hosts_per_leaf, radix):
    """Draw a text-based visualization of the topology"""
    
    print(f"\n📊 Leaf-Spine Topology Visualization")
    print(f"Configuration: {spine_count} spines, {leaf_count} leaves, {hosts_per_leaf} hosts/leaf, radix-{radix}")
    print("=" * 80)
    
    # Draw spine tier
    print("\n🔝 SPINE TIER (Core Layer)")
    spine_line = ""
    for i in range(spine_count):
        spine_line += f"[S{i+1:2d}]"
        if i < spine_count - 1:
            spine_line += "    "
    print(f"    {spine_line}")
    
    # Draw connections
    print("\n🔗 SPINE-LEAF CONNECTIONS (Full Mesh)")
    for row in range(3):
        line = ""
        for i in range(spine_count):
            if row == 0:
                line += " | | "
            elif row == 1:
                line += " | | "
            else:
                line += " | | "
            if i < spine_count - 1:
                line += "    "
        print(f"    {line}")
    
    # Draw leaf tier
    print("🍃 LEAF TIER (Access Layer)")
    leaf_line = ""
    for i in range(leaf_count):
        leaf_line += f"[L{i+1:2d}]"
        if i < leaf_count - 1:
            leaf_line += "  "
    print(f"    {leaf_line}")
    
    # Draw host connections
    print("\n🔗 LEAF-HOST CONNECTIONS")
    for row in range(2):
        line = ""
        for i in range(leaf_count):
            if row == 0:
                line += " | | "
            else:
                line += " | | "
            if i < leaf_count - 1:
                line += "  "
        print(f"    {line}")
    
    # Draw hosts
    print("🏠 HOST TIER")
    for host_row in range(hosts_per_leaf):
        host_line = ""
        for leaf in range(leaf_count):
            host_id = leaf * hosts_per_leaf + host_row + 1
            host_line += f"[H{host_id:2d}]"
            if leaf < leaf_count - 1:
                host_line += "  "
        print(f"    {host_line}")
    
    # Print statistics
    total_hosts = leaf_count * hosts_per_leaf
    total_switches = spine_count + leaf_count
    spine_leaf_links = spine_count * leaf_count
    host_leaf_links = total_hosts
    total_links = spine_leaf_links + host_leaf_links
    
    print(f"\n📈 TOPOLOGY STATISTICS")
    print(f"    Total hosts: {total_hosts}")
    print(f"    Total switches: {total_switches} ({spine_count} spines + {leaf_count} leaves)")
    print(f"    Total links: {total_links} ({spine_leaf_links} spine-leaf + {host_leaf_links} host-leaf)")
    print(f"    Network diameter: 3 hops (host → leaf → spine → leaf → host)")
    print(f"    Bisection bandwidth: {spine_count * 10} Gbps")


def draw_scaling_comparison():
    """Show scaling comparison across different configurations"""
    
    print(f"\n🔄 Scaling Comparison")
    print("=" * 80)
    
    configs = [
        {'spines': 2, 'leaves': 4, 'hosts': 2, 'radix': 16, 'name': 'Small'},
        {'spines': 4, 'leaves': 8, 'hosts': 3, 'radix': 24, 'name': 'Medium'},
        {'spines': 6, 'leaves': 12, 'hosts': 4, 'radix': 32, 'name': 'Large'}
    ]
    
    print(f"\n{'Config':<8} {'Spines':<8} {'Leaves':<8} {'H/L':<5} {'Hosts':<8} {'Switches':<10} {'Links':<8} {'Radix':<8}")
    print("-" * 80)
    
    for config in configs:
        total_hosts = config['leaves'] * config['hosts']
        total_switches = config['spines'] + config['leaves']
        total_links = (config['spines'] * config['leaves']) + total_hosts
        
        print(f"{config['name']:<8} {config['spines']:<8} {config['leaves']:<8} "
              f"{config['hosts']:<5} {total_hosts:<8} {total_switches:<10} "
              f"{total_links:<8} {config['radix']:<8}")


def draw_port_usage_analysis():
    """Analyze port usage for different configurations"""
    
    print(f"\n🔌 Port Usage Analysis")
    print("=" * 80)
    
    configs = [
        {'spines': 2, 'leaves': 4, 'hosts': 2, 'radix': 16},
        {'spines': 4, 'leaves': 8, 'hosts': 3, 'radix': 24},
        {'spines': 6, 'leaves': 12, 'hosts': 4, 'radix': 32}
    ]
    
    print(f"\n{'Spines':<8} {'Leaves':<8} {'Radix':<8} {'Spine Usage':<15} {'Leaf Usage':<15} {'Status':<10}")
    print("-" * 80)
    
    for config in configs:
        spine_ports_used = config['leaves'] + 1  # leaves + management
        leaf_ports_used = config['spines'] + config['hosts'] + 1  # spines + hosts + mgmt
        
        spine_util = (spine_ports_used / config['radix']) * 100
        leaf_util = (leaf_ports_used / config['radix']) * 100
        
        status = "✅ OK" if max(spine_util, leaf_util) <= 100 else "❌ OVERFLOW"
        
        print(f"{config['spines']:<8} {config['leaves']:<8} {config['radix']:<8} "
              f"{spine_ports_used}/{config['radix']} ({spine_util:4.1f}%){'':<3} "
              f"{leaf_ports_used}/{config['radix']} ({leaf_util:4.1f}%){'':<3} {status:<10}")


def interactive_visualizer():
    """Interactive topology visualizer"""
    
    print("🎮 Interactive Topology Visualizer")
    print("=" * 50)
    
    while True:
        print(f"\nOptions:")
        print("1. Visualize custom topology")
        print("2. Auto-calculate and visualize")
        print("3. Show scaling comparison") 
        print("4. Port usage analysis")
        print("5. Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                spines = int(input("Number of spine switches: "))
                leaves = int(input("Number of leaf switches: "))
                hosts = int(input("Hosts per leaf switch: "))
                radix = int(input("Switch radix: "))
                
                try:
                    # Validate topology
                    topo = LeafSpineTopology(spines, leaves, hosts, radix)
                    draw_topology(spines, leaves, hosts, radix)
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '2':
                total_hosts = int(input("Target number of hosts: "))
                radix = int(input("Switch radix: "))
                
                config = calculate_optimal_topology(total_hosts, radix)
                if config:
                    print(f"\n✅ Optimal configuration found:")
                    draw_topology(
                        config['spine_count'],
                        config['leaf_count'], 
                        config['hosts_per_leaf'],
                        radix
                    )
                else:
                    print(f"❌ No valid configuration found for {total_hosts} hosts with radix-{radix}")
            
            elif choice == '3':
                draw_scaling_comparison()
            
            elif choice == '4':
                draw_port_usage_analysis()
            
            elif choice == '5':
                print("Goodbye! 👋")
                break
            
            else:
                print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except ValueError:
            print("❌ Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == '--interactive':
            interactive_visualizer()
        elif sys.argv[1] == '--demo':
            # Demo mode with predefined examples
            examples = [
                (2, 4, 2, 16, "Small Example"),
                (4, 6, 3, 24, "Medium Example"), 
                (6, 8, 4, 32, "Large Example")
            ]
            
            for spines, leaves, hosts, radix, name in examples:
                print(f"\n{name}")
                print("=" * len(name))
                draw_topology(spines, leaves, hosts, radix)
            
            draw_scaling_comparison()
            draw_port_usage_analysis()
        else:
            print("Usage:")
            print("  python3 visualizer.py --interactive  # Interactive mode")
            print("  python3 visualizer.py --demo        # Demo mode")
    else:
        # Default: run interactive mode
        interactive_visualizer()


if __name__ == '__main__':
    main()
