# Concessions Cash Register app

 Designed for applications where no internet exists.
 Designed with the concept of a customer account
 
 Uses SQLModel objects and FastAPI for database interaction.
 Uses Streamlit for a locally-served user interface

 Basically, cut down on redundancy and handoffs/mapping, to make a unified API / WebForm / Database flow.

 1. Launch the Fastapi server  (from project root: fastapi run api\main.py)   http://localhost:8000/docs to see the endpoints
 2. Launch the UI (from project root: python launch_ui.py) (this will launch a Streamlit server)
 3. Browser should pop up at http://localhost:8501
 Register: to create transactions
 Customers: to manage Customer data details
 Products: to manage Product data details
