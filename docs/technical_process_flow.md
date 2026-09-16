# WarehouseAI - Technical Process Flow Documentation

## Overview
WarehouseAI is an intelligent warehouse operations assistant that combines live WMS (Warehouse Management System) data with RAG (Retrieval-Augmented Generation) capabilities to provide comprehensive warehouse insights and operational support.

## System Architecture

### Component Structure
```
warehouseAI/
├── agents/              # AI agent implementations
│   ├── warehouse_agent.py      # Main agent with tool calling
│   ├── warehouse_chat.py       # Chat conversation management
│   └── shortage_graph.py       # LangGraph workflow for shortage investigation
├── ui/                  # User interface layer
│   ├── streamlit_app.py        # Streamlit chat interface
│   ├── app.py                 # CLI tool interface
│   └── core/                  # Core UI components
│       ├── rag/               # RAG implementation
│       │   ├── ingest.py      # Document ingestion pipeline
│       │   └── retrieve.py    # Knowledge retrieval
│       ├── database/          # Database connections
│       │   └── db.py          # PostgreSQL connection
│       └── tools/             # WMS tools (moved to src/)
├── src/                 # Core business logic
│   ├── wms_tools.py           # WMS database query functions
│   └── db.py                  # Database connection management
├── database/            # Database schemas and migrations
│   ├── 01_schema.sql          # Database schema
│   ├── 01_warehouse_master.sql # Master data
│   └── 02_seed_wms_data.sql   # Sample data
├── knowledge_base/     # RAG knowledge base
│   ├── raw/                   # Source documents
│   ├── processed/             # Processed chunks
│   └── vector_store/          # ChromaDB embeddings
├── tests/               # Test cases
├── docs/                # Documentation
└── .streamlit/          # Streamlit configuration
```

## Data Flow Architecture

### 1. User Query Processing Flow

```
User Input (Question)
    ↓
Streamlit/CLI Interface
    ↓
Warehouse Agent (OpenAI GPT-4o-mini)
    ↓
Tool Selection & Execution
    ├─→ WMS Database Tools (PostgreSQL)
    │   ├─→ Order Details
    │   ├─→ Order Allocation
    │   ├─→ Item Inventory
    │   ├─→ Inventory Overview
    │   └─→ Warehouse Movements
    ├─→ Knowledge Retrieval (ChromaDB)
    │   ├─→ Embed Query (OpenAI text-embedding-3-small)
    │   ├─→ Vector Search
    │   └─→ Context Retrieval
    └─→ Workflow Tools (LangGraph)
        └─→ Shortage Investigation
    ↓
Response Generation
    ↓
Formatted Output
```

### 2. RAG Ingestion Pipeline

```
Source Documents (PDF, Text, CSV, Excel, Images)
    ↓
File Processing
    ├─→ Text Files → Chunk extraction
    ├─→ PDF → Page extraction → Chunking
    ├─→ CSV/Excel → Table conversion → Text representation
    └─→ Images → Vision model → Caption generation
    ↓
Chunk Processing
    ├─→ Metadata enrichment (source, type, location)
    ├─→ Hash generation (deduplication)
    └─→ Record creation
    ↓
Embedding Generation (OpenAI text-embedding-3-small)
    ↓
Vector Storage (ChromaDB)
    ├─→ Document upsert
    ├─→ Metadata indexing
    └─→ Vector similarity indexing
    ↓
Processed Storage
    ├─→ chunks.json (human-readable)
    └─→ ingestion_report.json (processing stats)
```

### 3. Shortage Investigation Workflow (LangGraph)

```
Order Number Input
    ↓
Load Allocation Status
    ├─→ Query order_position_details
    ├─→ Query inventory_details
    └─→ Calculate shortages
    ↓
Extract Shortage Items
    ├─→ Filter items with shortage > 0
    └─→ Create shortage item list
    ↓
Conditional Check
    ├─→ No shortages → Complete with summary
    └─→ Has shortages → Continue investigation
    ↓
Inspect Shortage Items
    ├─→ Query item inventory for each shortage item
    ├─→ Get physical, allocated, blocked, available quantities
    └─→ Aggregate inventory data
    ↓
Fetch Recent Movements
    ├─→ Query movement_details for each item
    ├─→ Get last 5 movements per item
    └─→ Aggregate movement data
    ↓
Generate Summary
    ├─→ Combine allocation, inventory, movement data
    ├─→ Format operational summary
    └─→ Provide recommendations
    ↓
Return Investigation Results
```

## Technical Implementation Details

### Database Schema

#### Core Tables
- **order_position_details**: Order line items and allocations
  - `op_order_number`, `op_order_position`, `op_order_item`
  - `op_order_quantity`, `op_allocated_quantity`

- **inventory_details**: Current inventory positions
  - `iv_item_id`, `iv_physical_quantity`, `iv_allocated_quantity`
  - `iv_blocked_quantity`, `iv_available_quantity`

