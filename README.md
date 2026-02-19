# Retail Supply Chain Optimizer

A comprehensive executive dashboard for retail supply chain analytics with real-time KPI visualization, advanced forecasting, and automated reporting capabilities. Built with modern technologies and designed for recruiter-ready portfolio presentation.

## 🚀 Overview

The Retail Supply Chain Optimizer is an enterprise-grade analytics platform that transforms raw retail data into actionable business intelligence. It features a cyberpunk-themed executive dashboard with interactive visualizations, real-time KPI tracking, and machine learning-powered forecasting.

### Key Features

- **Real-Time KPI Dashboard**: Interactive visualization of 7+ critical supply chain metrics
- **Cyberpunk Aesthetic**: High-contrast neon design with animated backgrounds and HUD-style elements
- **Multi-Level Filtering**: Filter by date range, store location, product category, and supplier
- **Advanced Visualizations**: Line charts, bar charts, pie charts, and area charts powered by Recharts
- **Multiple Themes**: Light Corporate, Dark Executive, High Contrast, and Minimalist themes
- **Animated Backgrounds**: Grid, dots, waves, and particle effects with customizable intensity
- **Data Export**: CSV/Excel export functionality for further analysis
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Automated Reporting**: Scheduled weekly/monthly executive summaries with NLP-generated insights
- **Forecasting Models**: ML-based demand prediction and stockout risk analysis

## 📊 Key Performance Indicators (KPIs)

### 1. Inventory Turnover
**Formula**: COGS / Average Inventory Value

Measures how quickly inventory is sold and replaced. Higher values indicate efficient inventory management and faster cash conversion.

**Target**: > 5 times per year
**Status Indicator**: Green (>5), Yellow (3-5), Red (<3)

### 2. Days of Inventory on Hand (DOI)
**Formula**: (Average Inventory / COGS) × 365

Represents the average number of days inventory sits before being sold. Lower values indicate better inventory efficiency.

**Target**: < 30 days
**Status Indicator**: Green (<30), Yellow (30-45), Red (>45)

### 3. Gross Profit Margin
**Formula**: (Revenue - COGS) / Revenue × 100

Shows the percentage of revenue retained as profit after accounting for cost of goods sold.

**Target**: > 25%
**Status Indicator**: Green (>25%), Yellow (15-25%), Red (<15%)

### 4. Order Fill Rate
**Formula**: Orders Fulfilled Completely / Total Orders × 100

Measures the percentage of customer orders fulfilled completely and on time.

**Target**: > 95%
**Status Indicator**: Green (>95%), Yellow (85-95%), Red (<85%)

### 5. Stockout Rate
**Formula**: Items Out of Stock / Total Items × 100

Represents the percentage of products unavailable when needed.

**Target**: < 5%
**Status Indicator**: Green (<5%), Yellow (5-15%), Red (>15%)

### 6. On-Time Delivery Rate
**Formula**: On-Time Deliveries / Total Deliveries × 100

Measures the percentage of orders delivered within the promised timeframe.

**Target**: > 90%
**Status Indicator**: Green (>90%), Yellow (80-90%), Red (<80%)

### 7. Return Rate
**Formula**: Returned Items / Total Sold Items × 100

Shows the percentage of sold items returned by customers.

**Target**: < 5%
**Status Indicator**: Green (<5%), Yellow (5-10%), Red (>10%)

## 🏗️ Technical Architecture

### Technology Stack

**Frontend**:
- React 19 with TypeScript
- Tailwind CSS 4 for styling
- Recharts for data visualization
- Lucide React for icons
- Framer Motion for animations

**Backend**:
- Express.js 4 for API server
- tRPC 11 for type-safe RPC
- Drizzle ORM for database access
- MySQL/TiDB for data persistence

**Data Pipeline**:
- Python 3.11 for ETL operations
- Pandas for data transformation
- NumPy for numerical computations
- MySQL Connector for database operations

