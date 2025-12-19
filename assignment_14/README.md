# Scalable Leaf-Spine Topology for Mininet

This project implements a scalable custom leaf-spine topology in Mininet using Python. The topology can be dynamically configured based on switch radix and automatically scales to accommodate varying numbers of hosts.

## 🏗️ Architecture Overview

The leaf-spine topology consists of two tiers:

- **Spine Tier (Core)**: High-capacity switches that provide interconnection
- **Leaf Tier (Access)**: Switches that connect directly to hosts

### Key Features

- ✅ **Scalable Design**: Automatically adjusts based on switch radix
- ✅ **Full Mesh Connectivity**: Every leaf connects to every spine
- ✅ **Auto-calculation**: Optimal topology configuration for given constraints  
- ✅ **Validation**: Built-in constraint checking
- ✅ **Structured Addressing**: Logical IP and MAC address assignment
- ✅ **QoS Support**: Configurable bandwidth and latency

## 📋 Requirements

- Python 3.6+
- Mininet 2.3+
- Open vSwitch
- Linux environment (tested on Ubuntu/Debian)

## 🚀 Quick Start

### Basic Usage

```bash
# Run with default configuration (2 spines, 4 leaves, 2 hosts/leaf)
sudo python3 leaf_spine_topology.py

# Custom configuration
sudo python3 leaf_spine_topology.py --spines 4 --leaves 8 --hosts 3 --radix 24

# Auto-calculate for 50 hosts
sudo python3 leaf_spine_topology.py --auto 50 --radix 32
```

### Running Examples

```bash
# Interactive examples
sudo python3 examples.py

# Direct example execution
sudo python3 -c "
from examples import run_small_topology
run_small_topology()
"
```

## 📖 Detailed Usage

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--spines` | `-s` | Number of spine switches | 2 |
| `--leaves` | `-l` | Number of leaf switches | 4 |
| `--hosts` | `-h` | Hosts per leaf switch | 2 |
| `--radix` | `-r` | Switch port capacity | 16 |
| `--auto` | `-a` | Auto-calculate for N hosts | None |
| `--controller` | `-c` | Remote controller IP | None |

### Examples

#### 1. Small Topology
```bash
sudo python3 leaf_spine_topology.py --spines 2 --leaves 4 --hosts 2 --radix 16
```
- 2 spine switches
- 4 leaf switches  
- 8 total hosts
- 16-port switches

#### 2. Medium Topology
```bash
sudo python3 leaf_spine_topology.py --spines 4 --leaves 8 --hosts 3 --radix 24
```
- 4 spine switches
- 8 leaf switches
- 24 total hosts
- 24-port switches

#### 3. Large Topology
```bash
sudo python3 leaf_spine_topology.py --spines 8 --leaves 16 --hosts 4 --radix 32
```
- 8 spine switches
- 16 leaf switches
- 64 total hosts  
- 32-port switches

#### 4. Auto-Calculated Topology
```bash
sudo python3 leaf_spine_topology.py --auto 100 --radix 48
```
Automatically calculates optimal configuration for 100 hosts using 48-port switches.

## 🔧 API Reference

### LeafSpineTopology Class

```python
class LeafSpineTopology(Topo):
    def __init__(self, spine_count=2, leaf_count=4, hosts_per_leaf=2, switch_radix=16):
        """
        Initialize leaf-spine topology
        
        Args:
            spine_count (int): Number of spine switches
            leaf_count (int): Number of leaf switches  
            hosts_per_leaf (int): Hosts per leaf switch
            switch_radix (int): Switch port capacity
        """
```

### Helper Functions

```python
def calculate_optimal_topology(total_hosts, switch_radix=16):
    """
    Calculate optimal topology parameters
    
    Args:
        total_hosts (int): Target number of hosts
        switch_radix (int): Switch port capacity
        
    Returns:
        dict: Optimal configuration or None if impossible
    """
```

## 📊 Scaling Analysis

The topology scales based on switch radix constraints:

### Port Usage
- **Leaf Switch**: `spine_connections + hosts + 1 (mgmt) ≤ radix`
- **Spine Switch**: `leaf_connections + 1 (mgmt) ≤ radix`

### Example Scaling
| Hosts | Radix | Spines | Leaves | Hosts/Leaf | Total Switches |
|-------|-------|--------|--------|------------|----------------|
| 20    | 16    | 2      | 10     | 2          | 12             |
| 50    | 24    | 3      | 17     | 3          | 20             |
| 100   | 32    | 4      | 25     | 4          | 29             |
| 200   | 48    | 5      | 40     | 5          | 45             |

## 🛠️ Advanced Configuration

### Network Properties
The topology uses the following default settings:

```python
# Spine-Leaf Links
bandwidth = 10  # Gbps
delay = '1ms'
loss = 0

# Host-Leaf Links  
bandwidth = 1   # Gbps
delay = '0.5ms'
loss = 0
```

### IP Addressing Scheme
- Hosts: `10.0.{leaf_id}.{host_id}/24`
- MAC: `00:00:00:00:{leaf_id:02d}:{host_id:02d}`

### Using with Remote Controller
```bash
sudo python3 leaf_spine_topology.py --controller 192.168.1.100
```

## 🧪 Testing

### Connectivity Tests
```bash
# In Mininet CLI
mininet> pingall

# Test specific hosts
mininet> h1 ping h8

# Bandwidth test
mininet> iperf h1 h8
```

### Performance Tests
```bash
# Multiple flows
mininet> iperf h1 h2 & iperf h3 h4 & iperf h5 h6

# Throughput matrix
mininet> py net.pingall(verbose=True)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Radix Too Small
```
ValueError: Leaf switches need X ports but radix is Y
```
**Solution**: Increase `--radix` or reduce topology size

#### 2. Controller Connection Failed
```
Unable to contact the remote controller
```  
**Solution**: Check controller IP and ensure it's running

#### 3. Permission Denied
```
Permission denied
```
**Solution**: Run with `sudo`

### Debug Mode
```bash
# Enable verbose logging
sudo python3 leaf_spine_topology.py --spines 2 --leaves 4 -v

# Check switch status
mininet> sh ovs-vsctl show

# View flows
mininet> sh ovs-ofctl dump-flows spine1
```

## 📁 File Structure

```
assignment_14/
├── leaf_spine_topology.py    # Main topology implementation
├── examples.py               # Example configurations
├── README.md                 # This documentation
└── test_topology.py          # Unit tests (optional)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of a computer networks lab assignment. Use for educational purposes.

## 📚 References

- [Mininet Documentation](http://mininet.org/)
- [OpenFlow Specification](https://www.opennetworking.org/software-defined-standards/specifications/)
- [Leaf-Spine Architecture](https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-737022.html)

## 🏷️ Version History

- **v1.0**: Initial implementation with basic leaf-spine topology
- **v1.1**: Added auto-calculation and scaling analysis
- **v1.2**: Enhanced with examples and comprehensive documentation

---

**Author**: Computer Networks Lab Assignment  
**Date**: December 2025  
**Institution**: Network Engineering Course
