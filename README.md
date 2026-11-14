# Distributed Backup System with SDN-Based Failover

## 1. Project Overview

The Distributed Backup System is a file backup application that transfers files from a client to backup servers using TCP.

The system divides files into smaller chunks, calculates SHA-256 checksums to verify data integrity, and supports resuming interrupted transfers.

Software Defined Networking (SDN) is integrated using Ryu and Mininet to dynamically switch between primary and backup network paths when a link failure occurs.

## 2. Features

- TCP-based file transfer.
- File chunking for efficient transfer.
- SHA-256 checksum verification.
- Multiple backup server replication.
- Resume interrupted file transfers.
- Backup server failure handling.
- SDN-based primary and backup path selection.
- Automatic network failover and path restoration.
- Transfer time and throughput measurement.

## 3. Technologies Used

- Python
- TCP Socket Programming
- SHA-256
- Ryu SDN Controller
- Mininet
- Open vSwitch
- OpenFlow 1.3
- Docker
- Ubuntu Linux

## 4. Project Architecture

### Application Layer

The client divides files into chunks and sends them to backup servers using TCP.

Each chunk contains:
- Chunk ID
- Chunk size
- SHA-256 checksum
- File data

The server verifies the checksum and stores the received chunks. Once all chunks are available, the original file is reconstructed.

### Distributed Backup

The application supports replication across three backup server instances.

If one backup server is unavailable, the client continues attempting transfers to the remaining servers.

### SDN Network Layer

The Mininet topology contains:
- One client host (h1)
- One destination server host (h2)
- Four Open vSwitch switches (s1, s2, s3, s4)

Two network paths are available:

Primary:
h1 -> s1 -> s2 -> s4 -> h2

Backup:
h1 -> s1 -> s3 -> s4 -> h2

The Ryu controller monitors link status and changes the forwarding rules when the primary path fails.

When the primary link is restored, the controller switches back to the primary path.

## 5. Project Structure

```text
distributed-backup-system/
│
├── client/
│   ├── tcp_client.py
│   └── mininet_client.py
│
├── server/
│   └── tcp_server.py
│
├── common/
│   ├── chunker.py
│   └── checksum.py
│
├── tests/
│   └── test_chunking.py
│
├── topology/
│   └── backup_topology.py
│
├── controller.py
├── controller_basic.py
└── README.md
