<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/82910a17-0c92-4738-9ab6-4217e1d4ef4b

## Run Locally

This project uses a standard **Vite + React** frontend and a **Python FastAPI** backend to run the AI assistant locally. 

**Prerequisites:** Node.js, Python 3.10+

### Setup the Environment

1. Set the `VITE_HF_API_KEY` in [.env.local](.env.local) to your free Hugging Face API key.

### Start the Python Backend

1. Navigate to the `backend` directory:
   `cd backend`
2. Create and activate a virtual environment:
   `python -m venv venv`
   `venv\Scripts\activate` (or `source venv/bin/activate` on mac/linux)
3. Install dependencies:
   `pip install -r requirements.txt`
4. Start the server:
   `fastapi dev main.py`

### Start the React Frontend

In a new terminal:
1. Install dependencies in the root root directory:
   `npm install`
2. Run the frontend:
   `npm run dev`

Navigate to `http://localhost:3000` to interact with the assistant!
