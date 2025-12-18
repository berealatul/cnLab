#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/ip_icmp.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <sys/time.h>

/**
 * Generic Checksum calculation function.
 */
unsigned short checksum(unsigned short *ptr, int nbytes) {
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
        *((u_char *)&oddbyte) = *(u_char *)ptr;
        sum += oddbyte;
    }

    sum = (sum >> 16) + (sum & 0xffff);
    sum = sum + (sum >> 16);
    answer = (short)~sum;

    return (answer);
}

// ICMP Timestamp structure as defined in RFC 792
struct icmp_timestamp {
    u_int8_t type;
    u_int8_t code;
    u_int16_t checksum;
    u_int16_t id;
    u_int16_t sequence;
    u_int32_t originate_timestamp;
    u_int32_t receive_timestamp;
    u_int32_t transmit_timestamp;
};

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: sudo %s <Target IP>\n", argv[0]);
        return 1;
    }

    char *target_ip = argv[1];

    // Create raw ICMP socket
    int s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (s < 0) {
        perror("Socket creation failed");
        exit(1);
    }

    struct sockaddr_in dest;
    dest.sin_family = AF_INET;
    dest.sin_addr.s_addr = inet_addr(target_ip);

    char packet[sizeof(struct icmp_timestamp)];
    struct icmp_timestamp *icmp = (struct icmp_timestamp *)packet;

    // Set ICMP Header fields
    icmp->type = 13; // ICMP_TIMESTAMP (Type 13)
    icmp->code = 0;
    icmp->checksum = 0;
    icmp->id = getpid();
    icmp->sequence = 1;

    // Get current time since midnight in milliseconds
    struct timeval tv;
    gettimeofday(&tv, NULL);
    uint32_t milliseconds = (tv.tv_sec % 86400) * 1000 + (tv.tv_usec / 1000);
    
    icmp->originate_timestamp = htonl(milliseconds);
    icmp->receive_timestamp = 0;
    icmp->transmit_timestamp = 0;

    // Calculate ICMP Checksum
    icmp->checksum = checksum((unsigned short *)icmp, sizeof(struct icmp_timestamp));

    // Send the packet
    if (sendto(s, packet, sizeof(struct icmp_timestamp), 0, (struct sockaddr *)&dest, sizeof(dest)) <= 0) {
        perror("sendto failed");
    } else {
        printf("ICMP Timestamp Message sent to %s\n", target_ip);
    }

    close(s);
    return 0;
}