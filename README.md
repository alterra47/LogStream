# LogStream: High-Performance Distributed Log Search Engine

**LogStream** is a distributed log aggregation system designed for high-throughput environments. It utilizes a hybrid architecture where **C++** handles real-time in-memory indexing for sub-millisecond search speeds, while **Python** manages API orchestration and **MongoDB** ensures persistent storage.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![C++](https://img.shields.io/badge/C++-20-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)
![Angular](https://img.shields.io/badge/Angular-17%2B-red.svg)

## 🚀 Key Features
* **Hybrid Storage Engine:** Combines the speed of C++ in-memory structures with the reliability of NoSQL disk storage.
* **Custom Inverted Index:** Implements a thread-safe inverted index algorithm (using `std::shared_mutex`) from scratch in C++ to map search terms to log IDs instantly.
* **Microservices Architecture:** Decoupled components communicating via **ZeroMQ** and REST APIs.
* **Real-Time Dashboard:** A lightweight, dependency-free Angular UI for live monitoring and searching.

## 🛠 Tech Stack

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Core Engine** | **C++20** | In-memory indexing, tokenization, and search logic. |
| **API Layer** | **Python (FastAPI)** | REST endpoints, request validation, and service orchestration. |
| **Messaging** | **ZeroMQ** | Low-latency asynchronous communication between Python and C++. |
| **Storage** | **MongoDB** | Persistent document storage for full log details. |
| **Frontend** | **Angular (Standalone)** | Responsive dashboard for visualizing and querying logs. |

## 🏗 Architecture

The system follows a "Write-Split, Read-Merge" pattern:

1.  **Ingestion:**
    * The **Python API** receives a log entry.
    * It assigns a unique 64-bit Timestamp ID.
    * It **asynchronously writes** the full log to MongoDB (Disk).
    * It **pushes** the log message to the C++ Engine via ZeroMQ (RAM).
2.  **Indexing (C++):**
    * The engine tokenizes the message (e.g., "Error in DB" -> `["error", "db"]`).
    * It updates the Inverted Index: `{"error": [ID_1], "db": [ID_1]}`.
3.  **Search:**
    * The user queries "Error".
    * Python asks C++ for all IDs associated with "Error".
    * C++ returns `[ID_1, ID_5, ID_9]` in microseconds.
    * Python fetches the full record details for those IDs from MongoDB and returns them to the UI.

## ⚙️ Installation & Setup

### Prerequisites
* **OS:** Linux (Arch/Ubuntu) or macOS.
* **Dependencies:** `g++`, `cmake`, `zeromq`, `python3`, `node/npm`, `mongodb`.

### 1. Start the Database
```bash
sudo systemctl start mongodb

```

### 2. Build & Run the C++ Engine

```bash
cd cpp_engine
mkdir build && cd build
cmake ..
make
./engine
# Output: [C++] Engine starting on tcp://*:5555...

```

### 3. Start the Python API

```bash
cd py_ingestor
source venv/bin/activate
uvicorn main:app --reload
# Output: Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000)

```

### 4. Launch the Dashboard

```bash
cd web_dashboard
ng serve
# Access at http://localhost:4200

```

## 🧪 Testing

**Stress Test Script:**
A Python script is included to flood the system with 1,000+ logs to demonstrate concurrency handling.

```bash
python stress_test.py

```