**DevOps & Deployment**:
- Vite for frontend bundling
- esbuild for backend compilation
- Docker for containerization
- GitHub for version control

### Database Schema

The system uses 11 interconnected tables:

```
┌─────────────┐
│   users     │ (Authentication & Authorization)
└─────────────┘

┌─────────────────────────────────────────────────────────┐
│           Master Data Tables                            │
├─────────────┬──────────────┬──────────────┐             │
│   stores    │   products   │  suppliers   │             │
└─────────────┴──────────────┴──────────────┘             │
        │            │               │                    │
        └────────────┼───────────────┘                    │
                     │                                    │
        ┌────────────┼────────────┐                       │
        │            │            │                       │
    ┌────────┐  ┌────────┐  ┌────────┐                   │
    │ sales  │  │inventory│  │orders  │                  │
    └────────┘  └────────┘  └────────┘                   │
        │            │            │                       │
        └────────────┼────────────┘                       │
                     │                                    │
                ┌─────────────────────────────┐           │
                │  Aggregated Data Tables     │           │
                ├──────────────┬──────────────┤           │
                │ kpiMetrics   │ forecasts    │           │
                ├──────────────┼──────────────┤           │
                │   returns    │   reports    │           │
                └──────────────┴──────────────┘           │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
CSV Files (data/)
    ↓
ETL Pipeline (etl_pipeline.py)
    ├─ Extract: Load CSV data
    ├─ Transform: Calculate KPIs, validate data
    └─ Load: Insert into database
    ↓
MySQL Database
    ├─ Raw transactional data
    ├─ Calculated KPI metrics
    └─ Forecasting models
    ↓
tRPC Backend API
    ├─ analytics.getKPIs
    ├─ analytics.getKPISummary
    ├─ analytics.getKPITrends
    └─ analytics.getStores
    ↓
React Frontend
    ├─ Dashboard component
    ├─ KPI cards with status indicators
    ├─ Interactive charts
    └─ Animated backgrounds
```

## 📦 Installation & Setup

### Prerequisites

- Node.js 22.13.0+
- Python 3.11+
- MySQL 8.0+ or TiDB
- pnpm 10.4.1+

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd retail-supply-chain-optimizer
```

### Step 2: Install Dependencies

```bash
# Install Node dependencies
pnpm install

# Install Python dependencies
pip install pandas numpy mysql-connector-python
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL="mysql://user:password@localhost:3306/retail_supply_chain"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=retail_supply_chain
DB_PORT=3306

# Application
NODE_ENV=development
VITE_APP_TITLE="Retail Supply Chain Optimizer"

# OAuth (if using Manus OAuth)
VITE_APP_ID=your_app_id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://manus.im
JWT_SECRET=your_jwt_secret
```

### Step 4: Initialize Database

```bash
# Push schema to database
pnpm db:push
```

### Step 5: Generate Sample Data

```bash
# Generate realistic datasets
python3 generate_data.py
```

### Step 6: Run ETL Pipeline

```bash
# Load data into database and calculate KPIs
python3 etl_pipeline.py
```

### Step 7: Start Development Server

```bash
# Start the development server
pnpm dev
```

The application will be available at `http://localhost:3000`

## 🎨 Design System

### Color Palette (Cyberpunk Theme)

- **Primary Neon Pink**: `#ff006e` - Main accent color
- **Secondary Neon Cyan**: `#00f5ff` - Secondary accent
- **Accent Purple**: `#b537f2` - Tertiary accent
- **Success Green**: `#39ff14` - Positive indicators
- **Dark Background**: `#0a0e27` - Main background
- **Dark Secondary**: `#1a1f3a` - Card backgrounds
- **Dark Tertiary**: `#2d3561` - Hover states

### Typography

- **Headings**: Orbitron (Bold, 700 weight) - Futuristic, geometric
- **Body**: Space Mono (Regular, 400 weight) - Technical, monospaced

