# WarehouseAI - Architecture Diagrams

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐           ┌─────────────────┐                 │
│  │  Streamlit Web  │           │   CLI Tools     │                 │
│  │    Interface    │           │   (app.py)      │                 │
│  │  (streamlit_    │           │                 │                 │
│  │   app.py)       │           │                 │                 │
│  └────────┬────────┘           └────────┬────────┘                 │
│           │                             │                            │
│           └────────────┬────────────────┘                            │
│                        │                                             │
├────────────────────────┼─────────────────────────────────────────────┤
│                        │              AGENT LAYER                      │
│                        ├─────────────────────────────────────────────┤
│                        │                                             │
│           ┌────────────▼────────────┐                               │
│           │   Warehouse Agent       │                               │
│           │  (warehouse_agent.py)   │                               │
│           │                         │                               │
│           │  • Tool Selection       │                               │
│           │  • Function Calling     │                               │
│           │  • Response Generation  │                               │
│           └────────────┬────────────┘                               │
│                        │                                             │
│           ┌────────────▼────────────┐                               │
│           │   Warehouse Chat        │                               │
│           │  (warehouse_chat.py)    │                               │
│           │                         │                               │
│           │  • Conversation Mgmt    │                               │
│           │  • Context Tracking     │                               │
│           │  • Tool Trace Display   │                               │
│           └────────────┬────────────┘                               │
│                        │                                             │
│           ┌────────────▼────────────┐                               │
│           │  Shortage Investigation │                               │
│           │    (shortage_graph.py)  │                               │
│           │                         │                               │
│           │  • LangGraph Workflow   │                               │
│           │  • Multi-step Analysis  │                               │
│           │  • Automated Tracing    │                               │
│           └────────────┬────────────┘                               │
├────────────────────────┼─────────────────────────────────────────────┤
│                        │            CORE SERVICES LAYER              │
│                        ├─────────────────────────────────────────────┤
│                        │                                             │
│    ┌───────────────────▼─────────────────┐                          │
│    │           WMS Tools                 │                          │
│    │        (src/wms_tools.py)          │                          │
│    │                                    │                          │
│    │  • get_order_details              │                          │
│    │  • get_order_allocation           │                          │
│    │  • get_item_inventory             │                          │
│    │  • get_inventory                  │                          │
│    │  • get_movements                  │                          │
│    └────────────┬──────────────────────┘                          │
│                 │                                                   │
│    ┌────────────▼──────────────────────┐                          │
│    │         Database Connection        │                          │
│    │           (src/db.py)             │                          │
│    │                                    │                          │
│    │  • PostgreSQL Connection Pool     │                          │
│    │  • Query Execution                │                          │
│    │  • Error Handling                 │                          │
│    └────────────┬──────────────────────┘                          │
│                 │                                                   │
│    ┌────────────▼──────────────────────┐                          │
│    │         RAG Services              │                          │
│    │    (ui/core/rag/)                 │                          │
│    │                                    │                          │
│    │  • ingest.py (Document Pipeline)  │                          │
│    │  • retrieve.py (Knowledge Search) │                          │
│    └────────────┬──────────────────────┘                          │
├────────────────────────┼─────────────────────────────────────────────┤
│                        │            DATA LAYER                       │
│                        ├─────────────────────────────────────────────┤
│                        │                                             │
│    ┌───────────────────▼─────────────────┐                          │
│    │         PostgreSQL Database         │                          │
│    │                                    │                          │
│    │  • order_position_details          │                          │
│    │  • inventory_details               │                          │
│    │  • movement_details               │                          │
│    └────────────────────────────────────┘                          │
│                                                                      │
│    ┌───────────────────▼─────────────────┐                          │
│    │         ChromaDB Vector Store       │                          │
│    │                                    │                          │
│    │  • warehouse_knowledge collection  │                          │
│    │  • Document embeddings             │                          │
│    │  • Metadata indexing              │                          │
│    └────────────────────────────────────┘                          │
│                                                                      │
│    ┌───────────────────▼─────────────────┐                          │
│    │         Knowledge Base Files        │                          │
│    │                                    │                          │
│    │  • raw/ (Source documents)          │                          │
│    │  • processed/ (Chunks)             │                          │
│    │  • vector_store/ (ChromaDB)        │                          │
│    └────────────────────────────────────┘                          │
├────────────────────────┼─────────────────────────────────────────────┤
│                        │          EXTERNAL SERVICES                   │
│                        ├─────────────────────────────────────────────┤
│                        │                                             │
│    ┌───────────────────▼─────────────────┐                          │
│    │         OpenAI API                  │                          │
│    │                                    │                          │
│    │  • GPT-4o-mini (Chat)              │                          │
│    │  • text-embedding-3-small (RAG)    │                          │
│    │  • gpt-5.4-mini (Vision)           │                          │
│    └────────────────────────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### User Query Processing Flow

