#streamlit/form_tx.py
'''Concession Register - Transaction input form
    Interacts with the API (not the database directly)'''

import os
import sys
import time
from typing import List

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import httpx
import pandas as pd
import streamlit as st
from streamlit_extras.card import card
from streamlit_extras.grid import grid

from db.models import Customer, CustomerCreate, CustomerShort, CustomerRead
from db.models import Product, ProductCreate, ProductShort, ProductRead
from db.models import Transaction, TxCreate
from db.models import LineItem, Payment


# Helper functions to fetch customers from the database
def get_customers() -> List[CustomerRead]:
    customers = [   
            CustomerCreate(id=997, name='Johnny Depp'),
            CustomerCreate(id=998, name='Sandra Bullock', staff=True, acct_balance=10.00),
            CustomerCreate(id=999, name='Donald Trump', acct_balance=1000.00)
        ]
    res = httpx.get('http://localhost:8000/customers/all')
    if res.status_code == 200:
        customers = [Customer(**x) for x in res.json()]
    return customers


# Helper function to fetch items from the database
def get_items() -> List[ProductShort]:
    products = [   
            ProductCreate(id=997, name='Candy Bar', price=0.75, emoji='🍫'),
            ProductCreate(id=998, name='Slushie', price=1.00, emoji='🍦'),
            ProductCreate(id=999, name='Soda', price=1.00, emoji='🥤'),
            ProductCreate(id=996, name='Popcorn', price=0.50, emoji='🍿')
        ]
    res = httpx.get('http://localhost:8000/products/all')
    if res.status_code == 200:
        products = [Product(**x) for x in res.json()]
    return products


# Sidebar for selecting customer
def select_customer(customers):
    st.subheader("Select Customer")
    # Perform customer search based on query
    customer_dict = {customer.name: customer for customer in customers}
    selected = st.selectbox("Customer (type to search)", customer_dict.keys())
    selected_customer = customer_dict[selected]
    return selected_customer

def format_merch_item(item):
    return f"{item.emoji} {item.name} - ${item.price:.2f}"

def add_to_cart(selected_item, qty):
    line_item = LineItem(item_id=selected_item.id, name=selected_item.name, price=selected_item.price, qty=qty)
    st.session_state.cart.append(line_item.model_dump())
    return line_item

# Sidebar for selecting items
def select_item(items) -> dict | None:
    st.subheader("Select Product")
    form = st.form('fm_select_item', clear_on_submit=True, border=True)
        # Perform item search based on query
    selected_item = form.selectbox("Product", options=items, format_func=format_merch_item)
    qty = form.number_input("Quantity", min_value=1, value=1)
    #selected_item
    if form.form_submit_button("Add to Cart"):
        line_item = add_to_cart(selected_item, qty)
        return line_item
    return None


def quick_select_item(items):
    '''my_grid = grid(3,3,3, vertical_align='center')
    #with my_grid.expander("Show Filters", expanded=True):
    for item in items:
        my_grid.button(item.emoji + item.name, use_container_width=True)
    '''

    button_text = items
    for item, col in zip(button_text, st.columns(len(button_text))):
        if col.button(label=format_merch_item(item)):
            col.write(f"{item.name} clicked")
            add_to_cart(item,1)
    

# Main section for displaying cart and total
def display_cart(cart):
    st.subheader("🛒 Cart")
    if not cart:
        st.write("Cart is empty.")
        return 0
    #Configure the column properties    
    cart_columns = {
        'item_id': st.column_config.TextColumn("ID", disabled=True),
        'name': st.column_config.TextColumn("Name", disabled=True),
        'price': st.column_config.NumberColumn("Price", min_value=0.00, format='$%.2f'),
        'qty': st.column_config.NumberColumn("QTY", min_value=0)
    }
    #Display and allow user to update the quantities in the cart
    df = pd.DataFrame(cart)
    edited_df = st.data_editor(df, key="my_cart", column_config=cart_columns, num_rows='dynamic')#, use_container_width=True)
    total = round((edited_df.price * edited_df.qty).sum(),2)
    st.write(f"Total: $***{total:.2f}***")
    #Preserve finished cart in state
    st.session_state.cart = edited_df.to_dict('records')
    return total


