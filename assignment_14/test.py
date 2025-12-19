#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append(os.path.dirname(__file__))

from leaf_spine import LeafSpineTopology, calculate_optimal_topology


class TestLeafSpine(unittest.TestCase):
    
    def test_small_topology(self):
        topo = LeafSpineTopology(2, 4, 2, 16)
        self.assertEqual(len(topo.switches()), 6)
        self.assertEqual(len(topo.hosts()), 8)
        self.assertEqual(len(topo.links()), 16)
    
    def test_switch_naming(self):
        topo = LeafSpineTopology(2, 3, 1, 16)
        switches = topo.switches()
        self.assertIn('spine1', switches)
        self.assertIn('spine2', switches)
        self.assertIn('leaf1', switches)
        self.assertIn('leaf3', switches)
    
    def test_radix_validation(self):
        with self.assertRaises(ValueError):
            LeafSpineTopology(10, 20, 5, 8)
    
    def test_auto_calculation(self):
        config = calculate_optimal_topology(20, 16)
        self.assertIsNotNone(config)
        self.assertGreaterEqual(config['leaf_count'] * config['hosts_per_leaf'], 20)
    
    def test_impossible_config(self):
        config = calculate_optimal_topology(1000, 4)
        self.assertIsNone(config)


def validate_configs():
    configs = [
        {'spine_count': 2, 'leaf_count': 4, 'hosts_per_leaf': 2, 'switch_radix': 16},
        {'spine_count': 4, 'leaf_count': 8, 'hosts_per_leaf': 3, 'switch_radix': 24},
        {'spine_count': 6, 'leaf_count': 12, 'hosts_per_leaf': 4, 'switch_radix': 32},
    ]
    
    print("Validating configurations...")
    for i, config in enumerate(configs, 1):
        try:
            topo = LeafSpineTopology(**config)
            total_hosts = config['leaf_count'] * config['hosts_per_leaf']
            print(f"Config {i}: ✓ {total_hosts} hosts, {config['spine_count'] + config['leaf_count']} switches")
        except Exception as e:
            print(f"Config {i}: ✗ {e}")


def test_auto_calc():
    print("\nAuto-calculation tests...")
    for hosts, radix in [(20, 16), (50, 24), (100, 32)]:
        config = calculate_optimal_topology(hosts, radix)
        if config:
            efficiency = hosts / (config['leaf_count'] * config['hosts_per_leaf']) * 100
            print(f"{hosts} hosts, radix-{radix}: {config['spine_count']}S+{config['leaf_count']}L ({efficiency:.1f}%)")
        else:
            print(f"{hosts} hosts, radix-{radix}: No solution")


if __name__ == '__main__':
    print("Leaf-Spine Topology Tests")
    print("=" * 30)
    
    # Unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLeafSpine)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    # Validation tests
    validate_configs()
    test_auto_calc()
    
    print(f"\nResult: {'✓ PASS' if result.wasSuccessful() else '✗ FAIL'}")