```
┌──────────────┐
│   User Input │
│  (Question)  │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Streamlit/CLI    │
│   Interface      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Warehouse Agent   │
│  (OpenAI GPT)     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Tool Selection   │
│  & Routing       │
└──────┬───────────┘
       │
       ├─────────────────┬─────────────────┬──────────────────┐
       │                 │                 │                  │
       ▼                 ▼                 ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   WMS Tools  │  │  RAG Search  │  │  Workflow    │  │  Direct AI   │
│              │  │              │  │  Tools       │  │  Response    │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       ▼                 ▼                 ▼                 │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ PostgreSQL    │  │  ChromaDB    │  │  LangGraph    │          │
│  Database     │  │  Vector Store│  │  Workflow     │          │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Response Format │
                    │  & Display      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  User Output     │
                    │  (Answer)        │
                    └──────────────────┘
```

### RAG Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  Source Documents                            │
│  PDFs | Text Files | CSV | Excel | Images                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  File Processing                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │   Text   │  │   PDF    │  │  Tables  │  │  Images  │    │
│  │  Files   │  │Extractor │  │ Processor│  │  Vision  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │              │          │
│       └──────────────┴──────────────┴──────────────┘          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Chunk Processing                              │
├─────────────────────────────────────────────────────────────┤
│  • Text chunking (1200 chars, 200 overlap)                   │
│  • Metadata enrichment (source, type, location)             │
│  • Hash generation (deduplication)                           │
│  • Record creation                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Embedding Generation                            │
├─────────────────────────────────────────────────────────────┤
│  OpenAI text-embedding-3-small                               │
│  Batch processing (50 embeddings per batch)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Vector Storage (ChromaDB)                      │
├─────────────────────────────────────────────────────────────┤
│  • Document upsert                                           │
│  • Metadata indexing                                        │
│  • Vector similarity indexing                               │
│  • Persistent storage (SQLite)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Processed Storage                              │
├─────────────────────────────────────────────────────────────┤
│  • chunks.json (human-readable chunks)                       │
│  • ingestion_report.json (processing statistics)             │
└─────────────────────────────────────────────────────────────┘
```

### Shortage Investigation Workflow (LangGraph)

```
┌──────────────────┐
│  Order Number    │
│     Input        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Load Allocation  │
│      Status      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Extract Shortage │
│     Items        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Has Shortages?  │
└──────┬───────────┘
       │
    ┌──┴──┐
    │ Yes │ No
    ▼     ▼
┌─────────┐ ┌─────────┐
│Inspect  │ │Complete │
│Shortage │ │Summary  │
│ Items   │ └─────────┘
└────┬────┘
     │
     ▼
