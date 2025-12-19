# Leaf-Spine Topology Project Summary

This project implements a **scalable custom leaf-spine topology** for Mininet using Python. The implementation can be dynamically configured based on switch radix and automatically scales to accommodate varying numbers of hosts.

## 📁 Project Files

### Core Implementation
- **`leaf_spine_topology.py`** - Main topology implementation with Mininet API
- **`examples.py`** - Example configurations and interactive demos
- **`demo.py`** - Comprehensive demonstration without requiring root privileges
- **`visualizer.py`** - Text-based topology visualization tool
- **`test_topology.py`** - Unit tests and validation suite

### Documentation
- **`README.md`** - Comprehensive project documentation
- **`SUMMARY.md`** - This summary file

## 🚀 Quick Start Commands

### 1. Basic Usage
```bash
# Run with default configuration (2 spines, 4 leaves, 2 hosts/leaf)
sudo python3 leaf_spine_topology.py

# Custom configuration
sudo python3 leaf_spine_topology.py --spines 4 --leaves 8 --hosts 3 --radix 24

# Auto-calculate for specific number of hosts
sudo python3 leaf_spine_topology.py --auto 50 --radix 32
```

### 2. Examples and Demos
```bash
# Interactive examples (requires root)
sudo python3 examples.py

# Non-root demonstration
python3 demo.py

# Topology visualization
python3 visualizer.py --demo
python3 visualizer.py --interactive
```

### 3. Testing and Validation
```bash
# Run unit tests
python3 test_topology.py

# Validate different configurations
python3 -c "from test_topology import validate_configurations; validate_configurations()"
```

## 🏗️ Architecture Features

### Leaf-Spine Design
- **Spine Tier**: High-capacity core switches
- **Leaf Tier**: Access switches connecting to hosts
- **Full Mesh**: Every leaf connects to every spine
- **Non-blocking**: 1:1 oversubscription ratio

### Scalability Features
- ✅ **Auto-scaling** based on switch radix constraints
- ✅ **Optimal calculation** for given host requirements
- ✅ **Validation** of topology constraints
- ✅ **Structured addressing** (IP and MAC)
- ✅ **QoS support** with configurable bandwidth

### Network Properties
- **Maximum distance**: 3 hops (host → leaf → spine → leaf → host)
- **Fault tolerance**: Can lose any single spine switch
- **Bisection bandwidth**: Spine count × 10 Gbps
- **Load balancing**: ECMP across multiple spines

## 📊 Example Configurations

| Configuration | Spines | Leaves | Hosts/Leaf | Total Hosts | Radix | Efficiency |
|---------------|---------|---------|-------------|-------------|-------|------------|
| Small         | 2       | 4       | 2           | 8           | 16    | 100%       |
| Medium        | 4       | 8       | 3           | 24          | 24    | 100%       |
| Large         | 6       | 12      | 4           | 48          | 32    | 100%       |
| Auto (50H)    | 3       | 17      | 3           | 51          | 24    | 98%        |

## 🧮 Auto-Calculation Algorithm

The topology automatically calculates optimal configurations:

```python
# Example: Calculate topology for 100 hosts with 32-port switches
config = calculate_optimal_topology(total_hosts=100, switch_radix=32)

# Returns: {'spine_count': 4, 'leaf_count': 25, 'hosts_per_leaf': 4, ...}
```

### Constraints
- **Leaf ports**: spine_connections + hosts + management ≤ radix
- **Spine ports**: leaf_connections + management ≤ radix
- **Optimization**: Minimize total switch count

## 🔧 API Usage

### Basic Topology Creation
```python
from leaf_spine_topology import LeafSpineTopology

# Create topology
topo = LeafSpineTopology(
    spine_count=4,
    leaf_count=8, 
    hosts_per_leaf=3,
    switch_radix=24
)

# Use with Mininet
from mininet.net import Mininet
net = Mininet(topo=topo)
net.start()
```

### Auto-Calculation
```python
from leaf_spine_topology import calculate_optimal_topology

# Find optimal configuration
config = calculate_optimal_topology(total_hosts=50, switch_radix=24)

if config:
    topo = LeafSpineTopology(**config)
```

## 🧪 Testing Features

### Unit Tests
- Topology creation validation
- Switch and host naming conventions
- Link connectivity verification
- Radix constraint checking
- Auto-calculation accuracy

### Integration Tests
- Mininet compatibility
- Network functionality
- Performance validation

## 📈 Scaling Analysis

### Port Utilization
The implementation efficiently uses switch ports:
- **16-port switches**: Up to ~210 hosts
- **24-port switches**: Up to ~490 hosts  
- **32-port switches**: Up to ~490 hosts (fewer switches needed)
- **48-port switches**: Up to ~490 hosts (optimal efficiency)

### Performance Characteristics
- **Linear scaling** with switch radix
- **Predictable performance** (3-hop maximum)
- **High availability** (spine redundancy)
- **Load distribution** across spines

## 💡 Key Benefits

1. **Educational**: Clear implementation of data center networking concepts
2. **Practical**: Real Mininet integration for experimentation
3. **Scalable**: Adapts to different switch capacities and host counts
4. **Validated**: Comprehensive testing and constraint checking
5. **Well-documented**: Extensive documentation and examples

## 🔍 Use Cases

- **Network research** and experimentation
- **Data center topology** simulation
- **Load balancing** algorithm testing
- **Failure recovery** scenario testing
- **Performance benchmarking**
- **Educational demonstrations**

## 🤝 Extensions

The codebase supports easy extensions:
- Custom link properties (bandwidth, latency, loss)
- Different switch types and capabilities
- Advanced addressing schemes
- Integration with SDN controllers
- Traffic generation and monitoring

## 📚 References

- Mininet documentation and tutorials
- Leaf-spine architecture best practices
- Data center networking principles
- OpenFlow and SDN concepts

---

**Project completed**: December 2025  
**Technologies**: Python, Mininet, OpenFlow, Software-Defined Networking  
**Purpose**: Computer Networks Lab Assignment
