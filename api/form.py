#form.py

import streamlit as st
import streamlit_pydantic as sp

from models.models import Group, Item

item_form = sp.pydantic_form(key="item_form", model=Item)
if item_form:
    st.json(item.json())

group_form = sp.pydantic_form(key="group_form", model=Group)
if group_form:
    st.json(group.json())
