import httpx
import pandas as pd
import streamlit as st
ss = st.session_state
ss.cst = None

# Helper functions to fetch customers from the database
@st.cache_data
def get_customers() -> list[dict]:
    res = httpx.get('http://fastapi_service:8000/customers/all')
    if res.status_code == 200:
        return res.json()   #[Customer(**x) for x in res.json()]
    return {'Error':'No customers retrieved'}

# Customer Selection
def cbk():
    pass

def format_customer(cst):
    return f"{cst['badge_id']} | {cst['name']}"

def select_customers(customers):
    # Select customer from database list (searchable)
    selected_customers = st.multiselect(
        label="Select Customer(s) (type to search)",
        key="session_customer",
        options=customers,
        placeholder='Select/Search a Customer',
        format_func=format_customer,
        on_change=cbk)
    return selected_customers

def manual_adjust_form() -> dict:  #Payment:
    with st.form('ManualAdj', clear_on_submit=True, border=True):
        customer = st.selectbox('Select Customer', ss.customers, format_func=format_customer)
        acct_adjust = st.number_input("Adjust Account +/-", value=0.00)
        reason = st.selectbox('Reason', ['Cash In/Out', 'Correction'])
        note = st.text_input("Manager Name & Note", value='')
    
        tx_data = {         
            'customer_id': customer['id'],
            'total': acct_adjust,
            'pmt': {'account': acct_adjust},
            'note': f'{reason} | {note}'
            }
        if st.form_submit_button('Review Account Actions'):
            pass

    form2 = st.form('fm_review_account_actions', clear_on_submit=True, border=True)
    with form2:
        st.write("To Update: ")
        tx_data
        if st.form_submit_button('Make Adjustment'):
            if reason == 0:
                tx_data.update({'txtype':2})
                save_transaction(tx_data)
            else:
                tx_data.update({'txtype':3})
                save_transaction(tx_data)
    return 
   #Payment(cash=cash, coupon=coupon, account=acct)

def closing_options(group_total:float) -> dict:  #Payment:
    cash_in = st.number_input("Cash Paid (from customer)", min_value=0.00, value=0.00)
    cash_back = st.number_input("Cash Back (to customer)", min_value=0.00, value=0.00)
    to_donate = st.number_input("Donate (to camp)", min_value=0.00, value=0.00)
    from_donations = st.number_input("From Donations (to customer)", min_value=0.00, value=0.00)
    adj_total = cash_in-cash_back+from_donations-to_donate
    st.write(f'Adjustment Total: ${adj_total:.2f}')
    st.write(f'Difference: ${group_total-adj_total:.2f}')
    return {'cash':cash_in-cash_back,
            'coupon':from_donations-to_donate,
            'account':adj_total}
   #Payment(cash=cash, coupon=coupon, account=acct)

# Closeout each person in record
def save_transaction(tx, txtype): #TxCreate):
    tx_dict = tx    
    st.write(f'Submitting tx data: {tx_dict}')
    response = httpx.post(f"http://fastapi_service:8000/tx/{txtype}", json=tx_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ Transaction submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit transaction. {response.status_code} | {response.text}')
    return False

def formatted_balance(bal):
    if bal > 0:
        return f"""$***{bal:.2f}*** - Cash Back (or Donate) ✅"""
    else:
        return f"""$***{bal:.2f}*** - Cash Needed ❌"""
    
# Main function
def main_form():
    st.title('💵 Account Closeout')
    with st.popover('Manual Acct Adjust'):
        line_item = manual_adjust_form()
    ss.cst = select_customers(ss.customers)
    
    st.divider()

    "Selected Customers Details:"
    if ss.cst:
        df = pd.DataFrame(ss.cst)
        df
        group_total = round((df.acct_balance).sum(),2)
        st.write(f"Group Total: {formatted_balance(group_total)}")
    
        form1 = st.form('fm_balance_options', clear_on_submit=True, border=True)
        with form1:
            account_action = closing_options(group_total)
            note = st.text_input("Reason", value='')

            if st.form_submit_button('Review Account Actions'):
                pass

        form2 = st.form('fm_review_account_actions', clear_on_submit=True, border=True)
        with form2:
            st.write("To Update: ")
            delta_customers = {cid:abal for cid,abal in df[['id','acct_balance']].itertuples(index=False)}
            
            account_actions = list()
            for cid,abal in delta_customers.items():
                account_actions.append ({         
                'customer_id': cid,
                'txtype': 3,
                'total': -abal,
                'pmt': {'account': -abal},
                'note': note
                })
            #Record closeout
            account_actions.append ({         
                'customer_id': 999,
                'txtype':3,
                'total': 0,
                'pmt': account_action,
                'note': f'{delta_customers.keys()}'
                })
            account_actions
            if st.form_submit_button('Review Account Actions'):
                for aa in account_actions:
                    save_transaction(aa)

    if st.button('RESET'): clear_session_state_and_rerun()


def clear_session_state_and_rerun():
    # Delete all the items in Session state
    get_customers.clear()
    ss.clear()
    st.rerun()

if __name__ == "__main__":
    # Get items from the database
    ss.customers = get_customers()
    main_form()


'''Vision:
X Customer Selector (SelectBox? dropdown? dataframe?)
Show Transactions (Dataframe?)
X Family/Group Total
X Reconciled Balance(Cash In/Out, Donate In/Out)

X Record Transaction 
X Update Customer(s) Balances to Zero
Update Customer(s) to 'Active' = False

Bonus: 
Update "Till" (Cash in/out & Donations in/out)
'''