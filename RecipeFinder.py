from nltk.tokenize import RegexpTokenizer
import tkinter as tk
from tkinter import simpledialog
from gooey import Gooey, GooeyParser
import ujson as json

tokenizer = RegexpTokenizer(r"\w+")

# Load recipe data from a single JSON file
def load_recipe_data(file_path):
    with open(file_path, "r") as file:
        recipe_data = json.load(file)
    return recipe_data

# Filter recipes based on available ingredients
def find_matching_recipes(recipe_data, available_ingredients):
    matching_recipes = []
    for recipe_key, recipe_info in recipe_data.items():
        recipe = recipe_info["json"]
        recipe_ingredients = tokenizer.tokenize(" ".join(recipe["ingredients"]))
        recipe_ingredients = [ingredient.lower() for ingredient in recipe_ingredients]
        if all(keyword in recipe_ingredients for keyword in available_ingredients):
            matching_recipes.append(recipe)
    return matching_recipes

# Display matching recipes
def display_recipes(recipes):
    if not recipes:
        print("No matching recipes found.")
    else:
        print("Matching recipes:")
        for index, recipe in enumerate(recipes, start=1):
            print(f"{index}. {recipe['title']}", flush=True)

def display_recipe_details(recipe):
    print(f"\nRecipe: {recipe['title']}\n")
    print("Ingredients:")
    for ingredient in recipe["ingredients"]:
        print(f"- {ingredient}")
    print("\nDirections:")
    for step, direction in enumerate(recipe["directions"], start=1):
        print(f"{step}. {direction}")

@Gooey(program_name="Recipe Finder", default_size=(800, 600))
def main():
    parser = GooeyParser(description="Find recipes based on your available ingredients!")

    parser.add_argument("Available_Ingredients", type=str, help="Comma-separated list of available ingredients")

    args = parser.parse_args()

    Available_Ingredients = [ingredient.strip().lower() for ingredient in args.Available_Ingredients.split(",")]

    # Load recipe data from the specified JSON file
    recipe_data = load_recipe_data("recipes.json")

    # Find matching recipes
    matching_recipes = find_matching_recipes(recipe_data, Available_Ingredients)

    # Display matching recipes
    display_recipes(matching_recipes)

    if matching_recipes:
        root = tk.Tk()
        root.iconbitmap("icon.ico")
        root.withdraw()  # Hide the main GUI window
        recipe_number = simpledialog.askinteger("Recipe Selection", "Enter the number of the recipe you want to view:")
        if recipe_number is not None and 0 <= recipe_number - 1 < len(matching_recipes):
            selected_recipe = matching_recipes[recipe_number - 1]
            display_recipe_details(selected_recipe)
        elif recipe_number is not None:
            print("Invalid recipe number.")

if __name__ == "__main__":
    main()