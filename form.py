#form.py

import streamlit as st
import streamlit_pydantic as sp

from models import Project, Customer

customer = sp.pydantic_form(key="customer_form", model=Customer)
if customer:
    st.json(customer.json())

project = sp.pydantic_form(key="my_form", model=Project)
if project:
    st.json(project.json())
