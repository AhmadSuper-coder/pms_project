# Patient Management System API Documentation

## Overview

This is a scalable Django REST Framework API for managing patients, documents, and authentication in a Patient Management System (PMS).

## Features

- **Scalable Architecture**: Built using DRF ViewSets and routers for better organization
- **Authentication**: JWT-based authentication with OAuth support
- **Document Management**: Google Cloud Storage integration for file uploads
- **Advanced Filtering**: Search, pagination, and filtering capabilities
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation
- **Error Handling**: Custom exception handling with consistent error responses
- **Security**: CORS support and proper permissions

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token pair
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/accounts/oauth-login/` - OAuth login (Google, etc.)

### Patients
- `GET /api/patient/patients/` - List all patients (paginated)
- `POST /api/patient/patients/` - Create a new patient
- `GET /api/patient/patients/{id}/` - Get patient details
- `PATCH /api/patient/patients/{id}/` - Update patient
- `DELETE /api/patient/patients/{id}/` - Delete patient
- `GET /api/patient/patients/search/` - Advanced patient search
- `GET /api/patient/patients/{id}/summary/` - Get patient summary

### Documents
- `GET /api/document/documents/` - List all documents (paginated)
- `POST /api/document/documents/` - Create document record
- `GET /api/document/documents/{id}/` - Get document details
- `PATCH /api/document/documents/{id}/` - Update document
- `DELETE /api/document/documents/{id}/` - Delete document
- `GET /api/document/documents/{id}/download_url/` - Get signed download URL
- `GET /api/document/documents/by_patient/` - Get documents by patient
- `GET /api/document/documents/stats/` - Get document statistics

### Document Upload (GCS)
- `POST /api/document/sign-upload/` - Get signed upload URL
- `POST /api/document/confirm/` - Confirm upload completion

### OTP
- `POST /api/otp/generate/` - Generate OTP code
- `POST /api/otp/verify/` - Verify OTP code

## API Documentation

Access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **Schema**: `http://localhost:8000/api/schema/`

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirement.txt
   ```

2. **Environment Variables** (create `.env` file):
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/pms_db
   GCS_BUCKET_NAME=your-bucket-name
   GCS_CREDENTIALS_PATH=path/to/credentials.json
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

3. **Database Setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run Server**:
   ```bash
   python manage.py runserver
   ```

## Usage Examples

### Authentication

```python
import requests

# Get JWT token
response = requests.post('http://localhost:8000/api/auth/token/', {
    'username': 'your-username',
    'password': 'your-password'
})
token = response.json()['access']

# Use token in headers
headers = {'Authorization': f'Bearer {token}'}
```

### Patient Management

```python
# List patients with filtering
response = requests.get('http://localhost:8000/api/patient/patients/', 
                       params={'search': 'john', 'ordering': 'full_name'},
                       headers=headers)

# Create patient
patient_data = {
    'full_name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+1234567890',
    'age': 30,
    'gender': 'M'
}
response = requests.post('http://localhost:8000/api/patient/patients/', 
                        json=patient_data, headers=headers)
```

### Document Upload

```python
# Step 1: Get signed upload URL
upload_data = {
    'filename': 'document.pdf',
    'content_type': 'application/pdf',
    'size_bytes': 1024000,
    'patient_id': 1,
    'document_type': 'medical_report'
}
response = requests.post('http://localhost:8000/api/document/sign-upload/', 
                        json=upload_data, headers=headers)
upload_info = response.json()

# Step 2: Upload file to GCS
files = {'file': open('document.pdf', 'rb')}
upload_response = requests.put(upload_info['upload_url'], 
                              files=files,
                              headers={'Content-Type': 'application/pdf'})

# Step 3: Confirm upload
confirm_data = {'document_id': upload_info['document_id']}
requests.post('http://localhost:8000/api/document/confirm/', 
             json=confirm_data, headers=headers)
```

## Advanced Features

### Filtering and Search

The API supports advanced filtering and search:

```python
# Search patients
GET /api/patient/patients/?search=john&age_min=18&age_max=65&gender=M

# Filter documents
GET /api/document/documents/?patient=1&document_type=medical_report&is_uploaded=true

# Ordering
GET /api/patient/patients/?ordering=-created_at
```

### Pagination

All list endpoints support pagination:

```python
# Page 1 (default)
GET /api/patient/patients/

# Specific page
GET /api/patient/patients/?page=2

# Custom page size
GET /api/patient/patients/?page_size=50
```

### Custom Actions

ViewSets include custom actions for specific functionality:

```python
# Patient search with advanced filters
GET /api/patient/patients/search/?q=john&age_min=18&gender=M

# Patient summary
GET /api/patient/patients/1/summary/

# Document statistics
GET /api/document/documents/stats/

# Download URL for document
GET /api/document/documents/1/download_url/
```

## Error Handling

The API provides consistent error responses:

```json
{
    "error": {
        "status_code": 400,
        "message": "Bad request - Invalid input data",
        "details": {
            "field_name": ["This field is required."]
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

## Security

- JWT-based authentication
- CORS configuration for frontend integration
- Proper permission classes
- Input validation and sanitization
- Secure file upload handling

## Scalability Features

1. **ViewSets**: Organized, reusable view logic
2. **Routers**: Automatic URL generation
3. **Filtering**: Built-in search and filter capabilities
4. **Pagination**: Efficient data loading
5. **Custom Actions**: Extensible functionality
6. **Proper Serializers**: Data validation and transformation
7. **Exception Handling**: Consistent error responses
8. **API Documentation**: Auto-generated and maintainable docs

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy .
```

### Database Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

## Production Deployment

1. Set `DEBUG=False` in production
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email backend
5. Set up Google Cloud Storage credentials
6. Use environment variables for sensitive data
7. Enable HTTPS
8. Set up monitoring and logging

## Contributing

1. Follow PEP 8 style guidelines
2. Write tests for new features
3. Update documentation
4. Use meaningful commit messages
5. Create pull requests for changes