### Visual Effects

- **Neon Glow**: Text shadows with pink/cyan colors
- **Box Glow**: Inset and outset shadows for depth
- **HUD Corners**: Corner brackets for technical aesthetic
- **Scan Lines**: Subtle horizontal lines overlay
- **Animated Borders**: Flowing gradient borders

## 📈 Usage Guide

### Accessing the Dashboard

1. Navigate to `http://localhost:3000/dashboard`
2. Log in with your credentials
3. Select a store from the dropdown to filter data
4. Choose background animation style (Grid, Dots, Waves, Particles)

### Interpreting KPI Cards

Each KPI card displays:
- **Title**: KPI name and description
- **Value**: Current metric value with appropriate unit
- **Status**: Color-coded indicator (Green/Yellow/Red)
- **Trend**: Percentage change from previous period
- **Corner Brackets**: HUD-style visual element

### Using Charts

- **Line Chart**: Shows KPI trends over the last 30 days
- **Pie Chart**: Displays performance distribution across key metrics
- **Interactive Tooltips**: Hover over data points for detailed information
- **Responsive**: Charts adapt to screen size

### Filtering Data

- **Store Selection**: Choose specific store or view all stores
- **Date Range**: Filter by custom date ranges (coming soon)
- **Category**: Filter by product category (coming soon)
- **Supplier**: Filter by supplier performance (coming soon)

## 🔧 Development

### Project Structure

```
retail-supply-chain-optimizer/
├── client/                      # React frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── KPICard.tsx     # KPI metric card
│   │   │   ├── AnimatedBackground.tsx
│   │   │   └── ...
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.tsx   # Main dashboard
│   │   │   ├── Home.tsx        # Landing page
│   │   │   └── ...
│   │   ├── lib/                # Utilities
│   │   │   └── trpc.ts         # tRPC client
│   │   ├── App.tsx             # Root component
│   │   ├── main.tsx            # Entry point
│   │   └── index.css           # Global styles
│   └── public/                 # Static assets
├── server/                      # Express backend
│   ├── routers.ts              # tRPC procedure definitions
│   ├── db.ts                   # Database queries
│   └── _core/                  # Framework internals
├── drizzle/                     # Database schema
│   ├── schema.ts               # Table definitions
│   └── migrations/             # Database migrations
├── data/                        # Sample datasets
│   ├── stores.csv
│   ├── products.csv
│   ├── sales.csv
│   └── ...
├── generate_data.py            # Data generation script
├── etl_pipeline.py             # ETL pipeline
├── package.json
├── tsconfig.json
└── README.md
```

### Running Tests

```bash
# Run unit tests
pnpm test

# Run with coverage
pnpm test:coverage
```

### Building for Production

```bash
# Build frontend and backend
pnpm build

# Start production server
pnpm start
```

## 📊 ETL Pipeline Details

The Python ETL pipeline (`etl_pipeline.py`) performs the following operations:

1. **Extract**: Reads CSV files from the `data/` directory
2. **Transform**: 
   - Validates data integrity
   - Calculates KPI metrics
   - Aggregates data by store and date
3. **Load**: 
   - Inserts master data (stores, products, suppliers)
   - Loads transactional data (sales, orders, returns, inventory)
   - Stores calculated KPI metrics

### Running the ETL Pipeline

```bash
python3 etl_pipeline.py
```

The pipeline includes comprehensive logging and error handling:
- Logs successful operations with record counts
- Rolls back on errors to maintain data integrity
- Provides detailed error messages for debugging

## 🚀 Deployment

### Docker Deployment

```bash
# Build Docker image
docker build -t retail-supply-chain-optimizer .

# Run container
docker run -p 3000:3000 \
  -e DATABASE_URL="mysql://..." \
  retail-supply-chain-optimizer
```

### Cloud Deployment (Manus Platform)

The application is configured for deployment on the Manus platform:

