# 🤖 AI Presentation Generator API

A powerful FastAPI-based API that automatically generates PowerPoint presentations from a given topic using AI. 
This project leverages background tasks with ARQ and Redis for a non-blocking, responsive user experience.

---

## ✨ Features

* **AI Content Generation**: Uses OpenAI's GPT models to generate slide titles and content.
* **Asynchronous by Design**: Employs background tasks with ARQ, so the API responds instantly while presentations are generated in the background.
* **Customizable Output**: Supports different aspect ratios, templates, and even custom fonts and colors per request.
* **Secure & Scalable**: Protected by API keys and includes rate limiting to prevent abuse.
* **Built with Docker**: Fully containerized for easy setup and deployment.

---

## 🛠️ Tech Stack

* **Backend**: FastAPI
* **Web Server**: Uvicorn
* **Task Queue**: ARQ
* **In-Memory Database / Broker**: Redis
* **Presentation Generation**: `python-pptx`
* **AI Service**: OpenAI
* **Containerization**: Docker & Docker Compose

---

## 🚀 Setup and Installation

Follow these steps to set up and run the project locally.

### Prerequisites

* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <repository-folder>

### 2. Configure Environment Variables

Create a file named .env in the root of the project and below ENV(s). This file is used to store sensitive information like API keys.

# Application Basic Settings
APP_NAME="Presentation Generator Service"
API_V1_STR="/api/v1"

# Redis Configuration (for Caching and Message Broker for ARQ)
REDIS_URL="redis://redis:6379/0"

# Comma-separated list of allowed API keys for our service
# Anyone calling our API must provide one of these in the X-API-Key header, same as OpneAI and other LLM service gives an API key to handle rate limiting and authentication.
ALLOWED_API_KEYS_STR="secret-key-1,adilnawaz123654654"

# Rate limit for most requests ( getting the status of presentaion creation)
DEFAULT_RATE_LIMIT="100/minute"
# Stricter rate limit for the expensive creation endpoint
CREATE_RATE_LIMIT="20/minute"

# Add secret key for the OpenAI API
OPENAI_API_KEY="sk-..."

### 3. Build and Run the Application

Use Docker Compose to build the images and start the services (API, worker, and Redis).

docker-compose up --build

### 4. Verify Installation

The application containers should be running without errors in the terminal. 
We can verify that the API is running by navigating to the auto-generated documentation in your browser:

Swagger UI: http://localhost:8000/docs

### API Endpoints

The API is automatically documented using Swagger UI. Once the application is running, we can interact with the API live at the links below:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Method	                Endpoint	                                            Description
POST	            /api/v1/presentations/	                        Submits a new presentation generation job.
GET	                /api/v1/presentations/{id}	                    Checks the status of a presentation job.
GET	                /api/v1/presentations/{id}/download	            Downloads the completed .pptx file.
POST	            /api/v1/presentations/{id}/configure	        Modifies a presentation's config.