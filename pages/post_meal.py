# pages/post_meal.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
import uuid
from utils.sidebar import create_sidebar_navigation

# Page configuration
st.set_page_config(page_title="Share Your Meal - Leo's Food App", page_icon="🐱", layout="wide")

# Create sidebar navigation
sidebar = create_sidebar_navigation("pages/post_meal.py")

# Check authentication status
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.warning("Please log in to share meals")
    if st.button("Go to Login"):
        st.switch_page("pages/auth.py")
else:
    # Initialize database
    def init_db():
        # Make sure the data directory exists
        if not os.path.exists("data"):
            os.makedirs("data")
            
        conn = sqlite3.connect('data/food_app.db')
        c = conn.cursor()
        
        # Create meals table if it doesn't exist
        c.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            tags TEXT,
            description TEXT,
            recipe_url TEXT,
            protein INTEGER,
            carbs INTEGER,
            fat INTEGER,
            calories INTEGER,
            fiber INTEGER,
            sugar INTEGER,
            sodium INTEGER,
            cholesterol INTEGER,
            saturated_fat REAL,
            trans_fat REAL,
            ingredients TEXT,
            instructions TEXT,
            image_path TEXT,
            date_posted TIMESTAMP,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0
        )
        ''')
        
        conn.commit()
        conn.close()

    # Initialize the database
    init_db()

    # Function to save meal to database
    def save_meal_to_db(meal_data):
        try:
            conn = sqlite3.connect('data/food_app.db')
            c = conn.cursor()
            
            # Generate a unique ID for the meal
            meal_id = str(uuid.uuid4())
            
            # Insert the meal data into the database
            c.execute('''
            INSERT INTO meals (
                id, user_id, username, name, category, tags, description, recipe_url,
                protein, carbs, fat, calories, fiber, sugar, sodium, cholesterol,
                saturated_fat, trans_fat, ingredients, instructions, image_path, date_posted,
                likes, comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                meal_id,
                st.session_state.user_id,
                st.session_state.username,
                meal_data['name'],
                meal_data['category'],
                meal_data['tags'],
                meal_data['description'],
                meal_data['recipe_url'],
                meal_data['protein'],
                meal_data['carbs'],
                meal_data['fat'],
                meal_data['calories'],
                meal_data['fiber'],
                meal_data['sugar'],
                meal_data['sodium'],
                meal_data['cholesterol'],
                meal_data['saturated_fat'],
                meal_data['trans_fat'],
                meal_data['ingredients'],
                meal_data['instructions'],
                meal_data['image_path'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                0,  # likes
                0   # comments
            ))
            
            conn.commit()
            conn.close()
            
            # Update the session state if needed
            if 'user_meals' not in st.session_state:
                st.session_state.user_meals = []
                
            # Add the meal to the session state
            meal_data['id'] = meal_id
            meal_data['date_posted'] = datetime.now().strftime("%b %d, %Y")
            meal_data['likes'] = 0
            meal_data['comments'] = 0
            st.session_state.user_meals.append(meal_data)
            
            return True, meal_id
        except Exception as e:
            st.error(f"Error saving meal: {e}")
            return False, None

    # Function to save uploaded image
    def save_uploaded_image(uploaded_file):
        if uploaded_file is None:
            return "https://api.placeholder.com/400/300"
            
        # Create a directory for storing images if it doesn't exist
        if not os.path.exists("data/images"):
            os.makedirs("data/images")
            
        # Generate a unique filename
        file_extension = os.path.splitext(uploaded_file.name)[1]
        filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join("data/images", filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path

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
        # Validate required fields
        if not meal_name:
            st.error("Please enter a meal name")
        elif not meal_description:
            st.error("Please enter a meal description")
        elif not ingredients:
            st.error("Please enter ingredients")
        elif not instructions:
            st.error("Please enter instructions")
        else:
            # Calculate actual calories from macros if not manually set
            calculated_calories = protein * 4 + carbs * 4 + fat * 9
            if calories == 0:
                calories = calculated_calories
                
            # Save the uploaded image
            image_path = save_uploaded_image(uploaded_image)
                
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
                "image_path": image_path
            }
            
            # Save to database
            success, meal_id = save_meal_to_db(meal_data)
            
            if success:
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
                        
                # Add buttons to view the meal or return to home
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Your Recipe"):
                        st.switch_page(f"pages/recipe_detail.py?id={meal_id}")
                with col2:
                    if st.button("Return to Home"):
                        st.switch_page("app.py")