# LogStream: High-Performance Distributed Log Search Engine

**LogStream** is a distributed log aggregation system designed for high-throughput enterprise environments. It utilizes a hybrid microservices architecture where **C++** handles real-time in-memory indexing for sub-millisecond search speeds, **C# (.NET)** manages reliable persistent storage via batch processing, and **Python** orchestrates the API gateway.

## 🚀 Key Features

* **Hybrid Storage Engine:** Combines the speed of **C++ in-memory** structures with the reliability of **PostgreSQL** relational storage.
* **Custom Inverted Index:** Implements a thread-safe inverted index algorithm (using `std::shared_mutex`) from scratch in C++ to map search terms to log IDs instantly.
* **Reliable Batch Processing:** A background **C# Worker Service** buffers high-velocity logs and performs bulk inserts into SQL, ensuring zero data loss under heavy load (1000+ logs/sec).
* **Microservices Architecture:** Decoupled components communicating via a **ZeroMQ Pub-Sub** mesh.
* **Real-Time Dashboard:** A lightweight, dependency-free **Angular** UI for live monitoring and searching.

## 🛠 Tech Stack

| Component | Technology | Role |
| --- | --- | --- |
| **Core Engine** | **C++20** | In-memory indexing, tokenization, and search logic (RAM). |
| **Log Processor** | **C# (.NET 8)** | High-performance background worker for batch SQL ingestion. |
| **API Layer** | **Python (FastAPI)** | REST endpoints, validation, and Pub-Sub orchestration. |
| **Messaging** | **ZeroMQ** | Low-latency asynchronous communication (Pub/Sub pattern). |
| **Storage** | **PostgreSQL** | Persistent relational storage for full log records. |
| **Frontend** | **Angular** | Responsive dashboard for visualizing and querying logs. |

## 🏗 Architecture

The system follows a **"Fan-Out Write, Merge Read"** pattern:

1. **Ingestion (Pub-Sub):**
* The **Python API** receives a log entry and assigns a unique ID.
* It **Publishes** the log to the ZeroMQ network (`tcp://*:5556`).
* **Subscriber 1 (C++):** Instantly tokenizes and indexes the message in RAM.
* **Subscriber 2 (C#):** Buffers the log into a thread-safe queue.


2. **Persistence (Batching):**
* The **C# Service** monitors its buffer.
* Once the buffer hits 100 logs (or 500ms elapses), it performs a **Bulk Insert** into PostgreSQL.
* This handles bursts of traffic without locking the database connection.


3. **Search:**
* The user queries "Error".
* Python asks **C++** via ZeroMQ (`REQ/REP`) for all IDs matching "Error".
* C++ returns `[ID_1, ID_5, ID_9]` in microseconds.
* Python queries **PostgreSQL** for the full details of those specific IDs and returns them to the UI.



## ⚙️ Installation & Setup

### Prerequisites

* **OS:** Linux (Arch/Ubuntu) or macOS.
* **Dependencies:** `g++`, `cmake`, `dotnet-sdk`, `zeromq`, `python3`, `postgresql`, `node/npm`.

### 1. Start the Database

Ensure PostgreSQL is running and the database `logstream_db` exists.

```bash
sudo systemctl start postgresql
# (Optional) Verify DB creation
# sudo -u postgres psql -c "CREATE DATABASE logstream_db;"

```

### 2. Auto-Launch System (Recommended)

A master script is provided to launch all services (C++, C#, Python, Angular) in the background.

```bash
chmod +x start.sh
./start.sh
# Check logs: tail -f csharp_log.txt python_log.txt

```

### Manual Startup (Alternative)

<details>
<summary>Click to expand manual commands</summary>

#### A. Run C++ Engine

```bash
cd cpp_engine/build && ./engine

```

#### B. Run C# Processor

```bash
cd csharp_processor/LogProcessor && dotnet run

```

#### C. Run Python API

```bash
cd py_ingestor && source venv/bin/activate && uvicorn main:app --reload

```

#### D. Run Dashboard

```bash
cd web_dashboard && ng serve

```

</details>

## 🧪 Testing & Verification

**Stress Test Script:**
A Python script is included to verify throughput and data integrity. It sends 1,000 logs and verifies that C++ indexed them and C# saved them.

```bash
python stress_test.py

```

**Expected Output:**

```text
🚀 Starting Stress Test: Sending 1000 logs...
✅ Ingestion Finished...
🔍 Verifying data integrity...
🎉 SUCCESS: 100% Data Integrity Verified!

```