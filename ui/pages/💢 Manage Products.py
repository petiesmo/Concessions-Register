#streamlit/Manage Products.py
'''Concession Register - Input/Edit Products
    Interacts with the API (not the database directly)'''

import time
from typing import List

import httpx
import pandas as pd
import streamlit as st

#from db.models import Product, ProductCreate, ProductShort, ProductRead, ProductUpdate
ss = st.session_state
ss.messages = list()
ss

# Helper function to fetch items from the database
def get_products() -> List[dict]:   #Product]:
    res = httpx.get('http://localhost:8000/products/all')
    if res.status_code == 200:
        return res.json()   #[Product(**x) for x in res.json()]
    return [{'Error': 'No products retrieved'}]
    '''fake_products = [   
            ProductCreate(id=997, name='Fake Candy Bar', price=0.75, emoji='🍫'),
            ProductCreate(id=998, name='Slushie', price=1.00, emoji='🍦'),
            ProductCreate(id=999, name='Soda', price=1.00, emoji='🥤'),
            ProductCreate(id=996, name='Popcorn', price=0.50, emoji='🍿')
        ]
    return fake_products'''


# Main section for interacting with Products
def save_new_product(prod):     #ProductCreate):
    prod_dict = prod    #.model_dump()
    ss.messages.append(f'Submitting product data: {prod_dict}')
    response = httpx.post("http://localhost:8000/products/", json=prod_dict)
    ss.messages.append(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ New Product submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit Product. {response.status_code} | {response.text}')
    return False

def update_delta_product(prod_id, prod_dict): #: ProductUpdate):
    #prod_dict = prod.model_dump()
    ss.messages.append(f'Submitting product data: {prod_dict}')
    response = httpx.patch(f"http://localhost:8000/products/{prod_id}", json=prod_dict)
    ss.messages.append(f'Server response: {response.json()}')
    if response.status_code == 200:
        st.toast(f'✅ Product {prod_id} changes submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit Product {prod_id}. {response.status_code} | {response.text}')
    return False

def delete_product(prod_id): 
    ss.messages.append(f'Deleting product #: {prod_id}')
    response = httpx.delete(f"http://localhost:8000/products/{prod_id}")
    ss.messages.append(f'Server response: {response.status_code} | {response.json()}')
    if response.status_code == 200:
        st.toast(f'✅ Product {prod_id} changes submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit Product {prod_id}. {response.status_code} | {response.text}')
    return False

#To see only the elements that have changed or been added
# https://docs.streamlit.io/develop/concepts/design/dataframes#access-edited-data


# Main function
def main_form():
    st.title('💢 Concessions - Product Management')
    st.write('Products populated from the database.')
    st.write('Products may be edited.')
    st.write('Products may be added in a new row at the bottom of the table (copy/paste OK).')
    products = ss.products
    df = pd.DataFrame(products)
    form1 = st.form('fm_edit_products', clear_on_submit=False, border=True)
    with form1:
        cart_columns = {
            'id': st.column_config.TextColumn("ID", disabled=True),
            'SKU': st.column_config.TextColumn("SKU"),
            'name': st.column_config.TextColumn("Name"),
            'description': st.column_config.TextColumn("Description"),
            'price': st.column_config.NumberColumn("Price", min_value=0, format='$%.2f'),
            'qty': st.column_config.NumberColumn("Qty", min_value=0, format='%.2f'),
            'emoji': st.column_config.TextColumn("Emoji")
        }

        edited_df = st.data_editor(df, key="my_products", column_config=cart_columns, num_rows='dynamic', use_container_width=True)
        if st.form_submit_button("Review Changes"):
            ss.products = edited_df.to_dict('records')
    #ss.my_products
    form2 = st.form('fm_review_product_changes', clear_on_submit=True, border=True)
    with form2:
        creates = ss.my_products.get('added_rows',list())
        st.write("To Create: ")
        new_products = creates  #[ProductCreate(**cst) for cst in creates]
        new_products

        updates = ss.my_products.get('edited_rows',list())
        st.write("To Update: ")
        #Updates will be a little more complicated since they reference the order of the list
        delta_products = {str(df.iloc[row].loc['id']):prd  for row,prd in updates.items()}  #ProductUpdate(**cst)
        delta_products

        deletes = ss.my_products.get('deleted_rows',list())
        st.write("To Delete: ")
        trash_products = [str(df.iloc[row].loc['id']) for row in deletes]  #ProductUpdate(**cst)
        trash_products
        ss.messages
        if st.form_submit_button("Process Changes"):
            for np in new_products: save_new_product(np)
            for key,dp in delta_products.items(): update_delta_product(key,dp)
            for key in trash_products: delete_product(key)
            ss.messages
            ss.clear()


if __name__ == "__main__":
    if 'ploaded' not in ss:
        products = get_products()
        #st.write(vars(_customers[0]))
        #products = [cst.model_dump() for cst in _products]
        ss.products = products
        ss.ploaded = True
    main_form()


""" 🍴  🍧  🍦  🍫  🍬  🍭  🍿  🚰  💦  💧  🍹  🥤  🧋  ☕  🥜  🥒  🥨  🌭  🍔  🍕  🍟  🌶️  🥓  🧀  🍒  🍦  🍩  🍪  🧁
👀  📢  📣  🔋  🔦  ✝   🙏  🧊  🛠️  ⛺                 
🧢  👕  👚  🎒  🎽  🎁  🎉  💢  💟   ❤  ❣️    
🧾  ⚖   🛍  🧮  🪙  🆓  💲  🎟   ⚠  🚫  ⛔
😎  😓  👽  👼  😇  😎  😓  🚹  🚺  🚻  🫶  👨‍👩‍👧‍👦  👩‍🍳
🌍  ☀️  ♻️  ❄️  ⭐
✢  ✣  ✤  ✦  ✧  ★  ☆  ✯  ✪  ✫  ✮  ♠︎  ♣︎  ♥︎  ♦︎  ⚀ ⚁ ⚂ ⚃ ⚄ ⚅   
&nbsp; &ensp; &emsp;

"""

