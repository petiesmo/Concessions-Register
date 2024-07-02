#streamlit/Register.py
'''Concession Register - Transaction input form
    Interacts with the API (not the database directly)'''

import time
from typing import List

import httpx
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid

#from db.models import CustomerCreate
#from db.models import ProductCreate
#from db.models import TxCreate
#from db.models import LineItem, Payment
st.set_page_config(
    page_title="Concessions Cash Register",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="collapsed"    #, menu_items=[]
    )
ss = st.session_state
ss

# Helper functions to fetch customers from the database
@st.cache_data
def get_customers() -> List[dict]:
    res = httpx.get('http://localhost:8000/customers/all')
    if res.status_code == 200:
        return res.json()   #[Customer(**x) for x in res.json()]
    return {'Error':'No customers retrieved'}
    '''customers = [   
        CustomerCreate(id=997, name='Johnny Depp (Fake!)'),
        CustomerCreate(id=998, name='Sandra Bullock (Fake!)', staff=True, acct_balance=10.00),
        CustomerCreate(id=999, name='Donald Trump (Fake!)', acct_balance=1000.00)
    ]
    return customers'''


# Helper function to fetch items from the database
@st.cache_data
def get_products() -> List[dict]:
    res = httpx.get('http://localhost:8000/products/all')
    if res.status_code == 200:
        return res.json()   #[Product(**x) for x in res.json()]
    return {'Error':'No products retrieved'}
    '''fake_products = [   
            ProductCreate(id=997, name='Candy Bar (FAKE!)', price=0.75, emoji='🍫'),
            ProductCreate(id=998, name='Slushie (Fake!)', price=1.00, emoji='🍦'),
            ProductCreate(id=999, name='Soda (Fake!)', price=1.00, emoji='🥤'),
            ProductCreate(id=996, name='Popcorn (Fake!)', price=0.50, emoji='🍿')
        ]
    return fake_products'''


# Customer Selection
def format_customer(cst):
    return f"{cst['badge_id']} | {cst['name']}"

def select_customer(customers):
    # Select customer from database list (searchable)
    selected_customer = st.selectbox("Customer (type to search)", customers, format_func=format_customer)
    ss.customer = selected_customer
    return selected_customer

def Customer_Section(customers):
    colA, colB = st.columns(2, gap='medium')
    with colA:
        selected_customer = select_customer(customers)
    with colB:
        st.write('Customer Acct Balance: ')
        st.markdown(f"{selected_customer['name']} &ensp;| &ensp; $***{selected_customer['acct_balance']:.2f}***")


# Merchandise Selection
def format_merch_item(item):
    return f"{item['emoji']} {item['name']} - ${item['price']:.2f}"

def add_to_cart(selected_item, qty):
    #Prepares data to be added to the cart
    #line_item = LineItem(item_id=selected_item.id, name=selected_item.name, price=selected_item.price, qty=qty)
    #ss.cart.append(line_item.model_dump())
    line_item = {
            'item_id':selected_item['id'],
            'name':selected_item['name'],
            'price': selected_item['price'],
            'qty':qty}
    ss.cart.append(line_item)
    return line_item

def select_item_form(items) -> dict | None:
    #Short form for selecting item + quantity
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

def quick_select_array(items, firstX=12):
    #Button array to quickly add one item to cart
    #TODO: User setting to nominate which buttons show up
    my_grid = grid(4,4,4, vertical_align='center')
    #with my_grid.expander("Show Filters", expanded=True):
    for item in items[:firstX]:
        if my_grid.button(label=format_merch_item(item), use_container_width=True):
            add_to_cart(item, 1)


def Items_Section(items):
    quick_select_array(items)
    with st.popover('All Items'):
        line_item = select_item_form(items)


# Main Register section - displaying cart and payments
def display_editable_cart(cart):
    #Displays the cart and total
    if not cart:
        st.write("Cart is empty.")
        return 0
    #Configure the column properties    
    cart_columns = {
        'sku': st.column_config.TextColumn("SKU", disabled=True),
        'name': st.column_config.TextColumn("Name", disabled=True),
        'price': st.column_config.NumberColumn("Price", min_value=0.00, format='$%.2f'),
        'qty': st.column_config.NumberColumn("QTY", min_value=0)
    }
    #Display and allow user to update the quantities in the cart
    df = pd.DataFrame(cart)
    edited_df = st.data_editor(df, key="my_cart", column_config=cart_columns, num_rows='dynamic')#, use_container_width=True)
    total = round((edited_df.price * edited_df.qty).sum(),2)
    st.write(f"Cart Total: $***{total:.2f}***")
    #Preserve finished cart in state
    ss.cart = edited_df.to_dict('records')
    return total

