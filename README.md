# ContextIQ

A Retrieval-Augmented Generation (RAG) chatbot using FastAPI, LangChain, LangGraph and MilvusDB backend and Vue frontend. Supports YouTube transcript and PDF ingestion for question answering.

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
- `docker compose -f docker/docker-compose.yml up --build`

