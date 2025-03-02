import streamlit as st
import pandas as pd
import random
import sqlite3
import os
from PIL import Image

# Page configuration
st.set_page_config(page_title="Leo's Kitchen", page_icon="images/logo.png", layout="wide")
st.logo(image="images/logo.png", size="large", link=None, icon_image=None)

# Initialize session state variables if they don't exist
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# --- SIDEBAR NAVIGATION ---
# st.sidebar.title("Navigation")
# st.sidebar.page_link("Home.py", label="🏠 Home", icon="🏠")
# st.sidebar.page_link("pages/About_Leo's_Kitchen.py", label="ℹ️ About Me")
# st.sidebar.page_link("pages/My_Recipe.py", label="📊 My Recipes")
# st.sidebar.page_link("pages/Leo_Chat_Bot.py", label="🤖 Chat Bot")
# st.sidebar.page_link("pages/Share_Your_Meal.py", label="📝 Share Your Meal")

# Check authentication and display appropriate sidebar options
if st.session_state.authenticated:
    st.sidebar.divider()
    st.sidebar.subheader(f"Welcome, {st.session_state.username}")
    st.sidebar.page_link("pages/My_Profile.py", label="👤 My Profile")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.user_id = None
        st.rerun()
else:
    st.sidebar.divider()
    st.sidebar.page_link("pages/Login.py", label="👤 Login/Register")

# --- SEARCH AND FILTER SECTION ---
with st.container():
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        search_query = st.text_input("Search for recipes or ingredients:",
                                     placeholder="e.g., chicken, protein bowl, breakfast...")

    with col2:
        category = st.selectbox("Category", ["All", "Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"])

    with col3:
        sort_by = st.selectbox("Sort by", ["Newest", "Most Popular", "Highest Protein", "Lowest Calories"])

# --- WELCOME BANNER ---
if not search_query and category == "All":
    # Show personalized welcome if user is logged in
    if st.session_state.authenticated:
        st.header(f"Welcome back to Leo's Kitchen, {st.session_state.username}! 🐱🍽️")
        st.write("Here are some recommendations based on your preferences.")
    else:
        st.header("Welcome to Leo's Kitchen! 🐱🍽️")
        st.write("Share your meals, track macros, and discover new recipes from the community.")
        # Call-to-action for non-logged in users
        cta_col1, cta_col2 = st.columns(2)
        with cta_col1:
            st.info("👋 **New here?** Create an account to save recipes and track your nutrition goals!")
        with cta_col2:
            st.button("Sign Up Now", on_click=lambda: st.switch_page("pages/Login.py"))

    # Featured meals carousel
    st.subheader("Featured Meals This Week")
    featured_cols = st.columns(3)

    with featured_cols[0]:
        st.image("https://th.bing.com/th/id/R.94d8183231643e76b89b5d57b93db74f?rik=N9XvJrMEvlF9VQ&pid=ImgRaw&r=0",
                 use_container_width=True)
        st.markdown("#### Protein Pancakes")
        st.markdown("⭐ 4.8 (124 ratings) • By @FitFoodie")
        st.markdown("**Macros:** 32g protein • 45g carbs • 12g fat • 420 calories")
        st.button("View Recipe", key="featured1")

    with featured_cols[1]:
        st.image("https://media1.popsugar-assets.com/files/thumbor/REfalCwtqSNtZ0waqnYlMOT00vE/fit-in/1024x1024/filter"
                 "s:format_auto-!!-:strip_icc-!!-/2018/02/21/636/n/44100376/2b69acf293c6667e_Mediterranean-Buddha-Bowl-"
                 "Culinary-Hill-LR-01-660x990/i/Mediterranean-Bowl.jpg", use_container_width=True)
        st.markdown("#### Mediterranean Bowl")
        st.markdown("⭐ 4.7 (98 ratings) • By @HealthyEats")
        st.markdown("**Macros:** 28g protein • 52g carbs • 15g fat • 460 calories")
        st.button("View Recipe", key="featured2")

    with featured_cols[2]:
        st.image("https://eatthegains.com/wp-content/uploads/2021/08/Chocolate-Protein-Smoothie-6.jpg",
                 use_container_width=True)
        st.markdown("#### Chocolate Protein Smoothie")
        st.markdown("⭐ 4.9 (156 ratings) • By @SmoothieKing")
        st.markdown("**Macros:** 24g protein • 30g carbs • 8g fat • 290 calories")
        st.button("View Recipe", key="featured3")

# --- SEARCH RESULTS OR MAIN FEED ---
st.divider()


