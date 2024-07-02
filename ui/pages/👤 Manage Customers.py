#streamlit/Manage Customers.py
'''Concession Register - Input/Edit Customers
    Interacts with the API (not the database directly)'''

import time
from typing import List

import httpx
import pandas as pd
import streamlit as st

#from db.models import CustomerCreate
ss = st.session_state

# Helper functions to fetch customers from the database
def get_customers() -> List[dict]:
    res = httpx.get('http://localhost:8000/customers/all')
    if res.status_code == 200:
        return res.json()   #[Customer(**x) for x in res.json()]
    return [{'Error': 'No customers retrieved'}]
    '''fake_customers = [   
        CustomerCreate(id=997, name='Johnny Depp (Fake!)'),
        CustomerCreate(id=998, name='Sandra Bullock', staff=True, acct_balance=10.00),
        CustomerCreate(id=999, name='Donald Trump', acct_balance=1000.00)
    ]
    return fake_customers'''


# Main section for displaying customers
def save_new_customer(cst: dict):   #CustomerCreate):
    cst_dict = cst  #cst.model_dump()
    st.write(f'Submitting customer data: {cst_dict}')
    response = httpx.post("http://localhost:8000/customers/", json=cst_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ New Customer submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit customer. {response.status_code} | {response.text}')
    return False

def update_delta_customer(cst_id, cst_dict): #CustomerUpdate):
    #cst_dict = cst.model_dump()
    st.write(f'Submitting customer data: {cst_dict}')
    response = httpx.patch(f"http://localhost:8000/customers/{cst_id}", json=cst_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 200:
        st.toast(f'✅ Customer {cst_id} changes submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit customer {cst_id}. {response.status_code} | {response.text}')
    return False

#To see only the elements that have changed or been added
# https://docs.streamlit.io/develop/concepts/design/dataframes#access-edited-data

def delete_customer(cst_id): 
    st.write(f'Deleting product #: {cst_id}')
    response = httpx.delete(f"http://localhost:8000/customers/{cst_id}")
    st.write(f'Server response: {response.status_code} | {response.json()}')
    if response.status_code == 200:
        st.toast(f'✅ Product {cst_id} changes submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit Product {cst_id}. {response.status_code} | {response.text}')
    return False

def formatted_balance(bal):
    if bal > 0:
        return f"""***{bal:.2f}***✅"""
    else:
        return f"""***{bal:.2f}***❌"""

# Main function
def main_form():
    st.title('👤 Concessions - Customer Account Management')
    st.write('Customers populated from the database.')
    st.write('Customers may be edited.')
    st.write('Customers may be added in a new row at the bottom of the table (copy/paste OK).')
    customers = ss.customers
    df = pd.DataFrame(customers)
    form1 = st.form('fm_edit_customers', clear_on_submit=False, border=True)
    with form1:
        cart_columns = {
            'id': st.column_config.TextColumn("ID", disabled=True),
            'name': st.column_config.TextColumn("Name"),
            'badge_id': st.column_config.TextColumn("Badge"),
            'acct_balance': st.column_config.NumberColumn("Balance", min_value=0, format='$%.2f'),
            'staff': st.column_config.CheckboxColumn('Is Staff', default=False),
            'active': st.column_config.CheckboxColumn('Active', default=False)
        }
        edited_df = st.data_editor(df, key="my_customers", column_config=cart_columns, num_rows='dynamic', use_container_width=True)
        if st.form_submit_button("Review Changes"):
            pass
    form2 = st.form('fm_review_customer_changes', clear_on_submit=True, border=True)
    with form2:
        creates = ss.my_customers.get('added_rows',list())
        st.write("To Create: ")
        new_customers = creates #[CustomerCreate(**cst) for cst in creates]
        new_customers

        updates = ss.my_customers.get('edited_rows',list())
        st.write("To Update: ")
        delta_customers = {str(df.iloc[row].loc['id']):cst for row,cst in updates.items()}  #CustomerUpdate(**cst)
        delta_customers

        deletes = ss.my_customers.get('deleted_rows',list())
        st.write("To Delete: ")
        gone_customers = [str(df.iloc[row].loc['id']) for row in deletes]  #CustomerUpdate(**cst)
        gone_customers

        if st.form_submit_button("Process Changes"):
            for nc in new_customers: save_new_customer(nc)
            for cid,dc in delta_customers.items(): update_delta_customer(cid,dc)
            for cid in gone_customers: delete_customer(cid)
            ss.clear()
    

if __name__ == "__main__":
    if 'cloaded' not in ss:
        customers = get_customers()
        #st.write(vars(_customers[0]))
        #customers = [cst.model_dump() for cst in _customers]
        ss.customers = customers
        ss.cloaded = True
    main_form()


