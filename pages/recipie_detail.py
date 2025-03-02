# pages/recipe_detail.py
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime
from utils.sidebar import create_sidebar_navigation

# Page configuration
st.set_page_config(page_title="Recipe Details - Leo's Food App", page_icon="🐱", layout="wide")

# Create sidebar navigation
sidebar = create_sidebar_navigation("pages/recipe_detail.py")

# Function to get recipe from database by ID
def get_recipe_by_id(recipe_id):
    try:
        # Make sure the data directory exists
        if not os.path.exists("data"):
            st.error("Database not found. Please add a recipe first.")
            return None
            
        conn = sqlite3.connect('data/food_app.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        c = conn.cursor()
        
        # Query for the recipe with the given ID
        c.execute("SELECT * FROM meals WHERE id = ?", (recipe_id,))
        recipe_row = c.fetchone()
        
        if recipe_row is None:
            return None
            
        # Convert row to dictionary
        recipe = dict(recipe_row)
        
        # Format additional information
        # Parse date
        try:
            posted_date = datetime.strptime(recipe['date_posted'], "%Y-%m-%d %H:%M:%S")
            recipe['date_posted'] = posted_date.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            recipe['date_posted'] = "Unknown date"
            
        # Split ingredients and instructions
        if recipe['ingredients']:
            recipe['ingredients'] = recipe['ingredients'].split('\n')
        else:
            recipe['ingredients'] = []
            
        if recipe['instructions']:
            recipe['instructions'] = recipe['instructions'].split('\n')
        else:
            recipe['instructions'] = []
            
        # Format tags
        if recipe['tags']:
            recipe['tags'] = [tag.strip() for tag in recipe['tags'].split(',')]
        else:
            recipe['tags'] = []
            
        # Handle image path
        if recipe['image_path'] and not recipe['image_path'].startswith('http'):
            # If the path is local and file exists
            if os.path.exists(recipe['image_path']):
                # In a real app, you would serve this file properly
                recipe['image'] = recipe['image_path']
            else:
                recipe['image'] = "https://api.placeholder.com/800/600"
        else:
            recipe['image'] = recipe['image_path']
            
        # Add additional fields that might not be in the database
        recipe.setdefault('rating', 4.5)
        recipe.setdefault('reviews', 0)
        recipe.setdefault('prep_time', "5 min")
        recipe.setdefault('cook_time', "0 min")
        recipe.setdefault('total_time', "5 min")
        recipe.setdefault('servings', 1)
        recipe.setdefault('fiber', 0)
        recipe.setdefault('sugar', 0)
        recipe.setdefault('sodium', 0)
        recipe.setdefault('saved_count', 0)
        
        # Get similar recipes based on category or tags
        c.execute("""
            SELECT id, name, image_path FROM meals 
            WHERE id != ? AND (category = ? OR tags LIKE ?) 
            ORDER BY date_posted DESC LIMIT 3
        """, (recipe_id, recipe['category'], f"%{recipe['tags'][0] if recipe['tags'] else ''}%"))
        
        similar_recipes = []
        for row in c.fetchall():
            similar = dict(row)
            if similar['image_path'] and not similar['image_path'].startswith('http'):
                similar['image'] = "https://api.placeholder.com/150/150"
            else:
                similar['image'] = similar['image_path']
            similar_recipes.append(similar)
            
        recipe['similar_recipes'] = similar_recipes
            
        conn.close()
        return recipe
        
    except Exception as e:
        st.error(f"Error retrieving recipe: {e}")
        return None

# Get recipe ID from query parameters
# In a real app, you'd parse query parameters properly
query_params = st.experimental_get_query_params()
recipe_id = query_params.get("id", ["1"])[0]  # Default to ID 1 if not provided

# Try to get the recipe from database
recipe = get_recipe_by_id(recipe_id)

# If recipe not found, show a sample
if recipe is None:
    # For demo purposes, let's create a sample recipe
    recipe = {
        "id": 1,
        "name": "Protein-Packed Overnight Oats",
        "user": "@HealthyChef",
        "username": "@HealthyChef",
        "user_profile_pic": "https://api.placeholder.com/100/100",
        "date_posted": "February 28, 2025",
        "image": "https://api.placeholder.com/800/600",
        "category": "Breakfast",
        "description": "A delicious high-protein breakfast that you can prepare the night before. Perfect for busy mornings when you need a nutritious start to your day without spending time cooking.",
        "rating": 4.8,
        "reviews": 124,
        "protein": 32,
        "carbs": 45,
        "fat": 12,
        "calories": 420,
        "fiber": 8,
        "sugar": 6,
        "sodium": 120,
        "prep_time": "5 min",
        "cook_time": "0 min",
        "total_time": "5 min + overnight",
        "servings": 1,
        "ingredients": [
            "1/2 cup rolled oats",
            "1 scoop vanilla protein powder",
            "1 tablespoon chia seeds",
            "1 tablespoon almond butter",
            "1/2 cup almond milk",
            "1/4 cup Greek yogurt",
            "1/2 banana, sliced",
            "1/4 cup berries",
            "1 teaspoon honey or maple syrup (optional)"
        ],
        "instructions": [
            "In a jar or container, mix oats, protein powder, and chia seeds.",
            "Add almond milk and Greek yogurt, then stir until well combined.",
            "Stir in almond butter and sweetener if using.",
            "Seal the container and refrigerate overnight or for at least 4 hours.",
            "Before serving, top with sliced banana and berries."
        ],
        "tags": ["high-protein", "meal-prep", "vegetarian", "quick", "no-cook"],
        "saved_count": 342,
        "likes": 518,
        "similar_recipes": [
            {"id": 2, "name": "Protein Pancakes", "image": "https://api.placeholder.com/150/150"},
            {"id": 3, "name": "Greek Yogurt Bowl", "image": "https://api.placeholder.com/150/150"},
            {"id": 4, "name": "Protein Smoothie", "image": "https://api.placeholder.com/150/150"}
        ]
    }

# Function to update likes or comments count
def update_recipe_stats(recipe_id, field, value):
    try:
        conn = sqlite3.connect('data/food_app.db')
        c = conn.cursor()
        
        # Update the specified field
        c.execute(f"UPDATE meals SET {field} = ? WHERE id = ?", (value, recipe_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating recipe stats: {e}")
        return False

# Function to save recipe to user's saved recipes
def save_recipe(recipe_id, user_id):
    try:
        conn = sqlite3.connect('data/food_app.db')
        c = conn.cursor()
        
        # Check if table exists, if not create it
        c.execute('''
        CREATE TABLE IF NOT EXISTS saved_recipes (
            user_id TEXT,
            recipe_id TEXT,
            date_saved TIMESTAMP,
            PRIMARY KEY (user_id, recipe_id)
        )
        ''')
        
        # Save the recipe
        c.execute(
            "INSERT OR REPLACE INTO saved_recipes (user_id, recipe_id, date_saved) VALUES (?, ?, ?)",
            (user_id, recipe_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving recipe: {e}")
        return False

# --- RECIPE DETAIL PAGE ---

# Top section: Image and basic info
col_img, col_info = st.columns([3, 2], gap="large")

with col_img:
    st.image(recipe["image"], use_column_width=True)
    
    # Action buttons
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
    with btn_col1:
        if st.button("❤️ Like", key="like_btn"):
            # Update likes count if button clicked
            new_likes = recipe.get('likes', 0) + 1
            if 'id' in recipe and update_recipe_stats(recipe['id'], 'likes', new_likes):
                recipe['likes'] = new_likes
                st.success("Recipe liked!")
                st.experimental_rerun()
    with btn_col2:
        if st.button("🔖 Save", key="save_btn"):
            if 'authenticated' in st.session_state and st.session_state.authenticated:
                if 'id' in recipe and save_recipe(recipe['id'], st.session_state.user_id):
                    st.success("Recipe saved to your collection!")
            else:
                st.warning("Please log in to save recipes")
                if st.button("Go to Login"):
                    st.switch_page("pages/auth.py")
    with btn_col3:
        st.button("📤 Share", key="share_btn")
    with btn_col4:
        st.button("🖨️ Print", key="print_btn")

with col_info:
    st.title(recipe["name"])
    
    # User and date info
    display_user = recipe.get('username', recipe.get('user', 'Unknown User'))
    st.markdown(f"Posted by {display_user} on {recipe['date_posted']}")
    
    # Rating
    st.markdown(f"⭐ {recipe['rating']} ({recipe['reviews']} ratings)")
    
    # Description
    st.markdown(recipe["description"])
    
    # Tags
    if recipe.get('tags'):
        st.markdown("**Tags:** " + ", ".join([f"#{tag}" for tag in recipe["tags"]]))
    
    # Recipe stats
    stats_col1, stats_col2, stats_col3 = st.columns(3)
    with stats_col1:
        st.markdown(f"**Prep time:**  \n{recipe['prep_time']}")
    with stats_col2:
        st.markdown(f"**Cook time:**  \n{recipe['cook_time']}")
    with stats_col3:
        st.markdown(f"**Servings:**  \n{recipe['servings']}")

# Nutrition information
st.subheader("Nutrition Information")
macro_cols = st.columns(4)

with macro_cols[0]:
    st.metric("Protein", f"{recipe['protein']}g")
with macro_cols[1]:
    st.metric("Carbs", f"{recipe['carbs']}g")
with macro_cols[2]:
    st.metric("Fat", f"{recipe['fat']}g")
with macro_cols[3]:
    st.metric("Calories", f"{recipe['calories']}")

# Macro pie chart
nutrition_data = pd.DataFrame({
    'Nutrient': ['Protein', 'Carbs', 'Fat'],
    'Grams': [recipe['protein'], recipe['carbs'], recipe['fat']],
    'Calories': [recipe['protein'] * 4, recipe['carbs'] * 4, recipe['fat'] * 9]
})

chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig = px.pie(nutrition_data, values='Grams', names='Nutrient', 
                 title='Macronutrient Distribution (grams)',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    fig = px.pie(nutrition_data, values='Calories', names='Nutrient', 
                 title='Calorie Distribution',
                 color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'])
    st.plotly_chart(fig, use_container_width=True)

# Ingredients and Instructions
ingredients_col, instructions_col = st.columns(2)

with ingredients_col:
    st.subheader("Ingredients")
    for item in recipe["ingredients"]:
        st.checkbox(item)

with instructions_col:
    st.subheader("Instructions")
    for i, step in enumerate(recipe["instructions"]):
        st.markdown(f"{i+1}. {step}")

# Comments section
st.subheader("Comments")
with st.form("comment_form"):
    comment_text = st.text_area("Leave a comment", placeholder="Share your thoughts or ask a question...")
    submit_comment = st.form_submit_button("Post Comment")

if submit_comment and comment_text:
    # Update comment count in database
    new_comments = recipe.get('comments', 0) + 1
    if 'id' in recipe and update_recipe_stats(recipe['id'], 'comments', new_comments):
        st.success("Comment posted successfully!")
        # In a real app, you would also save the comment text to a comments table
        recipe['comments'] = new_comments

# Sample comments (or you could fetch real comments from a database)
st.markdown("**@FitnessFoodie** • 2 days ago  \nMade this yesterday and loved it! I added a tablespoon of cocoa powder for a chocolate version. Delicious!")

st.markdown("**@ProteinQueen** • 5 days ago  \nThis has become my go-to breakfast! So convenient and keeps me full until lunch.")

# Similar recipes
if recipe.get('similar_recipes'):
    st.subheader("You might also like")
    similar_cols = st.columns(len(recipe["similar_recipes"]))

    for i, similar in enumerate(recipe["similar_recipes"]):
        with similar_cols[i]:
            st.image(similar["image"], use_column_width=True)
            st.markdown(f"**{similar['name']}**")
            if st.button("View Recipe", key=f"similar_{i}"):
                st.switch_page(f"pages/recipe_detail.py?id={similar['id']}")