import streamlit as st
import pandas as pd
import os
# --- File paths ---
USERS_FILE = "login_file.xlsx"
SERVICES_FILE = "model_price.xlsx"
USER_SERVICES_FILE = "user_services.xlsx"


# --- Load users ---
def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_excel(USERS_FILE)
    else:
        return pd.DataFrame(columns=["user_id", "password"])


# --- Save new user ---
def save_user(username, password):
    users = load_users()
    if username in users["user_id"].values:
        return False
    new_user = pd.DataFrame([[username, password]], columns=["user_id", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_excel(USERS_FILE, index=False)
    return True


# --- Save selected service ---
def save_user_service(username, model, vas, price):
    if os.path.exists(USER_SERVICES_FILE):
        user_services = pd.read_excel(USER_SERVICES_FILE)
    else:
        user_services = pd.DataFrame(columns=["user_id", "Model", "VAS", "Price"])

    new_entry = pd.DataFrame([[username, model, vas, price]], columns=["user_id", "Model", "VAS", "Price"])
    user_services = pd.concat([user_services, new_entry], ignore_index=True)
    user_services.to_excel(USER_SERVICES_FILE, index=False)


# --- Load services ---
def load_services():
    if os.path.exists(SERVICES_FILE):
        return pd.read_excel(SERVICES_FILE)
    else:
        st.error("Service file not found!")
        return pd.DataFrame(columns=["Unique ID", "Model", "VAS", "Price"])


services_df = load_services()

# --- Streamlit app ---
st.title("🔑 Login & Registration")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# --- Login ---
if choice == "Login":
    st.subheader("Login Section")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        user = users[(users["user_id"] == username) & (users["password"] == password)]
        if not user.empty:
            st.success(f"✅ Welcome {username}!")
            st.session_state["current_user"] = username  # store logged-in user
        else:
            st.error("❌ Invalid username or password")

# --- Register ---
elif choice == "Register":
    st.subheader("Create a New Account")
    new_username = st.text_input("Enter new username", key="reg_user")
    new_password = st.text_input("Enter new password", type="password", key="reg_pass")

    if st.button("Register", key="register_btn"):
        if new_username and new_password:
            if save_user(new_username, new_password):
                st.success("🎉 Registration successful!")
                st.session_state["current_user"] = new_username  # store logged-in user
            else:
                st.error("⚠️ Username already exists.")
        else:
            st.error("⚠️ Please fill in both fields.")

# --- Service selection for logged-in users ---
if st.session_state.get("current_user"):
    st.subheader("🚗 Select Your Service")

    # Select car model dynamically
    models = services_df["Model"].unique().tolist()
    selected_model = st.selectbox("Select Car Model", models, key="car_model")

    # Filter VAS based on selected model
    vas_options = services_df[services_df["Model"] == selected_model]["VAS"].tolist()
    selected_vas = st.selectbox("Select Service (VAS)", vas_options, key="vas")

    # Get price
    price = \
    services_df[(services_df["Model"] == selected_model) & (services_df["VAS"] == selected_vas)]["Price"].values[0]
    st.info(f"💰 Price for selected service: ₹{price}")

    if st.button("Confirm & Save Service", key="save_service_btn"):
        save_user_service(st.session_state["current_user"], selected_model, selected_vas, price)
        st.success("✅ Service saved successfully!")

