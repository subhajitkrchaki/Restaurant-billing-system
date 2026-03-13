# restaurant_billing.py
import csv
import io

import streamlit as st

MENU = {
    "Burger": 80.0,
    "Pizza": 180.0,
    "Fries": 50.0,
    "Cola": 25.0,
    "Ice Cream": 60.0,
}


def reset_cart() -> None:
    for item in MENU:
        st.session_state[f"qty_{item}"] = 0
    st.session_state["tax_percent"] = 5

st.set_page_config(page_title="Restaurant Billing", layout="centered")

st.markdown(
    """
    <style>
    :root {
        --bg-top: #fff8e8;
        --bg-bottom: #e9f5ff;
        --card-bg: #ffffff;
        --text-main: #1b263b;
        --text-muted: #415a77;
        --accent: #d97706;
        --accent-2: #0ea5e9;
        --line: #dbe7f3;
    }
    .stApp {
        background: radial-gradient(circle at 15% 10%, #ffffff 0%, var(--bg-top) 45%, var(--bg-bottom) 100%);
        color: var(--text-main);
    }
    h1, h2, h3, p, label, div, span {
        color: var(--text-main) !important;
    }
    .title-card {
        background: linear-gradient(110deg, #ffffff 0%, #f7fbff 100%);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }
    .menu-header {
        color: var(--text-muted) !important;
        font-size: 0.95rem;
        margin-bottom: 8px;
    }
    .menu-row {
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
    }
    .totals-card {
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-left: 8px solid var(--accent);
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 12px;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }
    .totals-card b {
        color: var(--text-muted) !important;
    }
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius: 10px;
        border: none !important;
        background: linear-gradient(90deg, #d97706 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 10px 24px !important;
        width: 100%;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
        transition: 0.15s ease;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Restaurant Billing System")
st.markdown(
    """
    <div class="title-card">
        <div style="font-size:1.05rem; font-weight:700; margin-bottom: 4px;">Build your order in seconds</div>
        <div style="color:#415a77;">Select quantities, set tax, and generate an itemized bill with one click.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("Menu")
st.markdown("<div class='menu-header'>Choose quantity for each item</div>", unsafe_allow_html=True)

action_col1, action_col2 = st.columns([1, 1])
with action_col1:
    st.button("Reset Cart", on_click=reset_cart, use_container_width=True)
with action_col2:
    st.caption("Use Generate Bill after selecting quantities.")

with st.form("billing_form"):
    quantities = {}

    for item, price in MENU.items():
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            st.markdown(f"<div class='menu-row'><b>{item}</b></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='menu-row'>Rs {price:.2f}</div>", unsafe_allow_html=True)
        with col3:
            quantities[item] = st.number_input(
                f"Qty for {item}",
                min_value=0,
                step=1,
                value=0,
                key=f"qty_{item}",
                label_visibility="collapsed",
            )

    tax_percent = st.slider("Tax (%)", min_value=0, max_value=30, value=5, step=1, key="tax_percent")
    submitted = st.form_submit_button("Generate Bill")

if submitted:
    cart = {item: int(qty) for item, qty in quantities.items() if qty > 0}

    if not cart:
        st.warning("Please select at least one item.")
    else:
        subtotal = sum(MENU[item] * qty for item, qty in cart.items())
        tax_rate = tax_percent / 100
        tax = subtotal * tax_rate
        total = subtotal + tax

        st.subheader("Bill")
        bill_rows = []
        for item, qty in cart.items():
            line_total = MENU[item] * qty
            bill_rows.append(
                {
                    "Item": item,
                    "Unit Price": f"Rs {MENU[item]:.2f}",
                    "Qty": qty,
                    "Line Total": f"Rs {line_total:.2f}",
                }
            )

        st.table(bill_rows)

        st.markdown(
            f"""
            <div class="totals-card">
                <b>Subtotal:</b> Rs {subtotal:.2f}<br>
                <b>Tax ({tax_percent}%):</b> Rs {tax:.2f}<br>
                <b>Total:</b> Rs {total:.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Unit Price", "Quantity", "Line Total"])
        for item, qty in cart.items():
            writer.writerow([item, f"{MENU[item]:.2f}", qty, f"{MENU[item] * qty:.2f}"])
        writer.writerow([])
        writer.writerow(["Subtotal", f"{subtotal:.2f}"])
        writer.writerow([f"Tax ({tax_percent}%)", f"{tax:.2f}"])
        writer.writerow(["Total", f"{total:.2f}"])

        st.download_button(
            label="Download Bill as CSV",
            data=output.getvalue(),
            file_name="restaurant_bill.csv",
            mime="text/csv",
            use_container_width=True,
        )