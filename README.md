# ✨ Lumina AI - Streamlit ChatBot Application

A modern, elegant AI-powered chatbot application built with Streamlit frontend and FastAPI backend. Lumina AI provides a conversational interface powered by Hugging Face's Qwen2.5-72B-Instruct model for next-generation customer support.

## 🎯 Features

- **Beautiful UI/UX**: Modern glassmorphism design with custom CSS styling
- **Real-time Chat**: Interactive conversation interface with message history
- **AI-Powered Responses**: Powered by Qwen2.5-72B-Instruct model via Hugging Face Inference API
- **Responsive Design**: Works seamlessly on different screen sizes
- **Error Handling**: Robust error handling with user-friendly messages
- **Easy Setup**: Simple installation and configuration process

## 🏗️ Architecture

Streamlit_AIChatBot_App/ 
├── app.py # Streamlit frontend application 
├── backend/ │ 
├── main.py # FastAPI backend server 
│ └── requirements.txt # Backend dependencies 
├── .gitignore 
└── README.md

### Technology Stack

**Frontend:**
- Streamlit - Web app framework
- Custom CSS with glassmorphism design
- Inter font for modern typography

**Backend:**
- FastAPI - High-performance web framework
- Uvicorn - ASGI server
- Hugging Face Hub - AI inference client
- Pydantic - Data validation

**AI Model:**
- Qwen/Qwen2.5-72B-Instruct - Advanced language model

## 📋 Prerequisites

- Python 3.8+
- Hugging Face API key ([Get one here](https://huggingface.co/settings/tokens))
- pip package manager

## 🚀 Quick Start

### 1. Clone the Repository
pip install -r backend/requirements.txt
