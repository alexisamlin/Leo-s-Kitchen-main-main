import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from PIL import Image
import io
import uuid

# Page configuration
st.set_page_config(page_title="My Profile - Leo's Food App", page_icon="🐱", layout="wide")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/about_me.py", label="ℹ️ About Me")
st.sidebar.page_link("pages/my_recipes.py", label="📊 My Recipes")
st.sidebar.page_link("pages/chatbot.py", label="🤖 Chat Bot")
st.sidebar.page_link("pages/post_meal.py", label="📝 Share Your Meal")
st.sidebar.page_link("pages/profile.py", label="👤 My Profile")
st.sidebar.page_link("pages/auth.py", label="🔑 Login/Register")

# Initialize database connection
def get_db_connection():
    conn = sqlite3.connect('food_app.db', check_same_thread=False)
    return conn

# Initialize session state variables
if 'edit_recipe_id' not in st.session_state:
    st.session_state.edit_recipe_id = None

if 'active_recipe_tab' not in st.session_state:
    st.session_state.active_recipe_tab = 0

# Functions for recipe management
def load_recipes():
    """Load recipes from CSV file"""
    try:
        if os.path.exists("data/meals.csv"):
            all_meals_df = pd.read_csv("data/meals.csv")
            # Filter recipes for current user
            user_meals_df = all_meals_df[all_meals_df['user_id'] == st.session_state.user_id]
            return user_meals_df, all_meals_df
        else:
            return pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading recipes: {e}")
        return pd.DataFrame(), pd.DataFrame()

def delete_recipe(recipe_id):
    """Delete a recipe by its ID"""
    try:
        # Load all recipes
        all_meals_df = pd.read_csv("data/meals.csv")
        
        # Get the recipe to delete
        recipe_to_delete = all_meals_df[all_meals_df['recipe_id'] == recipe_id]
        
        # Delete the image file if it exists
        if not recipe_to_delete.empty and 'image_path' in recipe_to_delete.columns:
            image_path = recipe_to_delete.iloc[0]['image_path']
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        
        # Filter out the recipe
        all_meals_df = all_meals_df[all_meals_df['recipe_id'] != recipe_id]
        
        # Save the updated CSV
        all_meals_df.to_csv("data/meals.csv", index=False)
        
        return True
    except Exception as e:
        st.error(f"Error deleting recipe: {e}")
        return False

def edit_recipe(recipe_id):
    """Set the recipe to edit in session state and switch to edit tab"""
    st.session_state.edit_recipe_id = recipe_id
    st.session_state.active_recipe_tab = 1
    st.experimental_rerun()

def get_recipe_by_id(recipe_id, all_meals_df):
    """Get a recipe by its ID"""
    recipe = all_meals_df[all_meals_df['recipe_id'] == recipe_id]
    if not recipe.empty:
        return recipe.iloc[0].to_dict()
    return None

# Check authentication status
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in to view your profile")
    st.button("Go to Login Page", on_click=lambda: st.switch_page("pages/auth.py"))
