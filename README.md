# VidBot - AI-Powered YouTube Video Q&A App

This project allow you chat with any YouTube video just by pasting its URL. It extracts the transcript, chunks the content, embeds it into a vector database, and enables intelligent conversation using LLMs.

## Tech Stack

| Layer            | Technology             |
|------------------|------------------------|
| Backend API      | FastAPI, Uvicorn       |
| Vector Database  | Qdrant (local mode)    |
| LLM Providers    | OpenAI, Cohere, Gemini |
| Data Processing  | Langchain              |
| Async Database   | MongoDB (via Motor)    |

## Project Structure

```
VidBot/
└── src/
    ├── .env
    ├── main.py
    ├── requirements.txt
    ├── AI/
    │   ├── LLM/
    │   │   ├── __init__.py
    │   │   ├── LLMEnums.py
    │   │   ├── LLMFactory.py
    │   │   ├── LLMInterface.py
    │   │   ├── providers/
    │   │   │   ├── __init__.py
    │   │   │   ├── GeminiProvider.py
    │   │   │   └── OpenAIProvider.py
    │   │   └── templates/
    │   │       ├── __init__.py
    │   │       └── locales/
    │   │           ├── ar/
    │   │           │   └── rag.py
    │   │           └── en/
    │   │               └── rag.py
    │   └── VectorDB/
    │       ├── __init__.py
    │       ├── VDBInterface.py
    │       └── providers/
    │           ├── __init__.py
    │           └── QdrantProvider.py
    ├── controllers/
    │   ├── __init__.py
    │   ├── base_controller.py
    │   ├── data_controller.py
    │   ├── process_controller.py
    │   └── rag_controller.py
    ├── models/
    │   ├── __init__.py
    │   ├── video_model.py
    │   └── db_schemas/
    │       ├── __init__.py
    │       ├── chunks.py
    │       └── video.py
    ├── routes/
    │   ├── data.py
    │   ├── rag.py
    │   └── schema/
    │       └── __init__.py
    └── utils/
        ├── app_config.py
        └── app_enums/
            ├── __init__.py
            └── response_enums.py

```

## Requirements

- Python 3.10

#### Install Python using MiniConda

1) Download and install MiniConda from  [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment:
    ```bash
    $ conda create -n mini-rag python=3.10
    ```
3) Activate the environment:
    ```bash
    $ conda activate mini-rag
    ```

## API Endpoints Overview

| Endpoint                   | Method | Description                      |
| -------------------------- | ------ | -------------------------------- |
| `/welcome`                 | GET    | App health check                 |
| `/data/upload_url`         | POST   | Upload a YouTube video URL       |
| `/{video_id}/index/push/`  | POST   | Index chunks into vector DB      |
| `/{video_id}/index/info`   | GET    | Get vector DB collection info    |
| `/{video_id}/index/search` | POST   | Search vector DB using text      |
| `/{video_id}/index/answer` | POST   | Ask a question and get an answer |


## Installation

### 1- Clone the Repository

```bash
$ git clone https://github.com/tawfikhammad/chat-with-video.git VidBot

$ cd VidBot
```

### 2- Install the required packages

```bash
$ cd src
$ pip install -r requirements.txt
```

### 3- Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## 4- Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```
- update `.env` with your credentials

```bash
$ cd docker
$ sudo docker compose up -d
```

## 5- Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```