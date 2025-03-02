# pages/Share_Your_Meal.py
import streamlit as st
import pandas as pd
import os
from PIL import Image
import io

# Page configuration
st.set_page_config(page_title="Share Your Meal - Leo's Food App", page_icon="🐱", layout="wide")
st.logo(image="images/logo.png", size="large", link=None, icon_image=None)
# --- SIDEBAR NAVIGATION ---
# st.sidebar.title("Navigation")
# st.sidebar.page_link("Home.py", label="🏠 Home", icon="🏠")
# st.sidebar.page_link("pages/About_Leo's_Kitchen.py", label="ℹ️ About Me")
# st.sidebar.page_link("pages/My_Recipe.py", label="📊 My Recipes")
# st.sidebar.page_link("pages/Leo_Chat_Bot.py", label="🤖 Chat Bot")
# st.sidebar.page_link("pages/Share_Your_Meal.py", label="📝 Share Your Meal")

# --- SHARE MEAL FORM ---
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
    
    # Create a dictionary with meal data
    meal_data = {
        "meal_name": meal_name,
        "meal_category": meal_category,
        "meal_tags": meal_tags,
        "meal_description": meal_description,
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
        "datetime": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save image if uploaded
    image_path = None
    if uploaded_image is not None:
        # Create images directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        
        # Generate unique filename
        image_filename = f"meal_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image_path = os.path.join("images", image_filename)
        
        # Save the image
        image = Image.open(uploaded_image)
        image.save(image_path)
        
        # Add image path to meal data
        meal_data["image_path"] = image_path
    
    # Load existing meals or create new dataframe
    try:
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        if os.path.exists("data/meals.csv"):
            meals_df = pd.read_csv("data/meals.csv")
        else:
            meals_df = pd.DataFrame()
    except (FileNotFoundError, pd.errors.EmptyDataError):
        meals_df = pd.DataFrame()
    
    # Append new meal
    new_meal_df = pd.DataFrame([meal_data])
    meals_df = pd.concat([meals_df, new_meal_df], ignore_index=True)
    
    # Save to CSV
    meals_df.to_csv("data/meals.csv", index=False)

    # After saving to CSV in Share_Your_Meal.py, modify the code after the success message

    # Add to session state for My_Profile.py to use
    if 'user_meals' not in st.session_state:
        st.session_state.user_meals = []

    # Create a meal entry in the format expected by My_Profile.py
    new_meal_entry = {
        "id": len(st.session_state.user_meals) + 1 if 'user_meals' in st.session_state else 1,
        "name": meal_name,
        "date_posted": pd.Timestamp.now().strftime("%b %d, %Y"),
        "likes": 0,
        "comments": 0,
        "image": image_path if image_path else "https://api.placeholder.com/300/200"
    }

    # Add to session state
    st.session_state.user_meals.append(new_meal_entry)

    # Remove the auto-redirect that's causing the logout
    # Delete or comment out these lines:
    # st.markdown("""
    # <meta http-equiv="refresh" content="3;URL='/'">
    # """, unsafe_allow_html=True)

    # Replace with a direct button
    if st.button("Go to My Profile"):
        st.switch_page("pages/My_Profile.py")

    # After saving to CSV in Share_Your_Meal.py, add this code:
    if 'user_meals' not in st.session_state:
        st.session_state.user_meals = []

    # Create a meal entry in the format expected by My_Profile.py
    new_meal_entry = {
        "id": len(st.session_state.user_meals) + 1,
        "name": meal_name,
        "date_posted": pd.Timestamp.now().strftime("%b %d, %Y"),
        "likes": 0,
        "comments": 0,
        "image": image_path if image_path else "https://api.placeholder.com/300/200"
    }

    # Add to session state
    st.session_state.user_meals.append(new_meal_entry)

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
    
    # Automatically redirect to home page after a few seconds
    st.markdown("""
    <meta http-equiv="refresh" content="3;URL='/'">
    """, unsafe_allow_html=True)
    
    if st.button("Go to Home Page Now"):
        st.switch_page("Home.py")