else:
    # Get user data
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT username, email, full_name, bio, profile_pic, date_joined, is_premium 
        FROM users WHERE id = ?
    """, (st.session_state.user_id,))
    
    user_data = c.fetchone()
    
    if not user_data:
        st.error("User data not found. Please try logging in again.")
    else:
        username, email, full_name, bio, profile_pic, date_joined, is_premium = user_data
        
        # --- PROFILE HEADER ---
        profile_header_col1, profile_header_col2 = st.columns([1, 3])
        
        with profile_header_col1:
            if profile_pic:
                st.image(profile_pic, width=200)
            else:
                st.image("https://api.placeholder.com/200/200", width=200)
                
        with profile_header_col2:
            if is_premium:
                st.title(f"{username} 🌟")
                st.caption("Premium Member")
            else:
                st.title(username)
                
            st.write(f"**Member since:** {date_joined}")
            st.write(f"**Full Name:** {full_name or 'Not set'}")
            
            if bio:
                st.write(f"**About me:** {bio}")
                
            # Edit profile button
            st.button("Edit Profile")
        
        # --- TABS FOR DIFFERENT SECTIONS ---
        tab1, tab2, tab3 = st.tabs(["My Stats", "My Recipes", "Saved Recipes"])
        
        with tab1:
            st.subheader("Nutrition Summary")
            
            # Mock data for user's nutrition history
            dates = pd.date_range(start='2025-02-01', end='2025-03-01')
            nutrition_data = pd.DataFrame({
                'Date': dates,
                'Protein': [round(100 + i*1.5) for i in range(len(dates))],
                'Carbs': [round(150 - i) for i in range(len(dates))],
                'Fat': [round(50 + i*0.5) for i in range(len(dates))],
                'Calories': [round(1800 + i*10) for i in range(len(dates))]
            })
            
            # Nutrition trend chart
            st.subheader("Your Macro Trends")
            fig = px.line(nutrition_data, x='Date', y=['Protein', 'Carbs', 'Fat'], 
                          title='Daily Macro Nutrients (Last 30 Days)')
            st.plotly_chart(fig, use_container_width=True)
            
            # Calorie tracking
            st.subheader("Calorie Tracking")
            fig2 = px.bar(nutrition_data, x='Date', y='Calories', 
                          title='Daily Calorie Intake (Last 30 Days)')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Weekly summary stats
            st.subheader("Weekly Summary")
            weekly_data = nutrition_data.tail(7)
            
            avg_col1, avg_col2, avg_col3, avg_col4 = st.columns(4)
            with avg_col1:
                st.metric("Avg. Protein", f"{round(weekly_data['Protein'].mean())}g", 
                          f"{round(weekly_data['Protein'].mean() - weekly_data['Protein'].iloc[0])}g")
            with avg_col2:
                st.metric("Avg. Carbs", f"{round(weekly_data['Carbs'].mean())}g", 
                          f"{round(weekly_data['Carbs'].mean() - weekly_data['Carbs'].iloc[0])}g")
            with avg_col3:
                st.metric("Avg. Fat", f"{round(weekly_data['Fat'].mean())}g", 
                          f"{round(weekly_data['Fat'].mean() - weekly_data['Fat'].iloc[0])}g")
            with avg_col4:
                st.metric("Avg. Calories", f"{round(weekly_data['Calories'].mean())}", 
                          f"{round(weekly_data['Calories'].mean() - weekly_data['Calories'].iloc[0])}")
        
        with tab2:
            # Create two subpages within the tab
            recipe_tabs = st.tabs(["My Shared Recipes", "Create/Edit Recipe"])
            
            # Load user recipes
            user_meals_df, all_meals_df = load_recipes()
            
            with recipe_tabs[st.session_state.active_recipe_tab]:
                if st.session_state.active_recipe_tab == 0:  # My Shared Recipes tab
                    st.subheader("My Shared Recipes")
                    
                    if user_meals_df.empty:
                        st.info("You haven't shared any recipes yet. Create your first recipe in the 'Create/Edit Recipe' tab!")
                        if st.button("Create My First Recipe"):
                            st.session_state.active_recipe_tab = 1
                            st.experimental_rerun()
                    else:
                        # Convert dataframe to list of dictionaries
                        user_recipes = user_meals_df.to_dict('records')
                        
                        for i, recipe in enumerate(user_recipes):
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                # Check if image path exists
                                if 'image_path' in recipe and recipe['image_path'] and os.path.exists(recipe['image_path']):
                                    st.image(recipe['image_path'], use_column_width=True)
                                else:
                                    st.image("https://api.placeholder.com/300/200", use_column_width=True)
                                
                            with col2:
                                st.subheader(recipe["meal_name"])
                                
                                # Format datetime if it exists
                                if 'datetime' in recipe:
                                    posted_date = recipe['datetime'].split()[0] if ' ' in recipe['datetime'] else recipe['datetime']
                                    st.write(f"Posted on: {posted_date}")
                                
                                # Display recipe info
                                st.write(f"**Category:** {recipe.get('meal_category', 'Uncategorized')}")
                                if 'meal_description' in recipe and recipe['meal_description']:
                                    st.write(recipe['meal_description'])
                                
                                # Mock likes and comments for now, or use real ones if they exist
                                likes = recipe.get('likes', 0)
                                comments = recipe.get('comments', 0)
                                st.write(f"❤️ {likes} likes • 💬 {comments} comments")
                                
                                action_col1, action_col2, action_col3 = st.columns(3)
                                with action_col1:
                                    # View recipe details
                                    if st.button("View Recipe", key=f"view_{i}"):
                                        st.session_state.view_recipe = recipe
                                        st.info("Recipe details (implement view logic here)")
                                        
                                with action_col2:
                                    # Edit recipe button
                                    if st.button("Edit", key=f"edit_{i}"):
                                        edit_recipe(recipe['recipe_id'])
                                        
                                with action_col3:
                                    # Delete recipe button
                                    # Delete recipe button
                                    if st.button("Delete", key=f"delete_{i}"):
                                        print(recipe)  # This shows what's in the dictionary
                                        if delete_recipe(recipe.get('recipe_id')):
                                            st.success("Recipe deleted successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to delete recipe.")
                                    
                            st.divider()
                        
                        # Button to create new recipe
                        if st.button("Create New Recipe", key="create_new"):
                            st.session_state.edit_recipe_id = None
                            st.session_state.active_recipe_tab = 1
                            st.experimental_rerun()
                
                else:  # Create/Edit Recipe tab
                    # Check if we're editing or creating
                    editing = st.session_state.edit_recipe_id is not None
                    
                    if editing:
                        recipe_to_edit = get_recipe_by_id(st.session_state.edit_recipe_id, all_meals_df)
                        st.subheader(f"Edit Recipe: {recipe_to_edit['meal_name']}")
                    else:
                        recipe_to_edit = None
                        st.subheader("Create New Recipe")
                    
                    # Recipe creation/editing form
                    with st.form("meal_form"):
                        # Basic meal information
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            meal_name = st.text_input("Meal Name", 
                                                     value=recipe_to_edit['meal_name'] if editing else "",
                                                     placeholder="e.g., Protein-Packed Breakfast Bowl")
                            
                            meal_category = st.selectbox("Category", 
                                                       options=["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"],
                                                       index=["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"].index(recipe_to_edit['meal_category']) if editing and 'meal_category' in recipe_to_edit else 0)
                            
                            meal_tags = st.text_input("Tags (comma separated)", 
                                                    value=recipe_to_edit['meal_tags'] if editing and 'meal_tags' in recipe_to_edit else "",
                                                    placeholder="e.g., high-protein, keto, vegan")
                        
                        with col2:
                            meal_description = st.text_area("Description", 
                                                          value=recipe_to_edit['meal_description'] if editing and 'meal_description' in recipe_to_edit else "",
                                                          placeholder="Describe your meal in a few sentences...")
                            
                            recipe_url = st.text_input("Recipe URL (optional)", 
                                                      value=recipe_to_edit['recipe_url'] if editing and 'recipe_url' in recipe_to_edit else "",
                                                      placeholder="Link to full recipe if available")
                        
                        # Image upload
                        st.subheader("Meal Image")
                        
                        # Show current image if editing
                        current_image_path = None
                        if editing and 'image_path' in recipe_to_edit and recipe_to_edit['image_path'] and os.path.exists(recipe_to_edit['image_path']):
                            current_image_path = recipe_to_edit['image_path']
                            st.write("Current image:")
                            st.image(current_image_path, width=300)
                            keep_image = st.checkbox("Keep current image", value=True)
                        else:
                            keep_image = False
                        
                        uploaded_image = st.file_uploader("Upload an image of your meal", type=["jpg", "jpeg", "png"])
                        
                        # Show a preview if new image is uploaded
                        if uploaded_image is not None:
                            st.image(uploaded_image, caption="New Image Preview", use_column_width=True)
                        
                        # Nutrition information
                        st.subheader("Nutrition Information")
                        
                        macro_col1, macro_col2, macro_col3, macro_col4 = st.columns(4)
                        
                        with macro_col1:
                            protein = st.number_input("Protein (g)", 
                                                    min_value=0, 
                                                    value=int(recipe_to_edit['protein']) if editing and 'protein' in recipe_to_edit else 20)
                        
                        with macro_col2:
                            carbs = st.number_input("Carbs (g)", 
                                                  min_value=0, 
                                                  value=int(recipe_to_edit['carbs']) if editing and 'carbs' in recipe_to_edit else 30)
                        
                        with macro_col3:
                            fat = st.number_input("Fat (g)", 
                                                min_value=0, 
                                                value=int(recipe_to_edit['fat']) if editing and 'fat' in recipe_to_edit else 10)
                        
                        with macro_col4:
                            default_calories = protein*4 + carbs*4 + fat*9
                            calories = st.number_input("Calories", 
                                                     min_value=0, 
                                                     value=int(recipe_to_edit['calories']) if editing and 'calories' in recipe_to_edit else default_calories)
                        
                        # Additional macros (collapsible)
                        with st.expander("Additional Nutrition Info (Optional)"):
                            add_col1, add_col2, add_col3 = st.columns(3)
                            
                            with add_col1:
                                fiber = st.number_input("Fiber (g)", 
                                                      min_value=0, 
                                                      value=int(recipe_to_edit['fiber']) if editing and 'fiber' in recipe_to_edit else 0)
                                
                                sugar = st.number_input("Sugar (g)", 
                                                      min_value=0, 
                                                      value=int(recipe_to_edit['sugar']) if editing and 'sugar' in recipe_to_edit else 0)
                            
                            with add_col2:
                                sodium = st.number_input("Sodium (mg)", 
                                                       min_value=0, 
                                                       value=int(recipe_to_edit['sodium']) if editing and 'sodium' in recipe_to_edit else 0)
                                
                                cholesterol = st.number_input("Cholesterol (mg)", 
                                                            min_value=0, 
                                                            value=int(recipe_to_edit['cholesterol']) if editing and 'cholesterol' in recipe_to_edit else 0)
                            
                            with add_col3:
                                saturated_fat = st.number_input("Saturated Fat (g)", 
                                                              min_value=0, 
                                                              value=int(recipe_to_edit['saturated_fat']) if editing and 'saturated_fat' in recipe_to_edit else 0)
                                
                                trans_fat = st.number_input("Trans Fat (g)", 
                                                          min_value=0, 
                                                          value=int(recipe_to_edit['trans_fat']) if editing and 'trans_fat' in recipe_to_edit else 0)
                        
                        # Ingredients and Instructions
                        st.subheader("Ingredients")
                        ingredients = st.text_area("List your ingredients (one per line)", 
                                                 height=150, 
                                                 value=recipe_to_edit['ingredients'] if editing and 'ingredients' in recipe_to_edit else "",
                                                 placeholder="1 cup oats\n2 scoops protein powder\n1 tbsp peanut butter")
                        
                        st.subheader("Instructions")
                        instructions = st.text_area("Recipe instructions", 
                                                  height=150,
                                                  value=recipe_to_edit['instructions'] if editing and 'instructions' in recipe_to_edit else "",
                                                  placeholder="1. Mix oats and protein powder\n2. Add water and microwave for 2 minutes\n3. Top with peanut butter")
                        
                        # Submit button
                        if editing:
                            submitted = st.form_submit_button("Update Recipe")
                        else:
                            submitted = st.form_submit_button("Share Your Meal")

                    if submitted:
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
                            "user_id": st.session_state.user_id,
                            "datetime": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # Set recipe_id
                        if editing:
                            meal_data["recipe_id"] = st.session_state.edit_recipe_id
                        else:
                            meal_data["recipe_id"] = str(uuid.uuid4())
                        
                        # Handle image
                        if uploaded_image is not None:
                            # Create images directory if it doesn't exist
                            os.makedirs("images", exist_ok=True)
                            
                            # Generate unique filename
                            image_filename = f"meal_{meal_data['recipe_id']}.jpg"
                            image_path = os.path.join("images", image_filename)
                            
                            # Save the image
                            image = Image.open(uploaded_image)
                            image.save(image_path)
                            
                            # Add image path to meal data
                            meal_data["image_path"] = image_path
                        elif editing and keep_image and current_image_path:
                            # Keep the current image
                            meal_data["image_path"] = current_image_path
                        
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
                        
                        if editing:
                            # Remove old recipe data
                            meals_df = meals_df[meals_df['recipe_id'] != st.session_state.edit_recipe_id]
                        
                        # Append new meal
                        new_meal_df = pd.DataFrame([meal_data])
                        meals_df = pd.concat([meals_df, new_meal_df], ignore_index=True)
                        
                        # Save to CSV
                        meals_df.to_csv("data/meals.csv", index=False)
                        
                        # Success message
                        if editing:
                            st.success("Your recipe has been updated successfully!")
                        else:
                            st.success("Your meal has been shared successfully!")
                        
                        # Show a preview of how it will appear in the feed
                        st.subheader("Preview:")
                        
                        preview_col1, preview_col2 = st.columns([1, 2])
                        
                        with preview_col1:
                            if uploaded_image is not None:
                                st.image(uploaded_image, use_column_width=True)
                            elif editing and keep_image and current_image_path:
                                st.image(current_image_path, use_column_width=True)
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
                        
                        # Reset editing state and return to recipes list
                        if st.button("View My Recipes"):
                            st.session_state.edit_recipe_id = None
                            st.session_state.active_recipe_tab = 0
                            st.experimental_rerun()
                    
                    # Cancel button (outside the form)
                    if st.button("Cancel"):
                        st.session_state.edit_recipe_id = None
                        st.session_state.active_recipe_tab = 0
                        st.experimental_rerun()
        
        with tab3:
            st.subheader("Recipes You've Saved")
            
            # Mock data for saved recipes
            saved_recipes = [
                {"name": "Banana Protein Muffins", "author": "@HealthyBaker", "date_saved": "Mar 1, 2025", 
                 "image": "https://api.placeholder.com/300/200"},
                {"name": "Quinoa Salad Bowl", "author": "@NutritionChef", "date_saved": "Feb 25, 2025", 
                 "image": "https://api.placeholder.com/300/200"},
                {"name": "Low-Carb Pizza", "author": "@KetoKing", "date_saved": "Feb 20, 2025", 
                 "image": "https://api.placeholder.com/300/200"},
                {"name": "Protein Ice Cream", "author": "@FitnessFoodie", "date_saved": "Feb 18, 2025", 
                 "image": "https://api.placeholder.com/300/200"}
            ]
            
            saved_grid_cols = st.columns(2)
            
            for i, recipe in enumerate(saved_recipes):
                with saved_grid_cols[i % 2]:
                    st.image(recipe["image"], use_column_width=True)
                    st.subheader(recipe["name"])
                    st.write(f"By {recipe['author']} • Saved on {recipe['date_saved']}")
                    
                    view_col, unsave_col = st.columns(2)
                    with view_col:
                        st.button("View Recipe", key=f"saved_view_{i}")
                    with unsave_col:
                        st.button("Unsave", key=f"saved_unsave_{i}")
                    
                    st.write("")  # Add some spacing
