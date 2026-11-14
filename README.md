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
├── requirements.txt    
├── controller_basic.py	
└── README.md


```

## 6. Installation and Prerequisites

The project was developed and tested using Ubuntu on WSL2.

Required software:

- Python 3
- Git
- Docker
- Mininet
- Open vSwitch
- Ryu SDN Controller

### Install Python dependencies

```bash
sudo apt update
sudo apt install python3 python3-pip git -y
```

### Install Mininet and Open vSwitch

```bash
sudo apt install mininet openvswitch-switch -y
sudo systemctl enable --now openvswitch-switch
```

### Set up Ryu using Docker

Create a Docker container using Python 3.8:

```bash
sudo docker run -it --name ryu-controller -p 6653:6653 -v "$PWD/controller.py:/app/controller.py" -w /app python:3.8-slim bash
```

Inside the container, install Ryu:

```bash
pip install ryu==4.34
pip install eventlet==0.30.2
```

Start the controller:

```bash
ryu-manager --ofp-tcp-listen-port 6653 controller.py
```

Keep this terminal running.

## 7. Running the Project

Open another Ubuntu terminal and navigate to the project directory.

### Step 1: Start Mininet

```bash
cd ~/distributed-backup-system
sudo mn -c
sudo mn --custom topology/backup_topology.py --topo backup --controller=remote,ip=127.0.0.1,port=6653 --switch ovs,protocols=OpenFlow13
```

### Step 2: Start the Backup Server

Inside the Mininet CLI, run:

```bash
h2 sh -c 'cd ~/distributed-backup-system && python3 server/tcp_server.py 5000 backup_mininet' &
```


### Step 3: Generate a Sample File

Open another Ubuntu terminal:

```bash
cd ~/distributed-backup-systempython3 -c "open('mininet_sample.bin','wb').write(b'MININET_BACKUP_TEST_' * 500)"
```

### Step 4: Transfer the File

Inside the Mininet CLI:

```bash
h1 sh -c 'cd ~/distributed-backup-system && PYTHONPATH=. python3 client/mininet_client.py'
```

Replace the project path with your actual project directory.

## 8. Testing Network Failover

The topology provides two alternative paths between the client and server.

### Simulate Primary Link Failure

Inside Mininet:

```bash
link s1 s2 down
```

The Ryu controller detects the failure and activates the backup path.

### Restore Primary Link

```bash
link s1 s2 up
```

The controller switches back to the primary path.

## 9. Testing and Results

The project was tested for:

- Successful TCP file transfers.
- File chunking and reconstruction.
- SHA-256 checksum verification.
- Interrupted transfer and resume functionality.
- Replication across multiple backup server instances.
- Backup server failure handling.
- SDN primary and backup path switching.
- File transfer through the backup network path.

A controller-side SDN failover reaction time of approximately 3.752 milliseconds was observed during testing.

This measurement represents the controller's reaction time from receiving a link-down event until sending updated forwarding rules.

## 10. Implementation Notes

- Three backup server instances were tested separately on localhost.
- The Mininet demonstration uses one client and one destination server with two alternative network paths.
- The Ryu controller uses predefined forwarding rules for the implemented topology.
- The measured controller reaction time is not the complete end-to-end application recovery time.

## 11. Conclusion

The Distributed Backup System combines TCP-based file transfer, chunking, checksum verification, interrupted transfer recovery, multiple backup server replication, and SDN-based network failover.

The project demonstrates how application-level fault tolerance and network-level redundancy can improve the reliability of file backup operations.
