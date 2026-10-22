# Application Scaling, Vector DB Rate Limiting & Locking Strategy

## 1. Problem: 10-Second Rebuild Coordination

Since full rebuild takes 10 seconds, multiple application instances detecting empty VDB simultaneously causes conflicts and wasted resources.

## 2. Solution: Introduce Locking: Application In-Memory + VDB Remote Locking

Single unified lock affects both embedding and VDB operations:
- **Local locks (5s)**: Batch Processing - SINGLE 5-second local lock that affects both embedding AND VDB operations together
- **Remote locks (5min)**: VDB-based coordination across different application instances

Using VDB for remote locking because:
- Same library already used for data storage
- Code can be encapsulated in existing VDB client
- No additional infrastructure needed
- Embedding service itself has no locking - it's called within VDB service's locked context

## 3. VDB Remote Locking Implementation

### Dedicated Lock Collection

Create special collection in Qdrant for lock management:

```text
[VDB Collections Layout]

Data Collections:
|-- laptops_vectors (actual data)
|-- reviews_vectors (actual data)
+-- specs_vectors (actual data)

Lock Collections:
|-- laptops_locks (coordination)
|-- reviews_locks (coordination)
+-- specs_locks (coordination)
```

### Lock Record Structure

- `expires_at` - important field - used to detect expiry

```text
{
  "id": "batch_processing_lock",
  "vector": [0.0],
  "payload": {
    "node_id": "app_instance_1",
    "acquired_at": 1704067200000,
    "expires_at": 1704067500000,
    "operation": "loadRecords"
  }
}
```

## 4. Complete Locking Mechanism with Load Balancing

```text
Coordinated Rebuild Sequence:

[Load Balancer] [App Instances] [Local Memory] [VDB Locks] [Batch Processing Unit]
       |               |                  |            |              |
----------Query------->|  (5s limit)      |            |              |
       |               |--Check Count---->|----------->|              |
       |               |<-Empty VDB / Non-Exp LOCKED---|              |
       |               |                  |            |              |
       |               |                  |            |              |
       |               | (If VDB Empty)   |            |              |
       |               |---+              |            |              |
       |               |   |  (5s limit)  |            |              |
       |               |   |--Local Lock->|            |              |
       |               |   |<-Success-----|            |              |
       |               |   |              |            |              |
       |               |   |--Dist Lock---|----------->|              |
       |               |   |<-Lock OK-----|<-----------|              |
       |               |   |              |            |              |
       |               |   |--Batch-------|------------|------------->|
       |               |   |              |            | (Embedding + |
       |               |   |              |            |  MySQL +     |
       |               |   |              |            |  VDB Data)   |
       |               |   |<-Ready-------|<-----------|<-------------|
       |               |   |  (10s)       |            |              |
       |               |   |              |            |              |
       |               |   |--Release---->|----------->|              |
       |               |<--+ Release Local|            |              |
       |               |                  |            |              |
       |       (handle user query)        |            |              |
       |               |                  |            |              |
<---------Response-----|                  |            |              |
       |               |                  |            |              |

Meanwhile other instances during local lock:

[Load Balancer] [App Instances] [Local Memory] [VDB Locks] [Batch Processing Unit]
       |               |                |            |              |
----------Query------->|                |            |              |
       |               |--Check Count-->|----------->|              |
       |               |<-Empty VDB-----|<-----------|              |
       |               |                |            |              |
       |               |--Local Lock--->|            |              |
       |               |<-BLOCKED-------|            |              |
       |               |                |            |              |
<---------Not Ready----| (Request ignored during 5s lock)           |
       |               |                |            |              |

After lock expires (>5s later):

[Load Balancer] [App Instances] [Local Memory] [VDB Locks] [Batch Processing Unit]
       |               |                |            |              |
----------Query------->|                |            |              |
       |               |--Check Count--------------->|              |
       |               |<-Has Data-------------------|              |
       |               |                |            |              |
       |               |                |            |              |
       |               |--Use VDB---------------------------------->|
<---------Response--------------------------------------------------|
       |               |                |            |              |
```

### Lock Expiry and Error Recovery

**Local Lock (5 seconds)**:
- Prevents duplicate operations on same node
- Auto-clears to prevent local deadlocks
- Fast retry mechanism

**Remote Lock (5 minutes)**:
- Coordinates across application instances
- Auto-expires if node fails during batch processing
- Other nodes detect expiry and can acquire lock

**System Rate Limiting**:
- Local operations: No restrictions for individual records
- Batch operations: Single unified lock (5s local + 5min distributed) per namespace
- During batch lock: Both embedding AND VDB operations are blocked
- Individual records: Process normally even when batch locked (bypass embedding, direct VDB access)

## 5. Namespace Concept

Namespace groups data collection + lock collection together as logical unit:

```text
[Namespace Organization]

namespace:laptops
|-- collection: laptops_vectors (data)
+-- collection: laptops_locks (coordination)

namespace:reviews
|-- collection: reviews_vectors (data)
+-- collection: reviews_locks (coordination)

Each topic has paired (data + lock) collections for complete isolation
```
