# utils/sidebar.py
import streamlit as st

def create_sidebar_navigation(active_page=None):
    """
    Creates consistent sidebar navigation across all pages
    
    Parameters:
    active_page (str): The current active page to highlight (optional)
    """
    st.sidebar.title("Navigation")
    
    # Define all navigation items with their paths and labels
    nav_items = [
        {"path": "app.py", "label": "🏠 Home", "icon": "🏠"},
        {"path": "pages/about_me.py", "label": "ℹ️ About Me"},
        {"path": "pages/my_recipes.py", "label": "📊 My Recipes"},
        {"path": "pages/chatbot.py", "label": "🤖 Chat Bot"},
        {"path": "pages/post_meal.py", "label": "📝 Share Your Meal"}
    ]
    
    # Display main navigation items
    for item in nav_items:
        if "icon" in item:
            st.sidebar.page_link(item["path"], label=item["label"], icon=item["icon"])
        else:
            st.sidebar.page_link(item["path"], label=item["label"])
    
    # Add authentication-related items
    st.sidebar.divider()
    
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        st.sidebar.subheader(f"Welcome, {st.session_state.username}")
        st.sidebar.page_link("pages/profile.py", label="👤 My Profile")
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.user_id = None
            st.rerun()
    else:
        st.sidebar.page_link("pages/auth.py", label="👤 Login/Register")
    
    return st.sidebar