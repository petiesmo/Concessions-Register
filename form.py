#form.py

import streamlit as st
import streamlit_pydantic as sp

from models import Project

data = sp.pydantic_form(key="my_form", model=Project)
if data:
    st.json(data.json())