- **movement_details**: Warehouse movement history
  - `mo_movement_id`, `mo_movement_type`, `mo_movement_status`
  - `mo_movement_item`, `mo_movement_quantity`
  - Location fields (from/to areas, aisles, racks, bins)

### API Integration

#### OpenAI Integration
- **Model**: GPT-4o-mini for chat responses
- **Embeddings**: text-embedding-3-small for RAG
- **Vision**: gpt-5.4-mini for image captioning
- **Function Calling**: Structured tool execution

#### ChromaDB Integration
- **Collection**: warehouse_knowledge
- **Embedding Model**: OpenAI text-embedding-3-small
- **Storage**: PersistentClient with local SQLite backend
- **Chunk Size**: 1200 characters with 200 character overlap

### Tool Function Specifications

#### WMS Database Tools
```python
get_order_details(order_number: str) -> dict
get_order_allocation(order_number: str) -> dict
get_item_inventory(item_id: str) -> dict
get_inventory(limit: int) -> dict
get_movements(item_id: str, limit: int) -> dict
```

#### Knowledge Retrieval Tool
```python
retrieve_knowledge(query: str, n_results: int = 5) -> dict
```

#### Workflow Tool
```python
investigate_order_shortage(order_number: str) -> dict
```

## Configuration Management

### Environment Variables (.env)
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=warehouse_ai
DB_USER=warehouse_user
DB_PASSWORD=your_password

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini

# RAG
RAG_EMBEDDING_MODEL=text-embedding-3-small
RAG_VISION_MODEL=gpt-5.4-mini
```

### Streamlit Configuration (.streamlit/config.toml)
- Theme: Light mode with elegant blue (#0066CC) accents
- Font: Inter for UI, JetBrains Mono for code
- Layout: Wide layout for better data visualization
- Icons: Material Symbols for professional appearance

## Error Handling & Resilience

### Database Connection Failures
- Graceful error messages
- Safe tool call wrappers in agent
- Status indicators (NOT_FOUND, NO_MOVEMENTS, ERROR)

### RAG Retrieval Failures
- Empty result handling
- Fallback to direct LLM response
- Ingestion error reporting

### Workflow Resilience
- Individual step error handling
- Partial result completion
- Trace logging for debugging

## Performance Considerations

### Caching Strategy
- Database connection pooling
- Embedding batch processing (50 embeddings per batch)
- ChromaDB persistent storage
- Session state management in Streamlit

### Query Optimization
- Indexed database queries
- Efficient vector similarity search
- Limit-based result pagination
- Conditional workflow execution

## Security Considerations

### Data Protection
- Environment variable usage for credentials
- No hardcoded secrets in code
- .gitignore for sensitive files
- Read-only database operations

### API Security
- OpenAI API key management
- Rate limiting considerations
- Error message sanitization

## Deployment Considerations

### Development Environment
- Python 3.11+
- Virtual environment (.venv)
- Local PostgreSQL instance
- Streamlit development server

### Production Deployment
- Containerization (Docker recommended)
- Managed PostgreSQL service
- Streamlit Cloud or dedicated hosting
- Environment-specific configuration
- Monitoring and logging

## Monitoring & Maintenance

### Health Checks
- Database connectivity
- API service availability
- Vector store integrity
- Ingestion pipeline status

### Logging
- Tool execution traces
- Error tracking
- Performance metrics
- User interaction logs

## Extensibility Points

### Adding New WMS Tools
1. Implement function in `src/wms_tools.py`
2. Add tool definition in `agents/warehouse_agent.py`
3. Update routing in `call_wms_tool()`
4. Add to system instructions

### Adding Knowledge Sources
1. Add file type handler in `ui/core/rag/ingest.py`
2. Implement extraction logic
3. Add metadata enrichment
4. Test ingestion pipeline

### Adding New Workflows
1. Create LangGraph workflow in `agents/`
2. Define state schema
3. Implement node functions
4. Add tool definition to agent
5. Update routing logic

## Troubleshooting Guide

### Common Issues
1. **Import Errors**: Check Python path configuration
2. **Database Connection**: Verify .env configuration
3. **RAG Retrieval**: Check ChromaDB collection status
4. **Streamlit Performance**: Monitor session state size
5. **OpenAI API**: Verify API key and rate limits

### Debug Mode
Enable detailed logging by setting environment variables:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
export PYTHONUNBUFFERED=1
```

## Version Control Strategy

### Git Structure
- Main branch: Production-ready code
- Feature branches: New functionality
- Documentation: docs/ directory
- Configuration: .streamlit/ directory
- Ignored: .env, .venv/, __pycache__/

### Release Process
1. Update version numbers
2. Update CHANGELOG.md
3. Tag release
4. Deploy to production
5. Monitor for issues

## Future Enhancements

### Planned Features
- Multi-language support
- Advanced analytics dashboard
- Real-time notifications
- Mobile-responsive design
- Integration with external WMS systems
- Advanced visualization capabilities

### Technical Debt
- Migrate to async database operations
- Implement comprehensive testing suite
- Add API rate limiting
- Improve error recovery mechanisms
- Optimize vector search performance