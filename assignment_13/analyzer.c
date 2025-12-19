#include <stdio.h>
#include <stdlib.h>
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
    static long start_usec = 0;

    if (start_sec == 0) {
        start_sec = header->ts.tv_sec;
        start_usec = header->ts.tv_usec;
    }

    double relative_time = (header->ts.tv_sec - start_sec) + (header->ts.tv_usec - start_usec) / 1000000.0;
    
    printf("[%0.6f] ", relative_time);

    if (ntohs(eth_header->ether_type) == ETHERTYPE_IP) {
        struct ip *ip_header = (struct ip *)(packet + sizeof(struct ether_header));
        
        if (ip_header->ip_p == IPPROTO_ICMP) {
            struct icmp *icmp_header = (struct icmp *)(packet + sizeof(struct ether_header) + (ip_header->ip_hl << 2));
            if (icmp_header->icmp_type == ICMP_ECHO) printf("ICMP Echo Request (Ping)");
            else if (icmp_header->icmp_type == ICMP_ECHOREPLY) printf("ICMP Echo Reply (Pong)");
            else printf("ICMP Type: %d", icmp_header->icmp_type);
        } else if (ip_header->ip_p == IPPROTO_TCP) printf("TCP Segment");
        else if (ip_header->ip_p == IPPROTO_UDP) printf("UDP Datagram");
        else printf("Other IP Protocol (%d)", ip_header->ip_p);
    } else if (ntohs(eth_header->ether_type) == ETHERTYPE_ARP) {
        printf("ARP Packet");
    } else {
        printf("Unknown L2 Protocol");
    }
    printf("\n");
}

int main(int argc, char *argv[]) {
    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <pcap_file>\n", argv[0]);
        return 1;
    }

    handle = pcap_open_offline(argv[1], errbuf);
    if (handle == NULL) {
        fprintf(stderr, "Could not open file: %s\n", errbuf);
        return 2;
    }

    printf("Time (s) \t Protocol Info\n");
    printf("------------------------------------------\n");
    pcap_loop(handle, 0, packet_handler, NULL);
    pcap_close(handle);
    return 0;
}