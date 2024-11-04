from copy import deepcopy
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

def get_one_customer(cst_id):
    res = httpx.get(f'http://fastapi_service:8000/customers/{cst_id}')
    if res.status_code == 200:
        return res.json()
    return [{'Error':f'Id {cst_id} not retrieved'}]

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

    with st.form('fm_review_account_actions', clear_on_submit=True, border=True):
        updates = list()
        if reason == "Cash In/Out":		#0 = Cash in/out
            tx_data.update({'txtype':2})
            cbox_data = deepcopy(tx_data)
            cbox_data.update({'customer_id':2}) #Cash Box = 2
            updates.append(tx_data)
            updates.append(cbox_data)
        else:
            tx_data.update({'txtype':3})
            updates.append(tx_data)
        st.write("To Update: ")
        updates
        if st.form_submit_button('Make Adjustment'):
            for udata in updates:
                save_transaction(udata)
            clear_session_state_and_rerun()
    return 
   #Payment(cash=cash, coupon=coupon, account=acct)

def closing_options(group_total:float) -> dict:  #Payment:
    cash_in = st.number_input("Cash Paid (from customer)", min_value=0.00, value=0.00)
    cash_back = st.number_input("Cash Back (to customer)", min_value=0.00, value=0.00)
    to_donate = st.number_input("Donate (to camp)", min_value=0.00, value=0.00)
    from_donations = st.number_input("From Donations (to customer)", min_value=0.00, value=0.00)
    cst_adj_total = cash_in-cash_back+from_donations-to_donate
    st.write(f'Customer Adjustment Total: ${cst_adj_total:.2f}')
    st.write(f'Difference: ${cst_adj_total+group_total:.2f}')
    return {'net_cash':cash_in-cash_back,
            'net_donate':to_donate-from_donations,
            'net_total':cst_adj_total}
   #Payment(cash=cash, coupon=coupon, account=acct)

# Closeout each person in record
def save_transaction(tx): #TxCreate):
    tx_dict = tx    
    st.write(f'Submitting tx data: {tx_dict}')
    response = httpx.post(f"http://fastapi_service:8000/tx/", json=tx_dict)
    st.write(f'Server response: {response.json()}')
    if response.status_code == 201:
        st.toast(f'✅ Transaction submitted successfully!')
        return True
    st.toast(f'❌ Failed to submit transaction. {response.status_code} | {response.text}')
    return False

def closeout_customer(cst_id):
    st.write(f'Closing out customer {cst_id}')
    response = httpx.patch(f"http://fastapi_service:8000/customers/closeout/{cst_id}")
    st.write(f'Server response: {response.json()}')
    if response.status_code in [200,201]:
        st.toast(f'✅ Customer Closed out successfully!')
        return True
    st.toast(f'❌ Failed to closeout customer. {response.status_code} | {response.text}')
    return False

def formatted_balance(bal):
    if bal > 0:
        return f"""$***{bal:.2f}*** - Cash Back (or Donate) ✅"""
    else:
        return f"""$***{bal:.2f}*** - Cash Needed ❌"""
    
# Main function
def main_form():
    st.title('💵 Account Closeout')
    col1,col2 = st.columns(2)
    with col1.popover('Manual Acct Adjust'):
        line_item = manual_adjust_form()
    if col2.button('RESET'): clear_session_state_and_rerun()

    st.divider()
    ss.cst_group = select_customers(ss.customers)
    
    st.divider()

    "Selected Customers Details:"
    if ss.cst_group:
        df_group = pd.DataFrame(ss.cst_group)
        df_group
        group_total = round((df_group.acct_balance).sum(),2)
        st.write(f"Group Total: {formatted_balance(group_total)}")
    
        with st.expander('Transactions Details (click to expand)'):
            combined_tx =  list()
            for cst in ss.cst_group:
                cst_detail = get_one_customer(cst['id'])
                combined_tx.extend(cst_detail['transactions'])
            df_tx_detail = pd.DataFrame(combined_tx)
            df_tx_detail['cart2'] = df_tx_detail['cart'].apply(lambda cart: ' | '.join([i['name'] for i in cart]))
            st.dataframe(df_tx_detail[['id','customer_id','total','note','cart2']], use_container_width=True)

        form1 = st.form('fm_balance_options', clear_on_submit=True, border=True)
        with form1:
            ss.net_action = closing_options(group_total)
            note = st.text_input("Reason", value='')

            if st.form_submit_button('Review Account Actions'):
                pass

        form2 = st.form('fm_review_account_actions2', clear_on_submit=True, border=True)
        with form2:
            st.write("To Update: ")
            delta_customers = {cid:abal for cid,abal in df_group[['id','acct_balance']].itertuples(index=False)}
            net_donation = ss.net_action.get('net_donate',0)
            pmt_donation = {'account':net_donation}
            net_cash = ss.net_action.get('net_cash',0)
            pmt_cash = {'account':net_cash}
            account_actions = list()
            for cid,abal in delta_customers.items():
                #Adjust each customer in the group to acct_balance 0
                account_actions.append ({         
                'customer_id': cid,
                'txtype': 4,	#4=Closeout
                'total': -abal,
                'pmt': {'account': -abal},
                'note': f'Closeout | {note}'
                })
            #Record closeout in donations (id=1) and cashbox in/out (id=2)
            if net_donation != 0:
                account_actions.append ({         
                'customer_id': 1,
                'txtype':3,
                'total': net_donation,
                'pmt': pmt_donation,
                'note': f"Closeout | {note} | Cash In/Out: {net_cash} | Donated: {net_donation} | ids: {list(delta_customers.keys())}"
                })
            if net_cash != 0:
                account_actions.append ({         
                'customer_id': 2,
                'txtype':2,
                'total': net_cash,
                'pmt': pmt_cash,
                'note': f"Closeout | {note} | Cash In/Out: {net_cash} | Donated: {net_donation} | ids: {list(delta_customers.keys())}"
                })

            account_actions
            if st.form_submit_button('Submit Account Actions'):
                for aa in account_actions:
                    save_transaction(aa)
                for cid in delta_customers.keys():
                    closeout_customer(cid)

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
X Update Customer(s) to 'Active' = False

Bonus: 
Update "Till" (Cash in/out & Donations in/out)
'''