@st.cache_data
def acct_total(total, cash, coupon):
    return total - cash - coupon
   

# Payment options
def payment_options(total:float) -> Payment:
    st.subheader("Payments")
    coupon = st.number_input("Coupon/Voucher/Discount", min_value=0.00, value=0.00)
    cash = st.number_input("Cash/Check", min_value=0.00, value=0.00)
    acct = st.number_input("Customer Account", min_value=0.00, value=acct_total(total,cash,coupon))
    return Payment(cash=cash, coupon=coupon, account=acct)


def formatted_balance(bal):
    if bal > 0:
        return f"""***{bal:.2f}***✅"""
    else:
        return f"""***{bal:.2f}***❌"""


def save_transaction(tx: TxCreate):
    tx_dict = tx.model_dump()
    st.write(f'Submitting tx data: {tx_dict}')
    response = httpx.post("http://localhost:8000/tx/", json=tx_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ Transaction submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit transaction. {response.status_code} | {response.text}')
    return False

def clear_session_state():
    # Delete all the items in Session state
    for key in st.session_state.keys():
        del st.session_state[key]

# Main function
def main_form(customers:List[Customer], merch:List[Product]):
    st.set_page_config(
        page_title="Concessions Cash Register",
        page_icon="🎪",
        layout="wide",
        initial_sidebar_state="expanded"    #, menu_items=[]
        )
    st.title('💵 Concessions Cash Register')

    if 'cart' not in st.session_state:
        st.session_state.cart = list()
    cart = st.session_state.cart


    # Select customer &
    # Display customer details
    colA, colB, colC = st.columns([.5,.1,.4])
    with colA:
        selected_customer = select_customer(customers)
        st.session_state['customer'] = selected_customer
    with colC:
        st.subheader("Selected Customer")
        st.write(f"Selected Customer: {selected_customer.name}")
        st.write(f"Account Balance: $***{selected_customer.acct_balance:.2f}***")     
    st.divider()

    with st.popover('Other items'):
        line_item = select_item(merch)
    
    q_line_item = quick_select_item(merch)
    #Display cart and register details
    col1, col2, col3 = st.columns([.5,.1,.4])
    with col1:
        total = display_cart(cart)
        tx_note = st.text_area('Note')
    with col3:
        payment = payment_options(total)
        projected_balance = selected_customer.acct_balance - payment.account
        st.markdown(f"Projected Balance: ${formatted_balance(projected_balance)}",)
    
    tx_saved = False
    if sum(payment.model_dump().values()) == total:
        if total > selected_customer.acct_balance:
            col3.write("Insufficient Account Balance.  Add cash or reduce items.")
        else:
            if st.button("Submit"):
                st.write(cart)
                tx_data = TxCreate(
                    customer_id=selected_customer.id,
                    total=total,
                    cart=cart,
                    pmt=payment.model_dump(),
                    note=tx_note
                )
                tx_data
                tx_saved = save_transaction(tx_data)
                
    if tx_saved:            
        #Reset the form
        time.sleep(1)
        clear_session_state()
        st.rerun()  # Reload the page



if __name__ == "__main__":
    # Get items from the database
    customers = get_customers()
    merch = get_items()
    main_form(customers, merch)


'''Fixes needed:
1. Fix floating error on Acct Balance
2. Reset all elements during st.rerun (dump session state)'''

'''Ideas:
0. Hot Buttons / Cards
1. Recent transactions - opportunity to do a refund?
2. Multipage (admin)
2a. Merge management
2b. Customer management
2c. **How to add cash to account
2d. Checkout'''


