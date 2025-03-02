import streamlit as st
import pandas as pd
import random
import sqlite3
import uuid  # Add this import to resolve the NameError
from datetime import datetime  # Add this to resolve datetime issues
from utils.sidebar import create_sidebar_navigation

# Page configuration
st.set_page_config(page_title="Leo's Food App", page_icon="🐱", layout="wide")

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Create sidebar navigation
sidebar = create_sidebar_navigation("app.py")

# --- SEARCH AND FILTER SECTION ---
with st.container():
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_query = st.text_input("Search for recipes or ingredients:", placeholder="e.g., chicken, protein bowl, breakfast...")
    
    with col2:
        category = st.selectbox("Category", ["All", "Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest", "Most Popular", "Highest Protein", "Lowest Calories"])

# --- WELCOME BANNER ---
if not search_query and category == "All":
    # Show personalized welcome if user is logged in
    if st.session_state.authenticated:
        st.header(f"Welcome back to Leo's Food App, {st.session_state.username}! 🐱🍽️")
        st.write("Here are some recommendations based on your preferences.")
    else:
        st.header("Welcome to Leo's Food App! 🐱🍽️")
        st.write("Share your meals, track macros, and discover new recipes from the community.")
        # Call-to-action for non-logged in users
        cta_col1, cta_col2 = st.columns(2)
        with cta_col1:
            st.info("👋 **New here?** Create an account to save recipes and track your nutrition goals!")
        with cta_col2:
            st.button("Sign Up Now", on_click=lambda: st.switch_page("pages/auth.py"))
    
    # Featured meals carousel
    st.subheader("Featured Meals This Week")
    featured_cols = st.columns(3)
    
    with featured_cols[0]:
        st.image("https://api.placeholder.com/640/480", use_column_width=True)
        st.markdown("#### Protein Pancakes")
        st.markdown("⭐ 4.8 (124 ratings) • By @FitFoodie")
        st.markdown("**Macros:** 32g protein • 45g carbs • 12g fat • 420 calories")
        st.button("View Recipe", key="featured1")
    
    with featured_cols[1]:
        st.image("https://api.placeholder.com/640/480", use_column_width=True)
        st.markdown("#### Mediterranean Bowl")
        st.markdown("⭐ 4.7 (98 ratings) • By @HealthyEats")
        st.markdown("**Macros:** 28g protein • 52g carbs • 15g fat • 460 calories")
        st.button("View Recipe", key="featured2")
    
    with featured_cols[2]:
        st.image("https://api.placeholder.com/640/480", use_column_width=True)
        st.markdown("#### Chocolate Protein Smoothie")
        st.markdown("⭐ 4.9 (156 ratings) • By @SmoothieKing")
        st.markdown("**Macros:** 24g protein • 30g carbs • 8g fat • 290 calories")
        st.button("View Recipe", key="featured3")

# --- SEARCH RESULTS OR MAIN FEED ---
# --- SEARCH RESULTS OR MAIN FEED ---
st.divider()

