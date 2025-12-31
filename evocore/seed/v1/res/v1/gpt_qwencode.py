architect agent using time: 14.738476991653442
architecture: {
    'project_name':'CodeGenAgentService',
    'project_type':'Microservice',
    'tech_stack':{'backend': 'FastAPI', 'runtime': 'Python 3.11', 'containerization': 'Docker', 'cloud_platform': 'Google Cloud Platform', 'deployment': 'Cloud Run', 'orm': 'None', 'testing': 'pytest', 'linting': 'black, isort', 'type_checking': 'mypy', 'logging': 'loguru', 'environment': 'dotenv', 'authentication': 'None'},
    'global_requirements':['Containerized deployment with Dockerfile', 'Expose /health endpoint for Cloud Run health checks', 'Use environment variables for configuration', 'Include unit tests and CI workflow', 'Provide a README with build and deploy instructions']
    'files':[
        FileSpec(path='Dockerfile', description='Docker image definition for the FastAPI app, based on python:3.11-slim.', responsibilities='Defines the base image, installs dependencies, copies application code, sets the entrypoint to uvicorn, and exposes port 8080 for Cloud Run.'), 
        FileSpec(path='requirements.txt', description='Python dependencies for the service.', responsibilities='Lists all required packages such as fastapi, uvicorn, pydantic, python-dotenv, loguru, and testing libraries.'), 
        FileSpec(path='app/main.py', description='Entrypoint for the FastAPI application.', responsibilities='Initializes FastAPI, mounts routers, configures middleware, and starts the uvicorn server when run directly.'), 
        FileSpec(path='app/routers/generation.py', description='API router that exposes the code generation endpoint.', responsibilities='Defines POST /generate endpoint that accepts user prompt and returns generated code snippets.'), 
        FileSpec(path='app/services/generator.py', description='Core logic for generating code using predefined templates or a simple rule-based engine.', responsibilities='Processes the prompt, selects the appropriate template, and returns the generated code string.'), 
        FileSpec(path='app/models.py', description='Pydantic models for request and response schemas.', responsibilities='Defines request payload structure (e.g., prompt, language) and response payload containing the generated code.'), 
        FileSpec(path='tests/test_generation.py', description='Unit tests for the generation service.', responsibilities='Verifies that given a sample prompt, the service returns a non-empty code string and adheres to the response schema.'), 
        FileSpec(path='.dockerignore', description='Files and directories ignored during Docker build.', responsibilities='Exclude .git, __pycache__, and local virtual environments from the Docker context.'), 
        FileSpec(path='.github/workflows/ci.yml', description='GitHub Actions workflow for CI.', responsibilities='Runs linting, type checking, unit tests, and builds the Docker image on push.'), 
        FileSpec(path='README.md', description='Project overview and deployment instructions.', responsibilities='Explains how to build the image, push to GCR, and deploy to Cloud Run, including environment variable configuration.')]
}


FILE: Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

FILE: requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
loguru==0.7.2
pytest==7.4.3
black==23.11.0
isort==5.12.0
mypy==1.7.0
pytest-cov==4.1.0

FILE: app/main.py
from fastapi import FastAPI
from app.routers import generation
from loguru import logger

app = FastAPI(title="CodeGenAgentService")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(generation.router)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)

FILE: app/routers/generation.py
from fastapi import APIRouter, HTTPException
from app.services.generator import generate_code
from app.models import CodeGenerationRequest, CodeGenerationResponse

router = APIRouter(prefix="/generate", tags=["generation"])

@router.post("/", response_model=CodeGenerationResponse)
async def generate(request: CodeGenerationRequest):
    try:
        code = generate_code(request.prompt, request.language)
        return CodeGenerationResponse(code=code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

FILE: app/services/generator.py
from loguru import logger

def generate_code(prompt: str, language: str) -> str:
    logger.info(f"Generating code for prompt: {prompt}")
    
    # Simple rule-based code generation
    if language == "python":
        if "hello world" in prompt.lower():
            return "print('Hello, World!')"
        elif "loop" in prompt.lower():
            return "for i in range(10):\n    print(i)"
        elif "function" in prompt.lower():
            return "def my_function():\n    pass"
        else:
            return "# Generated code snippet\nprint('Code generated successfully')"
    elif language == "javascript":
        if "hello world" in prompt.lower():
            return "console.log('Hello, World!');"
        elif "loop" in prompt.lower():
            return "for (let i = 0; i < 10; i++) {\n    console.log(i);\n}"
        elif "function" in prompt.lower():
            return "function myFunction() {\n    // Function body\n}"
        else:
            return "// Generated code snippet\nconsole.log('Code generated successfully');"
    else:
        return "# Generated code snippet\n// Language not supported"

FILE: app/models.py
from pydantic import BaseModel
from typing import Optional

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str

class CodeGenerationResponse(BaseModel):
    code: str

FILE: tests/test_generation.py
import pytest
from app.services.generator import generate_code
from app.models import CodeGenerationRequest, CodeGenerationResponse

def test_generate_code_python_hello():
    result = generate_code("hello world", "python")
    assert result is not None
    assert "Hello, World!" in result

def test_generate_code_python_loop():
    result = generate_code("loop", "python")
    assert result is not None
    assert "for i in range" in result

def test_generate_code_javascript_hello():
    result = generate_code("hello world", "javascript")
    assert result is not None
    assert "Hello, World!" in result

def test_generate_code_javascript_loop():
    result = generate_code("loop", "javascript")
    assert result is not None
    assert "for (let i = 0" in result

def test_generate_code_unsupported_language():
    result = generate_code("hello world", "go")
    assert result is not None

def test_request_response_models():
    request = CodeGenerationRequest(prompt="test", language="python")
    response = CodeGenerationResponse(code="test code")
    assert request.prompt == "test"
    assert response.code == "test code"

FILE: .dockerignore
.git
__pycache__
*.pyc
.env
.env.local
.env.*.local
.DS_Store
node_modules
.env
*.env

FILE: .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run linting
      run: |
        black --check .
        isort --check-only .
        mypy .
    - name: Run tests
      run: |
        pytest tests/
    - name: Build Docker image
      run: |
        docker build -t codegen-agent-service .

FILE: README.md
# CodeGenAgentService

A microservice for generating code snippets based on natural language prompts.

## Overview

This service provides a simple API endpoint that accepts a prompt and programming language, then returns a generated code snippet.

## Building and Deploying

### Prerequisites

- Docker
- Google Cloud SDK (for deployment to Cloud Run)

### Build

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/codegen-agent-service .
```

### Push to Google Container Registry

```bash
docker push gcr.io/YOUR_PROJECT_ID/codegen-agent-service
```

### Deploy to Cloud Run

```bash
gcloud run deploy --image gcr.io/YOUR_PROJECT_ID/codegen-agent-service --platform managed
```

### Environment Variables

The service uses environment variables for configuration. Create a `.env` file with the following variables:

```
# Example environment variables
DEBUG=true
```

## API Endpoints

### `POST /generate`

Generates code based on the provided prompt and language.

**Request Body:**
```json
{
  "prompt": "string",
  "language": "string"
}
```

**Response:**
```json
{
  "code": "string"
}
```

## Health Check

The service exposes a `/health` endpoint for Cloud Run health checks:

```bash
curl http://your-service-url/health
```

## Testing

Run tests with:

```bash
pytest tests/
```

## CI/CD

The service includes a GitHub Actions workflow that runs linting, type checking, and tests on every push and pull request. The workflow also builds the Docker image.