# Technical Project Description

This document provides a detailed technical overview of the project, covering its architecture, technologies, and key components.

## Project Overview

This project is a full-stack web application with a monolithic repository (`monorepo`) structure. It consists of a React-based frontend and a Python-based backend, designed to leverage cloud-native services for scalability and functionality.

## Architecture

The application follows a classic client-server architecture:

-   **Frontend:** A single-page application (SPA) built with React that runs in the user's browser.
-   **Backend:** A Python Flask server that exposes a RESTful API for the frontend.
-   **Cloud Integration:** The backend is tightly integrated with Amazon Web Services (AWS) to provide core functionalities like data storage, file management, and generative AI capabilities.

---

## Backend Subsystem

The backend is a Python application built using the Flask web framework.

### Core Technologies

-   **Language:** Python
-   **Web Framework:** Flask (`flask`, `gunicorn` for production deployment)
-   **AWS SDK:** Boto3 (`boto3`) is used for all interactions with AWS services.

### Key Components & Modules

-   `app.py`: The main entry point for the Flask application, defining API routes and handling HTTP requests.
-   `requirements.txt`: Manages all Python dependencies.
-   **AWS Service Integrations:**
    -   `bedrock_agent.py`: Implements an agent that interacts with **Amazon Bedrock**, suggesting the use of generative AI models for features like summarization, content generation, or chatbots.
    -   `dynamodb_client.py`: Contains logic to interact with **Amazon DynamoDB**, which serves as the primary NoSQL database for the application.
    -   `s3_client.py`: Manages interactions with **Amazon S3` for object storage, likely used for storing user-uploaded files, images, or documents (PDFs, as suggested by the `PyPDF2` and `Pillow` dependencies).
-   **API Clients (`api_clients/`)**: This directory likely contains modules for interacting with external or third-party APIs.
-   **Serverless Functions (`lambda_functions/`)**: This directory suggests the project may deploy serverless functions using AWS Lambda for specific, event-driven tasks.
-   **Utilities (`utils.py`)**: A common module for helper functions and shared logic.

### Environment & Configuration

-   Secrets and environment variables are managed via a `.env` file, loaded using `python-dotenv`.

---

## Frontend Subsystem

The frontend is a modern single-page application built with React.

### Core Technologies

-   **Library:** React
-   **Build & Development:** Create React App (`react-scripts`) is used for bootstrapping the development environment, running tests, and building the application for production.
-   **Package Manager:** npm

### Key Components

-   `src/`: This directory contains all the React components, application logic, and styling.
-   `public/`: Contains the main `index.html` file and other static assets.
-   `package.json`: Defines project metadata, scripts (`start`, `build`, `test`), and lists all frontend dependencies.

### Backend Communication

-   The frontend communicates with the backend via HTTP requests to the Flask API.
-   During development, a proxy is configured in `package.json` to forward API requests from `http://localhost:3000` (the default React dev server port) to the backend server at `http://localhost:5000` to avoid CORS issues.
