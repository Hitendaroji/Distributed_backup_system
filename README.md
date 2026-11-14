# Distributed Backup System with SDN-Based Failover

## Project Overview

The Distributed Backup System is a file backup application that uses TCP socket programming to transfer files from clients to backup servers.

The system divides files into smaller chunks, verifies data integrity using SHA-256 checksums, and supports resuming interrupted transfers.

Software Defined Networking (SDN) is integrated using the Ryu controller and Mininet to provide network path selection and automatic failover when a network link fails.

## Key Features

- TCP-based file transfer
- File chunking for efficient data transmission
- SHA-256 checksum verification
- File replication across multiple backup servers
- Resume support for interrupted transfers
- Handling of unavailable backup servers
- SDN-based primary and backup path selection
- Automatic network failover and path restoration
- Transfer time and throughput measurement

## Technologies Used

- Python
- TCP Socket Programming
- SHA-256
- Ryu SDN Controller
- Mininet
- Open vSwitch
- OpenFlow 1.3
- Docker
- Ubuntu Linux

## System Architecture

### 1. Application Layer

The client divides the original file into smaller chunks and transfers them to backup servers using TCP.

Each chunk contains:
- Chunk ID
- Chunk size
- SHA-256 checksum
- Actual file data

The server verifies each chunk using its checksum and stores the received data. Once all chunks are available, the original file is reconstructed.

### 2. Distributed Backup

The application supports replication across three backup server instances.

If one backup server becomes unavailable, the client continues attempting transfers to the remaining servers.

### 3. SDN Network Layer

The Mininet topology consists of:
- One client host (h1)
- One destination server host (h2)
- Four Open vSwitch switches (s1, s2, s3, s4)
- One Ryu SDN controller

**Primary Path:**

h1 → s1 → s2 → s4 → h2

**Backup Path:**

h1 → s1 → s3 → s4 → h2

The Ryu controller monitors link status and updates forwarding rules when the primary path fails. When the primary link is restored, the controller switches traffic back to the primary path.

## Project Structure

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
├── .gitignore
└── README.md
```

## Running the Project

### Prerequisites

- Ubuntu Linux or Ubuntu through WSL2
- Python 3
- Docker
- Mininet
- Open vSwitch
- Ryu SDN Controller

### Step 1: Start the Ryu Controller

Start the existing Docker container:

```bash
sudo docker start -ai ryu-controller
```

Inside the container
