"""
Pharmacy Medicine Bill Calculator
Course: Python Programming for Business Students
Run with:  streamlit run app.py
"""

import streamlit as st
from datetime import datetime

# ---------------------------------------------------------------
# 1. DATA: medicine catalogue (dictionary: name -> details)
#    price is float, needs_rx is bool (prescription required?)
# ---------------------------------------------------------------
MEDICINES = {
    "Paracetamol 500mg (strip of 10)": {"price": 30.0, "needs_rx": False},
    "Cough Syrup 100ml": {"price": 95.0, "needs_rx": False},
    "Vitamin C Tablets (strip of 15)": {"price": 120.0, "needs_rx": False},
    "ORS Sachets (pack of 5)": {"price": 40.0, "needs_rx": False},
    "Antacid Gel 170ml": {"price": 60.0, "needs_rx": False},
    "Amoxicillin 500mg (strip of 10)": {"price": 120.0, "needs_rx": True},
    "Azithromycin 500mg (strip of 3)": {"price": 150.0, "needs_rx": True},
}

# Business rules stored as constants so they are easy to change
GST_RATE = 0.05              # 5% GST on medicines (assumed rate)
SENIOR_DISCOUNT = 10         # 10% discount for senior citizens
BULK_DISCOUNT = 5            # extra 5% if subtotal >= 1000
BULK_LIMIT = 1000.0
FREE_DELIVERY_LIMIT = 500.0  # free home delivery above this amount
DELIVERY_FEE = 40.0
MAX_QTY = 50                 # maximum quantity allowed per medicine
NUM_SLOTS = 3                # number of medicines in one order


# ---------------------------------------------------------------
# 2. FUNCTION: core business calculation
# ---------------------------------------------------------------
def calculate_bill(cart, is_senior, home_delivery):
    """Takes the cart (list of dicts) and returns all bill amounts."""
    subtotal = 0.0

    # Loop through every item and add price x quantity
    for item in cart:
        subtotal += item["price"] * item["qty"]

    # Conditional logic: work out the total discount percentage
    discount_pct = 0
    if is_senior:
        discount_pct += SENIOR_DISCOUNT
    if subtotal >= BULK_LIMIT:
        discount_pct += BULK_DISCOUNT

    discount_amt = subtotal * discount_pct / 100
    after_discount = subtotal - discount_amt

    # GST is charged on the discounted amount
    gst = after_discount * GST_RATE

    # Delivery charge: free for big orders, flat fee for small ones
    if home_delivery:
        if after_discount >= FREE_DELIVERY_LIMIT:
            delivery = 0.0
        else:
            delivery = DELIVERY_FEE
    else:
        delivery = 0.0

    total = after_discount + gst + delivery

    return {
        "subtotal": subtotal,
        "discount_pct": discount_pct,
        "discount_amt": discount_amt,
        "gst": gst,
        "delivery": delivery,
        "total": total,
    }


# ---------------------------------------------------------------
# 3. USER INTERFACE (Streamlit)
# ---------------------------------------------------------------
st.set_page_config(page_title="Pharmacy Bill Calculator", page_icon="💊")
st.title("💊 Pharmacy Medicine Bill Calculator")
st.write("Select medicines, enter quantities and generate your bill.")

# Input 1: customer name (str)
customer_name = st.text_input("Customer name")

# Input 2: payment method (str from a fixed list)
payment = st.selectbox("Payment method", ["Cash", "UPI", "Card"])

# Inputs 3 & 4: checkboxes (bool values)
is_senior = st.checkbox("Senior citizen (60+ years)")
home_delivery = st.checkbox("Home delivery")

# Input 5: prescription confirmation (bool)
has_rx = st.checkbox("I have a valid doctor's prescription")

st.subheader("Choose your medicines")

# Inputs 6+: medicine selectbox + quantity, repeated using a loop
selections = []
for i in range(NUM_SLOTS):
    col1, col2 = st.columns([3, 1])
    with col1:
        med = st.selectbox(
            f"Medicine {i + 1}",
            ["-- None --"] + list(MEDICINES.keys()),
            key=f"med_{i}",
        )
    with col2:
        # min_value=0 stops negative numbers from being typed
        qty = st.number_input(
            "Qty", min_value=0, max_value=MAX_QTY, value=0, step=1, key=f"qty_{i}"
        )
    selections.append((med, int(qty)))

# ---------------------------------------------------------------
# 4. BILL GENERATION with validation and error handling
# ---------------------------------------------------------------
if st.button("Generate Bill"):
    try:
        cart = []
        needs_prescription = False

        # Build the cart only from valid rows (medicine chosen and qty > 0)
        for med, qty in selections:
            if med != "-- None --" and qty > 0:
                info = MEDICINES[med]
                cart.append({"name": med, "price": info["price"], "qty": qty})
                if info["needs_rx"]:
                    needs_prescription = True

        # Validation checks (each one stops the bill with a clear message)
        if customer_name.strip() == "":
            st.error("Please enter the customer name.")
        elif len(cart) == 0:
            st.warning("Please select at least one medicine with quantity 1 or more.")
        elif needs_prescription and not has_rx:
            st.error("Your cart has prescription-only medicine. "
                     "Please confirm you have a valid prescription.")
        else:
            bill = calculate_bill(cart, is_senior, home_delivery)

            # Display the bill
            st.success("Bill generated successfully!")
            st.write(f"**Customer:** {customer_name.strip()}")
            st.write(f"**Date:** {datetime.now().strftime('%d-%m-%Y %H:%M')}")
            st.write(f"**Payment:** {payment}")

            # Item-wise table
            rows = []
            for item in cart:
                rows.append({
                    "Medicine": item["name"],
                    "Price (₹)": f"{item['price']:.2f}",
                    "Qty": item["qty"],
                    "Amount (₹)": f"{item['price'] * item['qty']:.2f}",
                })
            st.table(rows)

            st.write(f"Subtotal: ₹{bill['subtotal']:.2f}")
            st.write(f"Discount ({bill['discount_pct']}%): -₹{bill['discount_amt']:.2f}")
            st.write(f"GST ({int(GST_RATE * 100)}%): ₹{bill['gst']:.2f}")
            st.write(f"Delivery charge: ₹{bill['delivery']:.2f}")
            st.metric("Total Payable", f"₹{bill['total']:.2f}")

            if bill["discount_pct"] > 0:
                st.info(f"You saved ₹{bill['discount_amt']:.2f} on this order.")

    except Exception as e:
        # Safety net so the app never crashes
        st.error(f"Something went wrong: {e}")
