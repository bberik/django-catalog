# 🛍️ Product Catalog App

A high-performance Django-based product catalog application with vector similarity search capabilities.

## 🌐 Live Demo
[View Live Demo](http://catalog-dev-alb-499800740.eu-north-1.elb.amazonaws.com/)

## ✨ Features

### Performance Optimizations
- **Database Query Optimization**
  - Strategic indexing on Product fields (title, description)
  - IVFFlat index for vector embeddings
  - Efficient caching for Categories and Tags
  - Smart pagination with Django's Lazy Querying
  - Optimized queries using Select Related

### Search Capabilities
- Vector similarity search for products
- Fast and accurate product matching
- Semantic search capabilities

### Admin Interface
- User-friendly product management
- Intuitive interface for adding/editing products
- Secure authentication system

#### Admin Access
- **URL**: [Admin Panel](http://catalog-dev-alb-499800740.eu-north-1.elb.amazonaws.com/admin)
- **Credentials**:
  - Username: `admin`
  - Password: `qpalzm`

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- PostgreSQL
- Virtual environment (recommended)

### Local Development Setup

1. **Environment Configuration**
   Create a `.env` file in the project root with the following variables:
   ```bash
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. **Setup Python Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements-dev.txt
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   python manage.py makemigrations
   python manage.py migrate
   
   # (Optional) Import sample data
   python manage.py import_json_data
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

## 🚀 Deployment

The application is currently deployed on AWS infrastructure:

### Infrastructure Components
- **Database**: AWS RDS (PostgreSQL)
- **Load Balancer**: AWS Application Load Balancer (ALB)
- **Container Service**: AWS Elastic Container Service (ECS)

### Deployment Steps

1. **Prerequisites**
   - Install AWS CLI
   - Install AWS CDK
   - Configure AWS credentials

2. **Deploy Infrastructure**
   ```bash
   # Deploy using CDK
   cdk deploy
   
   # Retrieve database credentials
   aws secretsmanager get-secret-value --secret-id catalog-dev-db-secret
   ```

## 📝 Notes
- The application is optimized for PostgreSQL with pgvector extension
- Caching system is implemented for Categories and Tags (TODO: Add cache invalidation on product updates)
- The system uses efficient pagination to handle large product catalogs

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