┌──────────────────┐
│  Fetch Recent    │
│   Movements      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Generate        │
│    Summary       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Return Results  │
└──────────────────┘
```

## Component Interaction Diagram

### Tool Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      User Question                           │
│              "Why is order ORD10004 partially allocated?"   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  OpenAI GPT-4o-mini                           │
│              (Function Calling Decision)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              get_order_allocation("ORD10004")                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Query                             │
│              (order_position_details,                         │
│               inventory_details)                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Allocation Status Data                           │
│              {status: "PARTIAL", items: [...]}                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              investigate_order_shortage("ORD10004")           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Workflow                            │
│              (Multi-step Investigation)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│Inventory │    │Movements │    │Analysis  │
│  Check   │    │  Check   │    │ Summary  │
└────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │
     └───────────────┴───────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Comprehensive Investigation Report                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              AI-Generated Response                            │
│              (Formatted with context and recommendations)      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              User Display (Streamlit)                         │
└─────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Security Layers                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Application Security                                  │   │
│  │  • Input validation                                   │   │
│  │  • SQL injection prevention                           │   │
│  │  • XSS protection                                     │   │
│  │  • CSRF protection                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Authentication & Authorization                        │   │
│  │  • Environment variable secrets                        │   │
│  │  • API key management                                 │   │
│  │  • Role-based access control                          │   │
│  │  • Session management                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Data Security                                         │   │
│  │  • Encrypted database connections                      │   │
│  │  • Secure API communications                           │   │
│  │  • Data at rest encryption                             │   │
│  │  • Audit logging                                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Network Security                                      │   │
│  │  • TLS/SSL encryption                                 │   │
│  │  • Firewall rules                                     │   │
│  │  • Network segmentation                                │   │
│  │  • DDoS protection                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│              Development Workstation                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Python 3.11+ Environment                            │   │
│  │  • Virtual Environment (.venv)                        │   │
│  │  • Local PostgreSQL Instance                          │   │
│  │  • Streamlit Development Server                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Development Tools                                    │   │
│  │  • Git for version control                            │   │
│  │  • IDE (VS Code, PyCharm)                            │   │
│  │  • Testing frameworks                                │   │
│  │  • Debugging tools                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                   Production Infrastructure                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Application Layer                                     │   │
│  │  • Streamlit Cloud / Kubernetes                       │   │
│  │  • Load balancing                                     │   │
│  │  • Auto-scaling                                       │   │
│  │  • Health monitoring                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Layer                                       │   │
│  │  • Managed PostgreSQL (AWS RDS, Cloud SQL)           │   │
│  │  • Read replicas                                      │   │
│  │  • Automated backups                                  │   │
│  │  • High availability                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vector Store Layer                                   │   │
│  │  • ChromaDB with persistent storage                    │   │
│  │  • Backup and recovery                               │   │
│  │  • Performance optimization                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  External Services                                    │   │
│  │  • OpenAI API (with rate limiting)                    │   │
│  │  • CDN for static assets                              │   │
│  │  • Monitoring and logging services                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Performance Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Performance Optimization                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Caching Strategy                                      │   │
│  │  • Database connection pooling                        │   │
│  │  • Embedding result caching                            │   │
│  │  • Session state management                            │   │
│  │  • API response caching                                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Query Optimization                                   │   │
│  │  • Indexed database queries                           │   │
│  │  • Efficient vector similarity search                  │   │
│  │  • Batch processing for embeddings                     │   │
│  │  • Result pagination                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Asynchronous Processing                               │   │
│  │  • Parallel tool execution                            │   │
│  │  • Background job processing                          │   │
│  │  • Streaming responses                                │   │
│  │  • Non-blocking I/O                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│              Monitoring & Logging Architecture                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Application Monitoring                               │   │
│  │  • Performance metrics (response time, throughput)    │   │
│  │  • Error tracking and alerting                        │   │
│  │  • User activity logging                              │   │
│  │  • Tool execution traces                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Database Monitoring                                  │   │
│  │  • Query performance                                 │   │
│  │  • Connection pool status                            │   │
│  │  • Storage utilization                               │   │
│  │  • Backup status                                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  System Monitoring                                    │   │
│  │  • CPU and memory usage                               │   │
│  │  • Network traffic                                    │   │
│  │  • Disk I/O                                          │   │
│  │  • Service health checks                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                  External System Integration                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WMS Integration                                      │   │
│  │  • PostgreSQL direct connection                       │   │
│  │  • REST API endpoints (future)                        │   │
│  │  • Webhook support (future)                           │   │
│  │  • Custom connector development                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Document Management                                  │   │
│  │  • File system integration                            │   │
│  │  • Cloud storage (S3, Azure Blob)                     │   │
│  │  • API-based document ingestion                        │   │
│  │  • Automated document updates                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Authentication & Identity                            │   │
│  │  • LDAP/Active Directory integration                  │   │
│  │  • OAuth 2.0 / SAML support                           │   │
│  │  • Custom authentication providers                     │   │
│  │  • Single sign-on (SSO)                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Scalability Strategy                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Horizontal Scaling                                   │   │
│  │  • Stateless application design                       │   │
│  │  • Container orchestration (Kubernetes)               │   │
│  │  • Auto-scaling based on load                         │   │
│  │  • Geographic distribution                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Vertical Scaling                                     │   │
│  │  • Database read replicas                            │   │
│  │  • Vector store sharding                             │   │
│  │  • Caching layer scaling                             │   │
│  │  • Resource optimization                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Data Partitioning                                    │   │
│  │  • Time-based data archiving                         │   │
│  │  • Geographic data distribution                      │   │
│  │  • Customer-specific data isolation                  │   │
│  │  • Hot/cold data storage                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack Summary

```
┌─────────────────────────────────────────────────────────────┐
│                   Technology Stack                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend:        Streamlit, HTML/CSS/JavaScript            │
│  Backend:         Python 3.11+, FastAPI (future)            │
│  Database:        PostgreSQL 14+                             │
│  Vector Store:    ChromaDB (SQLite backend)                 │
│  AI Engine:       OpenAI GPT-4o-mini, text-embedding-3-small│
│  Workflow:        LangGraph, LangChain                       │
│  Deployment:      Docker, Kubernetes (future)                 │
│  Monitoring:      Prometheus, Grafana (future)               │
│  Logging:         Structured logging, ELK stack (future)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## File Structure Reference

