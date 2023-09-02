from nltk.tokenize import RegexpTokenizer
import tkinter as tk
from tkinter import simpledialog
from gooey import Gooey, GooeyParser
import ujson as json
import pkg_resources
from autocorrect import Speller

spell = Speller()
tokenizer = RegexpTokenizer(r"\w+")

def load_recipe_data():
    try:
        with pkg_resources.resource_stream(__name__, 'recipes.json') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        return {}

def find_matching_recipes(recipe_data, available_ingredients):
    matching_recipes = []

    for recipe_key, recipe_info in recipe_data.items():
        recipe = recipe_info
        recipe_ingredients = tokenizer.tokenize(" ".join(recipe.get("ingredients", [])))
        recipe_ingredients = [ingredient.lower() for ingredient in recipe_ingredients]

        additional_ingredients = [ingredient for ingredient in recipe_ingredients if ingredient not in available_ingredients]
        score = len(additional_ingredients)

        if all(keyword in recipe_ingredients for keyword in available_ingredients):
            matching_recipes.append({"recipe": recipe, "score": score})

    matching_recipes.sort(key=lambda x: x["score"])
    return matching_recipes

@Gooey(program_name="Recipe Finder", default_size=(800, 600))
def main():
    parser = GooeyParser(description="Find recipes based on your available ingredients!")

    parser.add_argument("Available_Ingredients", type=str, help="Comma-separated list of available ingredients")

    args = parser.parse_args()

    input_ingredients = args.Available_Ingredients.split(",")
    corrected_ingredients = [spell(ingredient.strip().lower()) for ingredient in input_ingredients]

    recipe_data = load_recipe_data()

    if not recipe_data:
        return

    matching_recipes = find_matching_recipes(recipe_data, corrected_ingredients)

    if not matching_recipes:
        print("No matching recipes found.")
        return

    print("\nMatching recipes (Sorted by least additional ingredients, lower is better):")
    for index, recipe in enumerate(matching_recipes, start=1):
        print(f"{index}. {recipe['recipe'].get('title', 'Title not available')} (Score: {recipe['score']})")

    root = tk.Tk()
    root.withdraw()
    recipe_number = simpledialog.askinteger("Recipe Selection", "Enter the number of the recipe you want to view:")
    
    if recipe_number is not None and 0 <= recipe_number - 1 < len(matching_recipes):
        selected_recipe = matching_recipes[recipe_number - 1]["recipe"]
        print(f"\nRecipe: {selected_recipe.get('title', 'Title not available')}\n")
        print("Ingredients:")
        for ingredient in selected_recipe.get("ingredients", []):
            print(f"- {ingredient}")
        print("\nDirections:")
        for step, direction in enumerate(selected_recipe.get("directions", []), start=1):
            print(f"{step}. {direction}")
    elif recipe_number is not None:
        print("\nInvalid recipe number.")

if __name__ == "__main__":
    main()