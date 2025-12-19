#include <stdio.h>
#include <pcap.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <netinet/udp.h>
#include <netinet/ip_icmp.h>
#include <net/ethernet.h>
#include <time.h>

void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    struct ether_header *eth_header = (struct ether_header *) packet;
    static long start_sec = 0;
    if (start_sec == 0) start_sec = header->ts.tv_sec;

    double timestamp = (header->ts.tv_sec - start_sec) + (header->ts.tv_usec / 1000000.0);
    
    printf("[%0.6f] ", timestamp);

    if (ntohs(eth_header->ether_type) == ETHERTYPE_IP) {
        struct ip *ip_header = (struct ip *)(packet + sizeof(struct ether_header));
        
        if (ip_header->ip_p == IPPROTO_ICMP) {
            printf("ICMP Packet Detected\n");
            printf("    |--- (L2: Ethernet) --- (L3: IPv4) --- (L4: ICMP)\n");
        } else if (ip_header->ip_p == IPPROTO_TCP) {
            printf("TCP Packet Detected\n");
        } else if (ip_header->ip_p == IPPROTO_UDP) {
            printf("UDP Packet Detected\n");
        }
    } else if (ntohs(eth_header->ether_type) == ETHERTYPE_ARP) {
        printf("ARP Packet Detected\n");
        printf("    |--- (L2: Ethernet) --- (L3: ARP)\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <pcap_file>\n", argv[0]);
        return 1;
    }

    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle = pcap_open_offline(argv[1], errbuf);

    if (handle == NULL) {
        fprintf(stderr, "Error opening pcap: %s\n", errbuf);
        return 1;
    }

    printf("Time (s)   | Protocol Sequence\n");
    printf("-----------|------------------\n");
    pcap_loop(handle, 0, packet_handler, NULL);
    pcap_close(handle);
    return 0;
}