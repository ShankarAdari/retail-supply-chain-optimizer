# Technical Architecture

## System Overview

The Retail Supply Chain Optimizer is a modern full-stack application designed to provide real-time analytics and insights for retail supply chain management. The system follows a three-tier architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer (React)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Dashboard Component                                 │  │
│  │  ├─ KPI Cards (7 metrics)                           │  │
│  │  ├─ Interactive Charts (Line, Pie, Bar)             │  │
│  │  ├─ Animated Background (4 variants)                │  │
│  │  └─ Filter Controls                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ tRPC                             │
├─────────────────────────────────────────────────────────────┤
│                    API Layer (Express)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  tRPC Routers                                        │  │
│  │  ├─ analytics.getKPIs()                             │  │
│  │  ├─ analytics.getKPISummary()                       │  │
│  │  ├─ analytics.getKPITrends()                        │  │
│  │  ├─ analytics.getStores()                           │  │
│  │  ├─ analytics.getProducts()                         │  │
│  │  └─ auth.* (Authentication)                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ SQL                              │
├─────────────────────────────────────────────────────────────┤
│                  Data Layer (Drizzle ORM)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Database Queries                                    │  │
│  │  ├─ getKPIMetrics()                                 │  │
│  │  ├─ getAllStores()                                  │  │
│  │  ├─ getSalesByDateRange()                           │  │
│  │  ├─ getInventoryByStore()                           │  │
│  │  └─ getOrdersByStatus()                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓ MySQL                            │
├─────────────────────────────────────────────────────────────┤
│                  Database Layer (MySQL)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  11 Interconnected Tables                            │  │
│  │  ├─ Master Data: stores, products, suppliers        │  │
│  │  ├─ Transactional: sales, orders, returns           │  │
│  │  ├─ Operational: inventory                           │  │
│  │  ├─ Aggregated: kpiMetrics, forecasts               │  │
│  │  └─ Reporting: reports                              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↑                                          ↓
    ETL Pipeline (Python)                   Data Ingestion
         ↓                                          ↑
    CSV Files (data/)                    Batch Processing
```

## Component Architecture

### Frontend Components

**Dashboard.tsx** (Main Component)
- Orchestrates all dashboard functionality
- Manages state for filters and background variants
- Integrates with tRPC for data fetching
- Renders KPI cards and charts

**KPICard.tsx** (Reusable Component)
- Displays individual KPI metrics
- Shows status indicators (good/warning/critical)
- Displays trend information
- Supports multiple formats (percentage, currency, number)

**AnimatedBackground.tsx** (Visual Component)
- Canvas-based animations
- 4 animation variants (grid, dots, waves, particles)
- Responsive to window resizing
- Configurable intensity levels

### Backend Components

**routers.ts** (API Definitions)
- Defines tRPC procedures
- Implements input validation with Zod
- Handles error responses
- Manages authentication context

**db.ts** (Data Access Layer)
- Query helper functions
- Database connection management
- Error handling and logging
- Type-safe database operations

**schema.ts** (Data Model)
- Drizzle ORM table definitions
- Type-safe schema with TypeScript inference
- Relationships between tables
- Default values and constraints

## Data Flow

### Request Flow

```
User Action (Filter/Load)
         ↓
React Component State Update
         ↓
tRPC Hook Call (trpc.analytics.getKPIs.useQuery())
         ↓
Express Server Receives Request
         ↓
tRPC Router Validates Input (Zod)
         ↓
Database Query Helper (db.ts)
         ↓
Drizzle ORM Builds SQL Query
         ↓
MySQL Executes Query
         ↓
Results Returned to Component
         ↓
Component Re-renders with New Data
         ↓
Charts Update and Animate
```

### ETL Data Flow

```
CSV Files (data/)
    ↓
generate_data.py (Data Generation)
    ├─ Creates realistic datasets
    ├─ Generates relationships
    └─ Exports to CSV
    ↓
etl_pipeline.py (Data Processing)
    ├─ Extract: Read CSV files
    ├─ Transform: Calculate KPIs
    ├─ Validate: Check data integrity
    └─ Load: Insert into database
    ↓
MySQL Database
    ├─ Raw transactional data
    ├─ Calculated KPI metrics
    └─ Aggregated summaries
    ↓
tRPC API Queries
    ├─ Fetch KPI metrics
    ├─ Filter by store/date
    └─ Calculate trends
    ↓
React Dashboard
    ├─ Display KPI cards
    ├─ Render charts
    └─ Show trends
