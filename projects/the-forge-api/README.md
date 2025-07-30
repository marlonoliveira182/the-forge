# The Forge API

A web API version of The Forge v8 application for schema transformation and mapping operations. This API provides the same functionality as the desktop application but accessible via HTTP endpoints.

## Features

- **Schema Mapping**: Create field mappings between different schema formats (JSON Schema, XSD)
- **Schema to Excel**: Convert schemas to Excel format for analysis
- **XSD to JSON Schema**: Convert XSD schemas to JSON Schema format
- **JSON Schema to XSD**: Convert JSON Schema to XSD format

## API Endpoints

### Base URL
```
https://your-render-app.onrender.com
```

### Endpoints

#### 1. Health Check
- **GET** `/api/health`
- Returns API status and version

#### 2. Schema Mapping
- **POST** `/api/mapping`
- **Parameters:**
  - `source_file`: Source schema file (JSON, XSD, XML)
  - `target_file`: Target schema file (JSON, XSD, XML)
  - `threshold`: Similarity threshold (default: 0.7)
  - `keep_case`: Keep original case (default: false)
- **Returns:** Excel file with field mapping

#### 3. Schema to Excel
- **POST** `/api/schema-to-excel`
- **Parameters:**
  - `schema_file`: Schema file (JSON, XSD, XML)
  - `keep_case`: Keep original case (default: false)
- **Returns:** Excel file with schema structure

#### 4. XSD to JSON Schema
- **POST** `/api/xsd-to-jsonschema`
- **Parameters:**
  - `xsd_file`: XSD file
  - `keep_case`: Keep original case (default: false)
- **Returns:** JSON Schema file

#### 5. JSON Schema to XSD
- **POST** `/api/jsonschema-to-xsd`
- **Parameters:**
  - `json_schema_file`: JSON Schema file
- **Returns:** XSD file

## Usage Examples

### Using curl

#### Schema Mapping
```bash
curl -X POST "https://your-render-app.onrender.com/api/mapping" \
  -F "source_file=@source.json" \
  -F "target_file=@target.xsd" \
  -F "threshold=0.8" \
  -F "keep_case=false" \
  --output mapping.xlsx
```

#### Schema to Excel
```bash
curl -X POST "https://your-render-app.onrender.com/api/schema-to-excel" \
  -F "schema_file=@schema.json" \
  --output schema.xlsx
```

#### XSD to JSON Schema
```bash
curl -X POST "https://your-render-app.onrender.com/api/xsd-to-jsonschema" \
  -F "xsd_file=@schema.xsd" \
  --output schema.json
```

### Using JavaScript/Fetch

```javascript
// Schema Mapping
const formData = new FormData();
formData.append('source_file', sourceFile);
formData.append('target_file', targetFile);
formData.append('threshold', '0.8');

const response = await fetch('https://your-render-app.onrender.com/api/mapping', {
  method: 'POST',
  body: formData
});

const blob = await response.blob();
// Handle the Excel file download
```

## Deployment

### Render Deployment

1. **Connect your repository to Render:**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Name:** `the-forge-api`
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically deploy your application

### Docker Deployment

1. **Build the image:**
```bash
docker build -t the-forge-api .
```

2. **Run the container:**
```bash
docker run -p 8000:8000 the-forge-api
```

3. **Access the API:**
```
http://localhost:8000
```

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the application:**
```bash
uvicorn main:app --reload
```

3. **Access the API:**
```
http://localhost:8000
```

## API Documentation

Once deployed, you can access the interactive API documentation at:
- **Swagger UI:** `https://your-render-app.onrender.com/docs`
- **ReDoc:** `https://your-render-app.onrender.com/redoc`

## File Format Support

### Input Formats
- **JSON Schema:** `.json` files following JSON Schema specification
- **XSD:** `.xsd` and `.xml` files following XML Schema Definition

### Output Formats
- **Excel:** `.xlsx` files with formatted schema information
- **JSON Schema:** `.json` files with proper JSON Schema structure
- **XSD:** `.xsd` files with XML Schema Definition

## Error Handling

The API returns appropriate HTTP status codes:
- **200:** Success
- **400:** Bad Request (invalid file format, missing parameters)
- **500:** Internal Server Error (processing errors)

## Rate Limiting

The free tier on Render may have rate limits. For production use, consider upgrading to a paid plan.

## Security

- CORS is enabled for all origins (configure as needed for production)
- File uploads are validated for supported formats
- Temporary files are cleaned up after processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project maintains the same license as the original Forge application. 