#!/usr/bin/env python3
"""
Test Suite for Leaf-Spine Topology
==================================

Unit tests to validate the leaf-spine topology implementation.
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from leaf_spine_topology import LeafSpineTopology, calculate_optimal_topology
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink


class TestLeafSpineTopology(unittest.TestCase):
    """Test cases for the LeafSpineTopology class"""
    
    def setUp(self):
        """Set up test environment"""
        self.small_topo = LeafSpineTopology(
            spine_count=2, 
            leaf_count=4, 
            hosts_per_leaf=2, 
            switch_radix=16
        )
    
    def test_topology_creation(self):
        """Test basic topology creation"""
        # Test that topology is created without errors
        self.assertIsNotNone(self.small_topo)
        
        # Check switch counts
        switches = self.small_topo.switches()
        self.assertEqual(len(switches), 6)  # 2 spines + 4 leaves
        
        # Check host counts  
        hosts = self.small_topo.hosts()
        self.assertEqual(len(hosts), 8)  # 4 leaves * 2 hosts
    
    def test_switch_naming(self):
        """Test switch naming convention"""
        switches = self.small_topo.switches()
        
        # Check spine naming
        spine_switches = [s for s in switches if s.startswith('spine')]
        self.assertEqual(len(spine_switches), 2)
        self.assertIn('spine1', spine_switches)
        self.assertIn('spine2', spine_switches)
        
        # Check leaf naming
        leaf_switches = [s for s in switches if s.startswith('leaf')]
        self.assertEqual(len(leaf_switches), 4)
        self.assertIn('leaf1', leaf_switches)
        self.assertIn('leaf4', leaf_switches)
    
    def test_host_naming(self):
        """Test host naming convention"""
        hosts = self.small_topo.hosts()
        
        # Check host count and naming
        self.assertEqual(len(hosts), 8)
        self.assertIn('h1', hosts)
        self.assertIn('h8', hosts)
    
    def test_connectivity(self):
        """Test full mesh spine-leaf connectivity"""
        # Get all links
        links = self.small_topo.links()
        
        # Should have spine-leaf links (2*4=8) + host-leaf links (8)
        expected_links = 8 + 8  # spine-leaf + host-leaf
        self.assertEqual(len(links), expected_links)
    
    def test_radix_validation(self):
        """Test radix validation"""
        # This should work (small radix, small topology)
        try:
            LeafSpineTopology(spine_count=1, leaf_count=2, hosts_per_leaf=1, switch_radix=8)
            valid = True
        except ValueError:
            valid = False
        self.assertTrue(valid)
        
        # This should fail (radix too small)
        with self.assertRaises(ValueError):
            LeafSpineTopology(spine_count=10, leaf_count=20, hosts_per_leaf=5, switch_radix=8)


class TestOptimalCalculation(unittest.TestCase):
    """Test cases for optimal topology calculation"""
    
    def test_small_calculation(self):
        """Test calculation for small host count"""
        config = calculate_optimal_topology(total_hosts=10, switch_radix=16)
        
        self.assertIsNotNone(config)
        self.assertGreaterEqual(config['leaf_count'] * config['hosts_per_leaf'], 10)
        self.assertLessEqual(config['spine_count'] + config['hosts_per_leaf'], 15)  # Within radix
    
    def test_medium_calculation(self):
        """Test calculation for medium host count"""
        config = calculate_optimal_topology(total_hosts=50, switch_radix=24)
        
        self.assertIsNotNone(config)
        self.assertGreaterEqual(config['leaf_count'] * config['hosts_per_leaf'], 50)
        self.assertLessEqual(config['spine_count'] + config['hosts_per_leaf'], 23)
    
    def test_impossible_calculation(self):
        """Test calculation for impossible constraints"""
        # Too many hosts for tiny radix
        config = calculate_optimal_topology(total_hosts=1000, switch_radix=4)
        self.assertIsNone(config)
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Single host
        config = calculate_optimal_topology(total_hosts=1, switch_radix=16)
        self.assertIsNotNone(config)
        self.assertEqual(config['hosts_per_leaf'], 1)
        
        # Large radix
        config = calculate_optimal_topology(total_hosts=100, switch_radix=64)
        self.assertIsNotNone(config)


class TestTopologyIntegration(unittest.TestCase):
    """Integration tests requiring Mininet"""
    
    def setUp(self):
        """Set up minimal topology for testing"""
        self.topo = LeafSpineTopology(
            spine_count=1, 
            leaf_count=2, 
            hosts_per_leaf=1, 
            switch_radix=8
        )
    
    def test_mininet_integration(self):
        """Test that topology works with Mininet"""
        try:
            net = Mininet(
                topo=self.topo, 
                switch=OVSSwitch, 
                link=TCLink,
                autoSetMacs=True,
                build=False
            )
            net.build()
            
            # Check that network is built
            self.assertEqual(len(net.switches), 3)  # 1 spine + 2 leaves
            self.assertEqual(len(net.hosts), 2)     # 2 hosts
            
            # Test that we can start/stop (without CLI)
            net.start()
            net.stop()
            
            success = True
        except Exception as e:
            print(f"Mininet integration test failed: {e}")
            success = False
        
        self.assertTrue(success)


def run_topology_tests():
    """Run all topology tests"""
    print("Running Leaf-Spine Topology Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases using TestLoader
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestLeafSpineTopology))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimalCalculation))
    
    # Only run integration tests if we can import mininet
    try:
        from mininet.net import Mininet
        suite.addTests(loader.loadTestsFromTestCase(TestTopologyIntegration))
        print("Including Mininet integration tests")
    except ImportError:
        print("Skipping Mininet integration tests (Mininet not available)")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print(f"❌ {len(result.failures)} tests failed, {len(result.errors)} errors")
        
    return result.wasSuccessful()


def validate_configurations():
    """Validate different topology configurations"""
    print("\nValidating Different Configurations...")
    print("-" * 40)
    
    test_configs = [
        {'spines': 2, 'leaves': 4, 'hosts': 2, 'radix': 16, 'name': 'Small'},
        {'spines': 4, 'leaves': 8, 'hosts': 3, 'radix': 24, 'name': 'Medium'},  
        {'spines': 6, 'leaves': 12, 'hosts': 4, 'radix': 32, 'name': 'Large'},
    ]
    
    all_valid = True
    
    for config in test_configs:
        try:
            topo = LeafSpineTopology(
                spine_count=config['spines'],
                leaf_count=config['leaves'], 
                hosts_per_leaf=config['hosts'],
                switch_radix=config['radix']
            )
            
            total_hosts = config['leaves'] * config['hosts']
            total_switches = config['spines'] + config['leaves']
            
            print(f"✅ {config['name']}: {total_hosts} hosts, {total_switches} switches")
            
        except Exception as e:
            print(f"❌ {config['name']}: {e}")
            all_valid = False
    
    return all_valid


if __name__ == '__main__':
    print("Leaf-Spine Topology Test Suite")
    print("==============================\n")
    
    # Run unit tests
    tests_passed = run_topology_tests()
    
    # Validate configurations  
    configs_valid = validate_configurations()
    
    # Print final result
    print("\n" + "=" * 50)
    if tests_passed and configs_valid:
        print("🎉 All tests and validations passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)
