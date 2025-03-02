import streamlit as st
import pandas as pd
import os
from PIL import Image

# Page configuration
st.set_page_config(page_title="Community Meals - Leo's Food App", page_icon="🐱", layout="wide")
st.logo(image="images/logo.png", size="large", link=None, icon_image=None)
# --- SIDEBAR NAVIGATION ---
# st.sidebar.title("Navigation")
# st.sidebar.page_link("Home.py", label="🏠 Home", icon="🏠")
# st.sidebar.page_link("pages/About_Leo's_Kitchen.py", label="ℹ️ About Me")
# st.sidebar.page_link("pages/My_Recipe.py", label="📊 My Recipes")
# st.sidebar.page_link("pages/Leo_Chat_Bot.py", label="🤖 Chat Bot")
# st.sidebar.page_link("pages/Share_Your_Meal.py", label="📝 Share Your Meal")
# st.sidebar.page_link("pages/Meal_Feed.py", label="🍽️ Community Meals")

# --- MEAL FEED ---
st.title("Community Meals 🍽️")
st.write("Check out meals shared by the community!")

# Filter options
st.sidebar.header("Filter Meals")
try:
    # Load meals data
    meals_df = pd.read_csv("data/meals.csv")

    if not meals_df.empty:
        # Get unique categories for filter
        categories = ["All"] + list(meals_df["meal_category"].unique())
        selected_category = st.sidebar.selectbox("Category", categories)

        # Filter by category
        if selected_category != "All":
            filtered_meals = meals_df[meals_df["meal_category"] == selected_category]
        else:
            filtered_meals = meals_df

        # Sort options
        sort_option = st.sidebar.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Highest Protein", "Lowest Calories"]
        )

        if sort_option == "Newest First":
            filtered_meals = filtered_meals.sort_values("datetime", ascending=False)
        elif sort_option == "Oldest First":
            filtered_meals = filtered_meals.sort_values("datetime", ascending=True)
        elif sort_option == "Highest Protein":
            filtered_meals = filtered_meals.sort_values("protein", ascending=False)
        elif sort_option == "Lowest Calories":
            filtered_meals = filtered_meals.sort_values("calories", ascending=True)

        # Display meals
        if not filtered_meals.empty:
            for index, meal in filtered_meals.iterrows():
                with st.container():
                    st.markdown("---")
                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # Display image if available
                        # Fix: Check if image_path exists and is a valid string path
                        if "image_path" in meal and meal["image_path"] and isinstance(meal["image_path"],
                                                                                      str) and os.path.exists(
                                meal["image_path"]):
                            try:
                                st.image(meal["image_path"], use_container_width=True)
                            except:
                                st.image("https://via.placeholder.com/400x300?text=No+Image", use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/400x300?text=No+Image", use_container_width=True)

                    with col2:
                        st.markdown(f"### {meal['meal_name']}")
                        st.markdown(f"**Category:** {meal['meal_category']}")

                        # Display tags if available
                        if not pd.isna(meal.get('meal_tags', '')):
                            tags = [tag.strip() for tag in meal['meal_tags'].split(',')]
                            st.markdown(" ".join([f"*{tag}*" for tag in tags]))

                        st.markdown(f"**Description:** {meal['meal_description']}")

                        # Nutrition section
                        st.markdown("#### Nutrition Facts")
                        st.markdown(
                            f"**Protein:** {meal['protein']}g | **Carbs:** {meal['carbs']}g | **Fat:** {meal['fat']}g | **Calories:** {meal['calories']}")

                        # Recipe link if available
                        if not pd.isna(meal.get('recipe_url', '')) and meal['recipe_url']:
                            st.markdown(f"[View Full Recipe]({meal['recipe_url']})")

                        # View details button
                        if st.button(f"View Details", key=f"view_{index}"):
                            st.session_state.selected_meal = meal

                    # If meal is selected, show details
                    if 'selected_meal' in st.session_state and st.session_state.selected_meal is not None and st.session_state.selected_meal.equals(
                            meal):
                        with st.expander("Meal Details", expanded=True):
                            # Ingredients
                            st.subheader("Ingredients")
                            ingredients_list = meal['ingredients'].split('\n')
                            for ingredient in ingredients_list:
                                st.markdown(f"- {ingredient}")

                            # Instructions
                            st.subheader("Instructions")
                            instructions_list = meal['instructions'].split('\n')
                            for i, instruction in enumerate(instructions_list, 1):
                                st.markdown(f"{i}. {instruction}")

                            # Additional nutrition info if available
                            st.subheader("Detailed Nutrition")
                            nutrition_col1, nutrition_col2 = st.columns(2)

                            with nutrition_col1:
                                st.markdown(f"**Fiber:** {meal.get('fiber', 0)}g")
                                st.markdown(f"**Sugar:** {meal.get('sugar', 0)}g")
                                st.markdown(f"**Saturated Fat:** {meal.get('saturated_fat', 0)}g")

                            with nutrition_col2:
                                st.markdown(f"**Sodium:** {meal.get('sodium', 0)}mg")
                                st.markdown(f"**Cholesterol:** {meal.get('cholesterol', 0)}mg")
                                st.markdown(f"**Trans Fat:** {meal.get('trans_fat', 0)}g")
        else:
            st.info("No meals match your filter criteria.")
    else:
        st.info("No meals have been shared yet. Be the first to share your meal!")
except FileNotFoundError:
    st.info("No meals have been shared yet. Be the first to share your meal!")