```

## Database Schema

### Master Data Tables

**stores**
- Primary key: id
- Fields: storeCode, storeName, city, state, country, storeType
- Purpose: Store location and metadata
- Relationships: Referenced by sales, inventory, orders

**products**
- Primary key: id
- Fields: productCode, productName, category, unitCost, unitPrice
- Purpose: Product catalog
- Relationships: Referenced by sales, inventory, orders

**suppliers**
- Primary key: id
- Fields: supplierCode, supplierName, city, country, contactEmail
- Purpose: Supplier information
- Relationships: Referenced by orders

### Transactional Tables

**sales**
- Primary key: id
- Fields: storeId, productId, saleDate, quantity, salePrice, totalRevenue
- Purpose: Record sales transactions
- Relationships: Foreign keys to stores, products

**orders**
- Primary key: id
- Fields: supplierId, storeId, orderDate, orderStatus, expectedDeliveryDate, actualDeliveryDate
- Purpose: Track purchase orders
- Relationships: Foreign keys to suppliers, stores

**returns**
- Primary key: id
- Fields: saleId, returnDate, quantity, reason, refundAmount
- Purpose: Track product returns
- Relationships: Foreign key to sales

### Operational Tables

**inventory**
- Primary key: id
- Fields: storeId, productId, quantity, reorderPoint, lastUpdated
- Purpose: Track inventory levels
- Relationships: Foreign keys to stores, products

### Aggregated Tables

**kpiMetrics**
- Primary key: id
- Fields: storeId, metricDate, inventoryTurnover, daysOfInventory, grossProfitMargin, orderFillRate, stockoutRate, onTimeDeliveryRate, returnRate, totalRevenue, totalCost
- Purpose: Store calculated KPI values
- Relationships: Foreign key to stores

**forecasts**
- Primary key: id
- Fields: storeId, productId, forecastDate, predictedDemand, confidence, forecastMethod
- Purpose: Store ML-generated forecasts
- Relationships: Foreign keys to stores, products

**reports**
- Primary key: id
- Fields: reportType, generatedDate, content, recipientEmail, status
- Purpose: Store generated reports
- Relationships: None (standalone)

## API Endpoints (tRPC Procedures)

### Analytics Router

**analytics.getKPIs**
- Input: { storeId?: number, startDate?: Date, endDate?: Date }
- Output: Array of KPI metric records
- Purpose: Retrieve raw KPI data with optional filters
- Performance: O(n) where n = number of records in date range

**analytics.getKPISummary**
- Input: { storeId?: number }
- Output: Latest KPI summary object
- Purpose: Get current KPI values for dashboard display
- Performance: O(1) - returns latest record

**analytics.getKPITrends**
- Input: { storeId?: number, days?: number }
- Output: Array of KPI records with dates
- Purpose: Show KPI trends over time
- Performance: O(n) where n = number of days

**analytics.getStores**
- Input: None
- Output: Array of store records
- Purpose: Populate store filter dropdown
- Performance: O(n) where n = number of stores

**analytics.getProducts**
- Input: None
- Output: Array of product records
- Purpose: Populate product filter dropdown
- Performance: O(n) where n = number of products

**analytics.getSalesData**
- Input: { startDate: Date, endDate: Date, storeId?: number }
- Output: Array of sales records
- Purpose: Fetch sales data for analysis
- Performance: O(n) where n = sales in date range

**analytics.getInventory**
- Input: { storeId: number }
- Output: Array of inventory records
- Purpose: Get inventory levels for specific store
- Performance: O(n) where n = products in store

## Performance Considerations

### Database Optimization

1. **Indexing Strategy**
   - Primary keys on all tables
   - Foreign key indexes for joins
   - Composite indexes on frequently filtered columns
   - Date indexes for range queries

2. **Query Optimization**
   - Use WHERE clauses to filter early
   - Aggregate data at database level
   - Use appropriate JOIN types
   - Avoid N+1 query problems

3. **Caching Strategy**
   - tRPC query caching
   - React Query cache management
   - Browser cache for static assets
   - Consider Redis for high-traffic scenarios

### Frontend Optimization

1. **Component Rendering**
   - Memoization of expensive components
   - Lazy loading of charts
   - Virtual scrolling for large lists
   - Code splitting for routes

2. **Data Fetching**
   - Request batching
   - Pagination for large datasets
   - Incremental loading
   - Optimistic updates

3. **Asset Optimization**
   - Minified CSS and JavaScript
   - Image optimization
   - Font subsetting
   - Gzip compression

## Security Architecture

### Authentication & Authorization

- OAuth integration for user authentication
- Session-based authorization
- Role-based access control (admin/user)
- Protected procedures with `protectedProcedure`

### Data Security

- Parameterized queries to prevent SQL injection
- Input validation with Zod schemas
- HTTPS for all communications
- Environment variables for sensitive data

### Error Handling

- Comprehensive try-catch blocks
- Meaningful error messages
- Error logging for debugging
- User-friendly error displays

## Scalability Considerations

### Horizontal Scaling

- Stateless API servers (can run multiple instances)
- Load balancer for distributing requests
- Database replication for read scaling
- Cache layer for reducing database load

### Vertical Scaling

- Database query optimization
- Connection pooling
- Memory-efficient data structures
- Async/await for non-blocking operations

### Future Enhancements

- Microservices architecture
- Message queues for async processing
- Event-driven architecture
- CQRS pattern for complex queries

## Deployment Architecture

### Development Environment

```
Local Machine
├─ Node.js development server (Vite)
├─ Express API server
├─ MySQL database
└─ Python ETL scripts
```

### Production Environment

```
Cloud Platform (Manus/AWS/GCP)
├─ Frontend (Static hosting)
├─ Backend (Container/Serverless)
├─ Database (Managed MySQL)
└─ ETL (Scheduled jobs)
```

### Docker Deployment

```dockerfile
FROM node:22
WORKDIR /app
COPY package*.json ./
RUN pnpm install
COPY . .
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "start"]
```

## Monitoring & Observability

### Logging

- Server-side request logging
- Database query logging
- Error tracking and reporting
- Performance metrics collection

### Metrics

- API response times
- Database query performance
- Error rates
- User engagement metrics

### Alerting

- Threshold-based alerts
- Error rate monitoring
- Performance degradation alerts
- Availability monitoring

---

**Last Updated**: January 4, 2026
**Version**: 1.0.0