# Function to get real meals from CSV plus fallback to sample data
def get_meals(search_query="", category="All", sort_by="Newest", n_samples=12):
    real_meals = []

    # First, try to load real meals from CSV
    try:
        if os.path.exists("data/meals.csv"):
            meals_df = pd.read_csv("data/meals.csv")

            # Apply category filter
            if category != "All":
                meals_df = meals_df[meals_df["meal_category"] == category]

            # Apply search filter
            if search_query:
                # Search in meal name, description, ingredients and tags
                search_mask = (
                        meals_df["meal_name"].str.contains(search_query, case=False, na=False) |
                        meals_df["meal_description"].str.contains(search_query, case=False, na=False) |
                        meals_df["ingredients"].str.contains(search_query, case=False, na=False) |
                        meals_df["meal_tags"].str.contains(search_query, case=False, na=False)
                )
                meals_df = meals_df[search_mask]

            # Sort the data
            if sort_by == "Newest":
                if "datetime" in meals_df.columns:
                    meals_df = meals_df.sort_values("datetime", ascending=False)
            elif sort_by == "Highest Protein":
                meals_df = meals_df.sort_values("protein", ascending=False)
            elif sort_by == "Lowest Calories":
                meals_df = meals_df.sort_values("calories", ascending=True)
            # "Most Popular" uses default order for now since we don't track popularity yet

            # Convert to list of dictionaries
            for _, meal in meals_df.iterrows():
                meal_dict = meal.to_dict()

                # Create a simplified version for the feed
                real_meal = {
                    "name": meal_dict.get("meal_name", "Untitled Meal"),
                    "image": meal_dict.get("image_path", "https://api.placeholder.com/640/480"),
                    "user": st.session_state.get("username", "@User") if st.session_state.get("authenticated",
                                                                                              False) else "@Guest",
                    "rating": 5.0,  # Default rating (we'll add a rating system later)
                    "reviews": 1,  # Default reviews
                    "protein": meal_dict.get("protein", 0),
                    "carbs": meal_dict.get("carbs", 0),
                    "fat": meal_dict.get("fat", 0),
                    "calories": meal_dict.get("calories", 0),
                    "category": meal_dict.get("meal_category", "Other"),
                    "date_posted": meal_dict.get("datetime", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
                    # Additional fields for details view
                    "description": meal_dict.get("meal_description", ""),
                    "recipe_url": meal_dict.get("recipe_url", ""),
                    "ingredients": meal_dict.get("ingredients", ""),
                    "instructions": meal_dict.get("instructions", ""),
                    "is_user_submitted": True,
                    "original_data": meal_dict  # Store the original data for reference
                }

                real_meals.append(real_meal)
    except Exception as e:
        st.error(f"Error loading meals: {e}")
        # Continue to sample data if there's an error

    # If we don't have enough real meals, add sample ones
    if len(real_meals) < n_samples:
        sample_meals = get_sample_meals(n=n_samples - len(real_meals),
                                        search_query=search_query,
                                        category=category,
                                        sort_by=sort_by)
        return real_meals + sample_meals

    return real_meals


# Function to generate sample meal data (for supplementary content)
def get_sample_meals(n=12, search_query="", category="All", sort_by="Newest"):
    meal_types = ["Breakfast", "Lunch", "Dinner", "Snacks", "Desserts"]
    users = ["@HealthyChef", "@FitnessFoodie", "@MacroMaster", "@KetoKing", "@VeganVibes", "@LeoTheChef"]

    meals = []

    breakfast_items = ["Protein Oatmeal", "Greek Yogurt Bowl", "Egg White Scramble", "Avocado Toast",
                       "Protein Pancakes"]
    lunch_items = ["Chicken Salad", "Tuna Wrap", "Quinoa Bowl", "Turkey Sandwich", "Lentil Soup"]
    dinner_items = ["Salmon with Veggies", "Steak and Sweet Potato", "Chicken Stir Fry", "Tofu Curry",
                    "Turkey Meatballs"]
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
            "name": name,
            "image": f"https://api.placeholder.com/640/480",
            "user": random.choice(users),
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews": random.randint(10, 200),
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "calories": calories,
            "category": meal_type,
            "date_posted": pd.Timestamp("2025-03-01") - pd.Timedelta(days=random.randint(0, 30)),
            "is_user_submitted": False
        })

    # Sort results based on selected option
    if sort_by == "Newest":
        meals = sorted(meals, key=lambda x: x["date_posted"], reverse=True)
    elif sort_by == "Most Popular":
        meals = sorted(meals, key=lambda x: x["reviews"], reverse=True)
    elif sort_by == "Highest Protein":
        meals = sorted(meals, key=lambda x: x["protein"], reverse=True)
    elif sort_by == "Lowest Calories":
        meals = sorted(meals, key=lambda x: x["calories"])

    return meals


# Display search results or feed
meals = get_meals(search_query=search_query, category=category, sort_by=sort_by)

if search_query:
    st.subheader(f"Results for: {search_query}")
    if not meals:
        st.write("No meals found matching your search. Try a different keyword.")
elif category != "All":
    st.subheader(f"{category} Meals")
else:
    st.subheader("Trending Meals")