# Payment options
@st.cache_data
def acct_total(total, cash, coupon):
    return total - cash - coupon

def payment_options(total:float) -> dict:  #Payment:
    coupon = st.number_input("Coupon/Discount", min_value=0.00, value=0.00)
    cash = st.number_input("Cash/Check", min_value=0.00, value=0.00)
    acct = st.number_input("Customer Account", min_value=0.00, value=acct_total(total,cash,coupon))
    return {'cash':cash, 'coupon':coupon, 'account':acct} #Payment(cash=cash, coupon=coupon, account=acct)

def formatted_balance(bal):
    if bal > 0:
        return f"""***{bal:.2f}***✅"""
    else:
        return f"""***{bal:.2f}***❌"""

def Register_Section():
    #Primary register section - contains Cart and Payments
    if 'cart' not in ss:
        ss.cart = list()
    cart = ss.cart
    cst = ss.customer

    #Layout
    col1, col2 = st.columns(2, gap='medium')
    with col1:
        st.subheader("🛒 Cart")
        total = display_editable_cart(cart)
    
    with col2:
        col2.subheader("Payments")
        col2a,col2b = col2.columns(2)
        with col2a:
            payment = payment_options(total)
            projected_balance = cst['acct_balance'] - payment['account']
        with col2b:
            tx_note = st.text_input('Note')
            ss.tx_note = tx_note
            st.markdown(f"Projected Balance: ${formatted_balance(projected_balance)}")
    

    tx_saved = False
    if total > 0:
        if sum(payment.values()) == total:
            if total > cst['acct_balance']:
                col2b.write("Insufficient Account Balance.  Add cash or reduce items.")
            else:
                if col2b.button("Submit"):
                    tx_data = {         
                    'customer_id': cst['id'],
                    'total': total,
                    'cart': cart,
                    'pmt': payment,
                    'note': tx_note
                    }
                    tx_saved = save_transaction(tx_data)
    if col2b.button('RESET'): clear_session_state_and_rerun()
    return tx_saved

def save_transaction(tx): #TxCreate):
    tx_dict = tx    #.model_dump()
    st.write(f'Submitting tx data: {tx_dict}')
    response = httpx.post("http://localhost:8000/tx/", json=tx_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ Transaction submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit transaction. {response.status_code} | {response.text}')
    return False

def clear_session_state_and_rerun():
    # Delete all the items in Session state
    get_customers.clear()
    get_products.clear()
    ss.clear()
    st.rerun()

# Main function
def main_form():    #customers:List[Customer], merch:List[Product]):
    st.title('💵 Concessions Cash Register')

    # Select customer & Display customer details
    Customer_Section(ss.customers)
    st.divider()

    # Item hotbuttons   
    Items_Section(ss.merch)
    st.divider()

    #Display cart and register details
    tx_saved = Register_Section()
    if tx_saved:            
        #Reset the form
        with st.spinner("Loading..."):
            time.sleep(1)
        # Reload the page
        clear_session_state_and_rerun()



if __name__ == "__main__":
    # Get items from the database
    ss.customers = get_customers()
    ss.merch = get_products()
    main_form()

'''Fixes needed:
X 1. Fix floating error on Acct Balance
2. Reset all elements during st.rerun (dump session state)'''

'''Ideas:
XX 0. Hot Buttons / Cards
0. SET FOCUS TO PERSON
XX Lookup by badge ID
1. Item lookup by SKU
XX 2. Multipage (admin area?)
XX 2a. Merch management
XX 2b. Customer management
2c. **How to add cash to someone's account (AddFunds Tx type?)
2d. Checkout
1. Recent transactions - opportunity to do a refund?
_. User sign-in (Admin)?  Register ID?
FLAG ALLERGIES?
TILL Information - (Till# (MacAddress?), Cashier name, Cash In/Out, Tx List)
SETTINGS - allow_price_edits, allow_discounts
LOGS - API log, UI log, DB log?
TESTING - Mock API response
'''



