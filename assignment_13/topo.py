from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel

class BinaryTreeTopo(Topo):
    "Binary Tree Topology with 7 switches."
    def build(self):
        # Add 7 switches
        s1 = self.addSwitch('s1') # Root
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')
        s5 = self.addSwitch('s5')
        s6 = self.addSwitch('s6')
        s7 = self.addSwitch('s7')

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # Connect switches in a binary tree
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s2, s5)
        self.addLink(s3, s6)
        self.addLink(s3, s7)

        # Connect hosts to leaves
        self.addLink(h1, s4)
        self.addLink(h2, s7)

topos = { 'binarytree': ( lambda: BinaryTreeTopo() ) }