```
warehouseAI/
├── agents/                          # AI Agent Layer
│   ├── warehouse_agent.py          # Main agent with tool calling
│   ├── warehouse_chat.py           # Chat conversation management
│   └── shortage_graph.py          # LangGraph shortage investigation
├── ui/                             # User Interface Layer
│   ├── streamlit_app.py            # Streamlit web interface
│   ├── app.py                      # CLI tool interface
│   └── core/                       # Core Components
│       ├── rag/                    # RAG Implementation
│       │   ├── ingest.py           # Document ingestion pipeline
│       │   └── retrieve.py         # Knowledge retrieval
│       ├── database/               # Database Layer
│       │   └── db.py               # PostgreSQL connection
│       └── tools/                  # WMS Tools (referenced from src/)
├── src/                            # Core Business Logic
│   ├── wms_tools.py                # WMS database query functions
│   └── db.py                       # Database connection management
├── database/                       # Database Schemas
│   ├── 01_schema.sql              # Database schema
│   ├── 01_warehouse_master.sql    # Master data
│   └── 02_seed_wms_data.sql      # Sample data
├── knowledge_base/                 # RAG Knowledge Base
│   ├── raw/                       # Source documents
│   ├── processed/                 # Processed chunks
│   └── vector_store/              # ChromaDB embeddings
├── tests/                          # Test Cases
├── docs/                           # Documentation
│   ├── technical_process_flow.md  # Technical documentation
│   ├── presentation_flow.md        # Presentation flow
│   └── architecture_diagrams.md   # This file
├── .streamlit/                     # Streamlit Configuration
│   └── config.toml                # Theme and settings
├── .env                            # Environment variables
├── requirements.txt                 # Python dependencies
└── README.md                       # Project overview
```