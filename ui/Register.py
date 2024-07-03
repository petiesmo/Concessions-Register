#streamlit/Register.py
'''Concession Register - Transaction input form
    Interacts with the API (not the database directly)'''

import time
from typing import List

import httpx
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Concessions Cash Register",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="collapsed"    #, menu_items=[]
    )
ss = st.session_state


def cbk():
    '''Workaround to help set focus on the customer dropdown'''
    st.session_state['counter'] += 1

if 'counter' not in st.session_state:
    st.session_state['counter'] = 0
 
# Helper functions to fetch customers from the database
@st.cache_data
def get_customers() -> List[dict]:
    res = httpx.get('http://fastapi_service:8000/customers/all')
    if res.status_code == 200:
        return res.json()   #[Customer(**x) for x in res.json()]
    return {'Error':'No customers retrieved'}


# Helper function to fetch items from the database
@st.cache_data
def get_products() -> List[dict]:
    res = httpx.get('http://fastapi_service:8000/products/all')
    if res.status_code == 200:
        return res.json()   #[Product(**x) for x in res.json()]
    return {'Error':'No products retrieved'}


# Customer Selection
def format_customer(cst):
    return f"{cst['badge_id']} | {cst['name']}"

def select_customer(customers):
    # Select customer from database list (searchable)
    selected_customer = st.selectbox(
        label="Customer (type to search)",
        key="session_customer",
        options=customers,
        index=None,
        placeholder='Select/Search a Customer',
        format_func=format_customer,
        on_change=cbk)
    ss.customer = selected_customer
    return selected_customer

def Customer_Section(customers):
    colA, colB = st.columns(2, gap='medium')
    with colA:
        selected_customer = select_customer(customers)
    with colB:
        if selected_customer:
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
            if cst: projected_balance = cst['acct_balance'] - payment['account']
        with col2b:
            tx_note = st.text_input('Note')
            ss.tx_note = tx_note
            if cst: st.markdown(f"Projected Balance: ${formatted_balance(projected_balance)}")
    

    tx_saved = False
    if cst and total > 0:
        if sum(payment.values()) == total:
            #TODO: Allow negative balance for staff
            if total > cst['acct_balance']:
                col2b.write("Insufficient Account Balance.  Add cash or reduce items.")
            else:
                if col2b.button("Submit"):
                    #Should map to TxCreate
                    tx_data = {         
                    'customer_id': cst['id'],
                    'txtype': 1,
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
    response = httpx.post("http://fastapi_service:8000/tx/", json=tx_dict)
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

    components.html(
        f"""
            <div></div>
            <p style="color:white;">{st.session_state.counter}</p>
            <script>
                var input = window.parent.document.querySelectorAll("input[role=combobox]");

                for (var i = 0; i < input.length; ++i) {{
                    input[i].focus();
                }}
        </script>
        """,
        height=150
    )


if __name__ == "__main__":
    # Get items from the database
    ss.customers = get_customers()
    ss.merch = get_products()
    main_form()