# Function to handle meal detail view
def view_meal_details(meal_index):
    st.session_state.selected_meal_index = meal_index


# Initialize session state for meal viewing
if 'selected_meal_index' not in st.session_state:
    st.session_state.selected_meal_index = None


# Function to safely check if path exists
def safe_path_exists(path):
    # Check if path is a valid type for os.path.exists
    if isinstance(path, (str, bytes, os.PathLike)) or isinstance(path, int):
        return os.path.exists(path)
    return False


# Display meal detail view if selected
if st.session_state.selected_meal_index is not None and st.session_state.selected_meal_index < len(meals):
    meal = meals[st.session_state.selected_meal_index]

    # Back button
    if st.button("← Back to Feed"):
        st.session_state.selected_meal_index = None
        st.rerun()

    # Meal detail view
    st.header(meal["name"])

    detail_col1, detail_col2 = st.columns([1, 2])

    with detail_col1:
        # Handle image display - Using safe_path_exists to prevent type errors
        image_path = meal.get("image")
        if isinstance(image_path, (str, bytes, os.PathLike)) and safe_path_exists(image_path):
            st.image(image_path, use_container_width=True)
        else:
            st.image("https://api.placeholder.com/640/480", use_container_width=True)

        # User info and stats
        st.markdown(f"**Posted by:** {meal['user']}")
        st.markdown(f"⭐ {meal['rating']} ({meal['reviews']} ratings)")

        # Nutrition card
        st.markdown("### Nutrition Information")
        st.markdown(f"**Protein:** {meal['protein']}g")
        st.markdown(f"**Carbs:** {meal['carbs']}g")
        st.markdown(f"**Fat:** {meal['fat']}g")
        st.markdown(f"**Calories:** {meal['calories']}")

        # Additional nutrition if available
        if meal.get("is_user_submitted", False) and "original_data" in meal:
            orig = meal["original_data"]
            with st.expander("Additional Nutrition Info"):
                add_col1, add_col2 = st.columns(2)
                with add_col1:
                    st.markdown(f"**Fiber:** {orig.get('fiber', 0)}g")
                    st.markdown(f"**Sugar:** {orig.get('sugar', 0)}g")
                    st.markdown(f"**Saturated Fat:** {orig.get('saturated_fat', 0)}g")
                with add_col2:
                    st.markdown(f"**Sodium:** {orig.get('sodium', 0)}mg")
                    st.markdown(f"**Cholesterol:** {orig.get('cholesterol', 0)}mg")
                    st.markdown(f"**Trans Fat:** {orig.get('trans_fat', 0)}g")

    with detail_col2:
        # Description
        if meal.get("description"):
            st.markdown("### Description")
            st.markdown(meal["description"])

        # Ingredients
        st.markdown("### Ingredients")
        if meal.get("ingredients"):
            ingredients_list = meal["ingredients"].split('\n')
            for ingredient in ingredients_list:
                if ingredient.strip():
                    st.markdown(f"- {ingredient}")
        else:
            st.markdown("*Ingredients not available*")

        # Instructions
        st.markdown("### Instructions")
        if meal.get("instructions"):
            instructions_list = meal["instructions"].split('\n')
            for i, instruction in enumerate(instructions_list, 1):
                if instruction.strip():
                    st.markdown(f"{i}. {instruction}")
        else:
            st.markdown("*Instructions not available*")

        # Recipe URL if available
        if meal.get("recipe_url"):
            st.markdown(f"[View Original Recipe]({meal['recipe_url']})")

        # Action buttons
        action_col1, action_col2, action_col3 = st.columns(3)
        with action_col1:
            st.button("Save Recipe")
        with action_col2:
            st.button("Print Recipe")
        with action_col3:
            st.button("Share Recipe")
else:
    # Pinterest-style masonry grid layout
    cols = st.columns(3)
    for i, meal in enumerate(meals):
        with cols[i % 3]:
            # Handle image display - Using safe_path_exists to prevent type errors
            image_path = meal.get("image")
            if isinstance(image_path, (str, bytes, os.PathLike)) and safe_path_exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.image("https://api.placeholder.com/640/480", use_container_width=True)

            st.markdown(f"#### {meal['name']}")
            st.markdown(f"⭐ {meal['rating']} ({meal['reviews']} ratings) • {meal['user']}")

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
                st.button("View Recipe", key=f"recipe_{i}", on_click=view_meal_details, args=(i,))
            with button_col2:
                # Different button text based on auth status
                if st.session_state.authenticated:
                    st.button("Save", key=f"save_{i}")
                else:
                    if st.button("Login to Save", key=f"login_save_{i}"):
                        st.switch_page("pages/Login.py")

            # Add some spacing between cards
            st.markdown("<br>", unsafe_allow_html=True)

# --- FOOTER ---
st.divider()
st.markdown("© 2025 Leo's Food App | [Terms of Service](/) | [Privacy Policy](/)")