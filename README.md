# ContextIQ

A production-grade Retrieval-Augmented Generation (RAG) chatbot using FastAPI, LangChain, LangGraph and MilvusDB backend and Vue frontend. Supports YouTube transcript and PDF ingestion for question answering.

## Features
- Upload a PDF or provide a YouTube URL
- Chat with the content (YouTube transcript or PDF)
- Modern Vue frontend
- FastAPI backend with LangChain, LangGraph, MilvusDB
- Authentication support

## Frontend
- Built with Vue (see `frontend/`)

## Backend
- FastAPI, LangChain, LangGraph, Milvus (see `backend/`)

## Usage
1. Setup
    - Python 3.9+ with virtual environment
    - docker
    - All dependencies installed (see requirements.txt)
    steps:
    # environment setup
    - clone the repo
    - create virual environemnt `python -m venv .venv`
    - activate virtual environment `source .venv/bin/activate`
    - install dependencies `pip install -r requirements.txt`

    # DB setup(this will run a milvus DB on docker)
    - Install docker desktop
    - `cd docker`
    - `sudo docker compose up -d`

2. Start backend
    - backend service `python -m backend.main`
3. Start Frontend
    - run frontend `npm run dev --prefix frontend`

## License
MIT