# Function to get meals from database
def get_meals_from_db(search_query=None, category=None, sort_by=None, limit=12):
    try:
        conn = sqlite3.connect('data/food_app.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        c = conn.cursor()
        
        # Build the query
        query = "SELECT * FROM meals"
        params = []
        
        # Add search condition if provided
        if search_query:
            query += " WHERE (name LIKE ? OR description LIKE ? OR tags LIKE ?)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])
            
            # Add category filter with AND if search is active
            if category and category != "All":
                query += " AND category = ?"
                params.append(category)
        # Add category filter with WHERE if it's the only filter
        elif category and category != "All":
            query += " WHERE category = ?"
            params.append(category)
        
        # Add sorting
        if sort_by == "Newest":
            query += " ORDER BY date_posted DESC"
        elif sort_by == "Most Popular":
            query += " ORDER BY likes DESC"
        elif sort_by == "Highest Protein":
            query += " ORDER BY protein DESC"
        elif sort_by == "Lowest Calories":
            query += " ORDER BY calories ASC"
        else:
            # Default sorting
            query += " ORDER BY date_posted DESC"
            
        # Add limit
        query += f" LIMIT {limit}"
        
        # Execute the query
        c.execute(query, params)
        
        # Fetch all results
        meals = []
        for row in c.fetchall():
            meal = dict(row)
            
            # Format the date
            try:
                posted_date = datetime.strptime(meal['date_posted'], "%Y-%m-%d %H:%M:%S")
                meal['date_posted'] = posted_date
            except (ValueError, TypeError):
                # Handle cases where the date might be in a different format or None
                meal['date_posted'] = datetime.now()
            
            # Handle image path
            if meal['image_path'] and meal['image_path'].startswith('data/'):
                # This is a local file path
                # In a production app, you'd use a proper file serving solution
                # For simplicity, we'll use a placeholder if it's a local path
                meal['image'] = "https://api.placeholder.com/640/480"
            else:
                meal['image'] = meal['image_path']
                
            meals.append(meal)
            
        conn.close()
        return meals
        
    except Exception as e:
        st.error(f"Error retrieving meals: {e}")
        return []

# If no meals in database, fall back to sample data function
def get_sample_meals(n=12):
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"]
    users = ["@HealthyChef", "@FitnessFoodie", "@MacroMaster", "@KetoKing", "@VeganVibes", "@LeoTheChef"]
    
    meals = []
    
    breakfast_items = ["Protein Oatmeal", "Greek Yogurt Bowl", "Egg White Scramble", "Avocado Toast", "Protein Pancakes"]
    lunch_items = ["Chicken Salad", "Tuna Wrap", "Quinoa Bowl", "Turkey Sandwich", "Lentil Soup"]
    dinner_items = ["Salmon with Veggies", "Steak and Sweet Potato", "Chicken Stir Fry", "Tofu Curry", "Turkey Meatballs"]
    snack_items = ["Protein Bar", "Greek Yogurt", "Hummus and Veggies", "Protein Shake", "Apple with Peanut Butter"]
    dessert_items = ["Protein Brownies", "Fruit Parfait", "Protein Cookies", "Frozen Yogurt", "Protein Mug Cake"]
    
    all_items = {
        "Breakfast": breakfast_items,
        "Lunch": lunch_items,
        "Dinner": dinner_items,
        "Snacks": snack_items,
        "Desserts": dessert_items
    }
    
    for i in range(n):
        meal_type = random.choice(meal_types) if category == "All" else category
        name = random.choice(all_items[meal_type])
        
        if search_query and search_query.lower() not in name.lower():
            continue
            
        protein = random.randint(15, 40)
        carbs = random.randint(20, 60)
        fat = random.randint(5, 25)
        calories = protein * 4 + carbs * 4 + fat * 9
        
        meals.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "image": f"https://api.placeholder.com/640/480",
            "user": random.choice(users),
            "username": random.choice(users),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews": random.randint(10, 200),
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "calories": calories,
            "category": meal_type,
            "date_posted": pd.Timestamp("2025-03-01") - pd.Timedelta(days=random.randint(0, 30)),
            "likes": random.randint(5, 100),
            "comments": random.randint(0, 20)
        })
    
    # Sort results based on selected option
    if sort_by == "Newest":
        meals = sorted(meals, key=lambda x: x["date_posted"], reverse=True)
    elif sort_by == "Most Popular":
        meals = sorted(meals, key=lambda x: x["likes"], reverse=True)
    elif sort_by == "Highest Protein":
        meals = sorted(meals, key=lambda x: x["protein"], reverse=True)
    elif sort_by == "Lowest Calories":
        meals = sorted(meals, key=lambda x: x["calories"])
        
    return meals

# Display search results or feed
# First try to get meals from the database
meals = get_meals_from_db(search_query, category, sort_by)

# If no meals found in database, use sample data
if not meals:
    meals = get_sample_meals()

if search_query:
    st.subheader(f"Results for: {search_query}")
    if not meals:
        st.write("No meals found matching your search. Try a different keyword.")
elif category != "All":
    st.subheader(f"{category} Meals")
else:
    st.subheader("Trending Meals")

# Pinterest-style masonry grid layout
cols = st.columns(3)
for i, meal in enumerate(meals):
    with cols[i % 3]:
        st.image(meal["image"], use_column_width=True)
        st.markdown(f"#### {meal['name']}")
        
        # Display username if available, otherwise use user field
        user_display = meal.get('username', meal.get('user', 'Unknown User'))
        st.markdown(f"⭐ {meal.get('rating', '4.5')} ({meal.get('reviews', '0')} ratings) • {user_display}")
        
        # Macro information in a clean format
        macros_col1, macros_col2 = st.columns(2)
        with macros_col1:
            st.markdown(f"**Protein:** {meal['protein']}g")
            st.markdown(f"**Carbs:** {meal['carbs']}g")
        with macros_col2:
            st.markdown(f"**Fat:** {meal['fat']}g")
            st.markdown(f"**Calories:** {meal['calories']}")
        
        # Action buttons
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            if st.button("View Recipe", key=f"recipe_{i}"):
                # Navigate to recipe detail page with the meal ID
                st.switch_page(f"pages/recipe_detail.py?id={meal['id']}")
        with button_col2:
            # Different button text based on auth status
            if st.session_state.authenticated:
                st.button("Save", key=f"save_{i}")
            else:
                if st.button("Login to Save", key=f"login_save_{i}"):
                    st.switch_page("pages/auth.py")
        
        # Add some spacing between cards
        st.markdown("<br>", unsafe_allow_html=True)

# --- FOOTER ---
st.divider()
st.markdown("© 2025 Leo's Food App | [Terms of Service](/) | [Privacy Policy](/)")