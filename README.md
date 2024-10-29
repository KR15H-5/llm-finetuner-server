
# LLM Fine-Tuner Backend

This is the backend microservice for the **LLM Fine-Tuner** project, enabling users to fine-tune language models with their own writing samples, such as essays and emails, to generate custom models that reflect individual tone, style, and vocabulary.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup and Installation](#setup-and-installation)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)


---

## Overview

The LLM Fine-Tuner backend is responsible for handling data preprocessing, model fine-tuning, and serving custom models through an API. By fine-tuning the model with personalized input data, it learns and generates responses that better match the user’s unique voice.

## Features

- **User Data Preprocessing**: Cleans and formats user-submitted text data for consistency.
- **Model Fine-Tuning**: Uses input data to adjust a pre-trained language model, aligning it with the user’s writing style.
- **Custom Model Serving**: Exposes fine-tuned models through a REST API for text generation.
- **Scalable Microservice Architecture**: Designed to work as part of a microservice setup with the frontend client.

## Technology Stack

- **Programming Language**: Python
- **Framework**: Flask or FastAPI (choose the one you’re using)
- **Machine Learning Library**: Hugging Face Transformers(Future Adoption for Deprecated SDK)
- **Containerization**: Docker

## Setup and Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/KR15H-5/llm-finetuner-server.git
   cd llm-finetuner-server
   ```

2. **Install Dependencies**
   It’s recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

4. **Run the Application**
   Start the server locally:
   ```bash
   python app.py
   ```

5. **Docker Deployment (Optional)**
   If deploying with Docker:
   ```bash
   docker build -t llm-finetuner-backend .
   docker run -p 8000:8000 llm-finetuner-backend
   ```

## API Endpoints

### Base URL
- `http://localhost:8000/` (or your deployment URL)

### Available Endpoints

| Method | Endpoint          | Description                                       |
|--------|--------------------|---------------------------------------------------|
| POST   | `/finetune`       | Fine-tunes the model with provided user data      |
| GET    | `/generate`       | Generates text based on the fine-tuned model      |
| GET    | `/view-model-adapters`         | Checks the status of the current finetuned models          |
- **`POST /finetune`**: Accepts a JSON payload with user text data, initiates model fine-tuning.
- **`GET /generate`**: Accepts a prompt and returns a generated response using the fine-tuned model.
- **`GET /view-model-adapters`**: Checks the status of the current finetuned models


## Usage

1. **Fine-Tune the Model**  
   Send a POST request to `/finetune` with user data to start the fine-tuning process.
2. **Generate Text**  
   Use the `/generate` endpoint to obtain model-generated responses based on user-specific tone.

---


