# Leaf-Spine Topology for Mininet

Scalable leaf-spine topology implementation that auto-adjusts based on switch radix.

## Files

- `leaf_spine.py` - Main topology implementation
- `test.py` - Tests and validation
- `README.md` - This file

## Usage

### Basic Usage
```bash
# Default: 2 spines, 4 leaves, 2 hosts/leaf, radix-16
sudo python3 leaf_spine.py

# Custom configuration  
sudo python3 leaf_spine.py --spines 4 --leaves 8 --hosts 3 --radix 24

# Auto-calculate for 50 hosts
sudo python3 leaf_spine.py --auto 50 --radix 24
```

### Command Options
```
--spines, -s    Number of spine switches (default: 2)
--leaves, -l    Number of leaf switches (default: 4) 
--hosts         Hosts per leaf switch (default: 2)
--radix, -r     Switch port capacity (default: 16)
--auto, -a      Auto-calculate for N total hosts
--controller    Remote controller IP
```

### Examples
```bash
# Small topology: 8 hosts
sudo python3 leaf_spine.py --spines 2 --leaves 4 --hosts 2

# Medium topology: 24 hosts  
sudo python3 leaf_spine.py --spines 4 --leaves 8 --hosts 3 --radix 24

# Large auto-calculated: 100 hosts
sudo python3 leaf_spine.py --auto 100 --radix 32
```

### Testing
```bash
# Run tests (no root needed)
python3 test.py
```

## Architecture

- **Spine Tier**: Core switches providing interconnection
- **Leaf Tier**: Access switches connecting to hosts  
- **Full Mesh**: Every leaf connects to every spine
- **3-hop Max**: Host → Leaf → Spine → Leaf → Host

## Scaling

Auto-calculation finds optimal configuration:
- 20 hosts, radix-16: 1 spine + 2 leaves = 3 switches
- 50 hosts, radix-24: 1 spine + 3 leaves = 4 switches  
- 100 hosts, radix-32: 1 spine + 4 leaves = 5 switches

## Network Properties

- **IP Addressing**: 10.0.{leaf}.{host}/24
- **MAC Addressing**: 00:00:00:00:{leaf}:{host}
- **Bandwidth**: 10G spine-leaf, 1G host-leaf
- **Non-blocking**: 1:1 oversubscription ratio