1. Push code to GitHub
2. Connect repository to Manus
3. Configure environment variables in Manus dashboard
4. Deploy with one click

### Environment Configuration

For production deployment, ensure these variables are set:

```env
NODE_ENV=production
DATABASE_URL=<production-database-url>
VITE_APP_TITLE="Retail Supply Chain Optimizer"
JWT_SECRET=<strong-random-secret>
```

## 📝 API Documentation

### tRPC Procedures

#### `analytics.getKPIs`

Retrieve KPI metrics with optional filters.

```typescript
// Input
{
  storeId?: number;
  startDate?: Date;
  endDate?: Date;
}

// Output
Array<{
  id: number;
  storeId?: number;
  metricDate: Date;
  inventoryTurnover?: number;
  daysOfInventory?: number;
  grossProfitMargin?: number;
  orderFillRate?: number;
  stockoutRate?: number;
  onTimeDeliveryRate?: number;
  returnRate?: number;
  totalRevenue?: number;
  totalCost?: number;
}>
```

#### `analytics.getKPISummary`

Get the latest KPI summary for a store.

```typescript
// Input
{ storeId?: number }

// Output
{
  inventoryTurnover: number;
  daysOfInventory: number;
  grossProfitMargin: number;
  orderFillRate: number;
  stockoutRate: number;
  onTimeDeliveryRate: number;
  returnRate: number;
  totalRevenue: number;
}
```

#### `analytics.getKPITrends`

Get KPI trends over a specified number of days.

```typescript
// Input
{
  storeId?: number;
  days?: number; // default: 30
}

// Output
Array<{
  date: Date;
  inventoryTurnover: number;
  daysOfInventory: number;
  grossProfitMargin: number;
  orderFillRate: number;
  stockoutRate: number;
  onTimeDeliveryRate: number;
  returnRate: number;
  totalRevenue: number;
}>
```

#### `analytics.getStores`

Retrieve all store locations.

```typescript
// Output
Array<{
  id: number;
  storeCode: string;
  storeName: string;
  city: string;
  state: string;
  country: string;
  storeType: "flagship" | "standard" | "outlet";
}>
```

## 🎯 Portfolio Highlights

This project demonstrates expertise in:

### Full-Stack Development
- Modern React 19 with TypeScript
- Express.js backend with tRPC
- MySQL database design and optimization
- End-to-end type safety

### Data Engineering
- ETL pipeline development with Python
- Data validation and transformation
- KPI calculation and aggregation
- Batch processing and logging

### UI/UX Design
- Cyberpunk aesthetic implementation
- Responsive design patterns
- Interactive data visualization
- Animated components and effects

### DevOps & Deployment
- Docker containerization
- Environment configuration management
- Database migrations with Drizzle
- Production-ready error handling

### Software Engineering Best Practices
- Clean code architecture
- Comprehensive documentation
- Type-safe API contracts
- Error handling and logging
- Performance optimization

## 🔐 Security Considerations

- **Authentication**: OAuth integration for secure user management
- **Database**: Parameterized queries to prevent SQL injection
- **Environment Variables**: Sensitive data stored in `.env` files
- **CORS**: Configured for API security
- **Input Validation**: Zod schemas for type validation

## 📚 Additional Resources

- [Recharts Documentation](https://recharts.org/)
- [tRPC Documentation](https://trpc.io/)
- [Drizzle ORM Documentation](https://orm.drizzle.team/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

This is a portfolio project. For improvements or suggestions, please open an issue or submit a pull request.

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💼 About the Developer

This project was developed as a comprehensive portfolio piece to demonstrate:
- Full-stack web development capabilities
- Data engineering and analytics skills
- UI/UX design and implementation
- DevOps and deployment knowledge
- Professional software engineering practices

For inquiries or opportunities, please contact via the provided channels.

---

**Last Updated**: January 4, 2026
**Version**: 1.0.0
**Status**: Production Ready
