import streamlit as st
import pandas as pd
import os
import hashlib
USER_FILE = "data/users.csv"
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
def init_user_store():
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(USER_FILE):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv(USER_FILE, index=False)
def load_users():
    init_user_store()
    return pd.read_csv(USER_FILE)
def save_user(username, password):
    users = load_users()
    hashed = hash_password(password)
    users.loc[len(users)] = [username, hashed]
    users.to_csv(USER_FILE, index=False)
def login():
    if "user" in st.session_state:
        return

    # Center the login form
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.markdown('<div class="main-header">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Please sign in to continue</div>', unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Login", "Register"])
        with tab_login:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")

            if st.button("Login", use_container_width=True):
                users = load_users()
                hashed = hash_password(password)

                valid = (
                    (users["username"] == username) &
                    (users["password"] == hashed)
                ).any()

                if valid:
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")

        with tab_register:
            new_user = st.text_input("Choose Username", key="reg_user")
            new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Register", use_container_width=True):
                users = load_users()

                if new_user.strip() == "":
                    st.error("Username cannot be empty")
                elif new_user in users["username"].values:
                    st.error("Username already exists")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters")
                elif new_pass != confirm:
                    st.error("Passwords do not match")
                else:
                    save_user(new_user, new_pass)
                    st.success("🎉 Registration successful. Please login.")