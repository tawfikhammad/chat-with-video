# VidBot - AI-Powered YouTube Video Q&A App

RAG application allows you chat with any YouTube video just by pasting its URL, supported both Arabic and English Languages. 

This project uses GitHub Actions for automated CI/CD workflow

## Tech Stack

| Layer            | Technology             |
|------------------|------------------------|
| Backend API      | FastAPI, Uvicorn       |
| Vector Database  | Qdrant (local mode)    |
| LLM Providers    | OpenAI, Cohere, Gemini |
| Data Processing  | Langchain              |
| Async Database   | MongoDB (via Motor)    |

## Requirements

- Python 3.11

#### Install Python using MiniConda

1) Download and install MiniConda from  [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment:
    ```bash
    $ conda create -n vidbot python=3.11
    ```
3) Activate the environment:
    ```bash
    $ conda activate vidbot
    ```

## API Endpoints Overview

| Endpoint                   | Method | Description                      |
| -------------------------- | ------ | -------------------------------- |
| `/welcome`                 | GET    | App health check                 |
| `/data/upload_url`         | POST   | Upload a YouTube video URL       |
| `/{video_id}/index/`       | POST   | Index chunks into vector DB      |
| `/{video_id}/info`         | GET    | Get vector DB collection info    |
| `/{video_id}/search`       | POST   | Search vector DB using text      |
| `/{video_id}/answer`       | POST   | Ask a question and get an answer |


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
$ cd src
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## 4- Run Docker Compose Services

```bash
$ docker compose up -d
```

## 5- Run the FastAPI server

```bash
$ cd src
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```