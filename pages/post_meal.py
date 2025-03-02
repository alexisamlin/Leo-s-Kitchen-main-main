# pages/post_meal.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Page configuration (keep existing code)
st.set_page_config(page_title="Share Your Meal - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION --- (keep existing code)
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")

# Initialize session state for meals if not exists
if 'user_meals' not in st.session_state:
    st.session_state.user_meals = []

# Function to save meal to database
def save_meal_to_db(meal_data):
    try:
        # In a real app, you would connect to your database
        # For now, we'll store in session state
        meal_data['id'] = len(st.session_state.user_meals) + 1
        meal_data['date_posted'] = datetime.now().strftime("%b %d, %Y")
        meal_data['likes'] = 0
        meal_data['comments'] = 0
        st.session_state.user_meals.append(meal_data)
        return True
    except Exception as e:
        st.error(f"Error saving meal: {e}")
        return False

# Function to delete a meal
def delete_meal(meal_id):
    try:
        # In a real app, you would delete from your database
        # For now, we'll delete from session state
        st.session_state.user_meals = [
            meal for meal in st.session_state.user_meals 
            if meal['id'] != meal_id
        ]
        return True
    except Exception as e:
        st.error(f"Error deleting meal: {e}")
        return False

# Handle query parameters for delete action
query_params = st.experimental_get_query_params()
if 'delete' in query_params:
    meal_id = int(query_params['delete'][0])
    if delete_meal(meal_id):
        st.success("Meal deleted successfully!")
        # Clear query parameters after processing
        st.experimental_set_query_params()

# --- SHARE MEAL FORM --- (Keep existing form code)
st.title("Share Your Meal 📝")
st.write("Fill out the form below to share your meal with the community!")

with st.form("meal_form"):
    # Basic meal information
    col1, col2 = st.columns(2)
    
    with col1:
        meal_name = st.text_input("Meal Name", placeholder="e.g., Protein-Packed Breakfast Bowl")
        meal_category = st.selectbox("Category", ["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"])
        meal_tags = st.text_input("Tags (comma separated)", placeholder="e.g., high-protein, keto, vegan")
    
    with col2:
        meal_description = st.text_area("Description", placeholder="Describe your meal in a few sentences...")
        recipe_url = st.text_input("Recipe URL (optional)", placeholder="Link to full recipe if available")
    
    # Image upload
    st.subheader("Meal Image")
    uploaded_image = st.file_uploader("Upload an image of your meal", type=["jpg", "jpeg", "png"])
    
    # Show a preview if image is uploaded
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Image Preview", use_column_width=True)
    
    # Nutrition information
    st.subheader("Nutrition Information")
    
    macro_col1, macro_col2, macro_col3, macro_col4 = st.columns(4)
    
    with macro_col1:
        protein = st.number_input("Protein (g)", min_value=0, value=20)
    
    with macro_col2:
        carbs = st.number_input("Carbs (g)", min_value=0, value=30)
    
    with macro_col3:
        fat = st.number_input("Fat (g)", min_value=0, value=10)
    
    with macro_col4:
        calories = st.number_input("Calories", min_value=0, value=protein*4 + carbs*4 + fat*9)
    
    # Additional macros (collapsible)
    with st.expander("Additional Nutrition Info (Optional)"):
        add_col1, add_col2, add_col3 = st.columns(3)
        
        with add_col1:
            fiber = st.number_input("Fiber (g)", min_value=0, value=0)
            sugar = st.number_input("Sugar (g)", min_value=0, value=0)
        
        with add_col2:
            sodium = st.number_input("Sodium (mg)", min_value=0, value=0)
            cholesterol = st.number_input("Cholesterol (mg)", min_value=0, value=0)
        
        with add_col3:
            saturated_fat = st.number_input("Saturated Fat (g)", min_value=0, value=0)
            trans_fat = st.number_input("Trans Fat (g)", min_value=0, value=0)
    
    # Ingredients and Instructions
    st.subheader("Ingredients")
    ingredients = st.text_area("List your ingredients (one per line)", height=150, 
                               placeholder="1 cup oats\n2 scoops protein powder\n1 tbsp peanut butter")
    
    st.subheader("Instructions")
    instructions = st.text_area("Recipe instructions", height=150,
                                placeholder="1. Mix oats and protein powder\n2. Add water and microwave for 2 minutes\n3. Top with peanut butter")
    
    # Submit button
    submitted = st.form_submit_button("Share Your Meal")

if submitted:
    # Calculate actual calories from macros
    calculated_calories = protein * 4 + carbs * 4 + fat * 9
    
    # Prepare meal data
    meal_data = {
        "name": meal_name,
        "category": meal_category,
        "tags": meal_tags,
        "description": meal_description,
        "recipe_url": recipe_url,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "calories": calories,
        "fiber": fiber,
        "sugar": sugar,
        "sodium": sodium,
        "cholesterol": cholesterol,
        "saturated_fat": saturated_fat,
        "trans_fat": trans_fat,
        "ingredients": ingredients,
        "instructions": instructions,
        # In a real app, you would save the image to storage and store the URL
        "image": "https://api.placeholder.com/400/300" if uploaded_image is None else "uploaded_image"
    }
    
    # Save to database
    if save_meal_to_db(meal_data):
        # Success message
        st.success("Your meal has been shared successfully!")
        
        # Show a preview of how it will appear in the feed
        st.subheader("Preview:")
        
        preview_col1, preview_col2 = st.columns([1, 2])
        
        with preview_col1:
            if uploaded_image is not None:
                st.image(uploaded_image, use_column_width=True)
            else:
                st.image("https://api.placeholder.com/400/300", use_column_width=True)
        
        with preview_col2:
            st.markdown(f"### {meal_name}")
            st.markdown(f"**Category:** {meal_category}")
            st.markdown(f"**Description:** {meal_description}")
            
            st.markdown("#### Nutrition Facts")
            st.markdown(f"**Protein:** {protein}g | **Carbs:** {carbs}g | **Fat:** {fat}g | **Calories:** {calories}")
            
            if recipe_url:
                st.markdown(f"[View Full Recipe]({recipe_url})")