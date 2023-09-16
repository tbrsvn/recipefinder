import os
os.environ["PYTHONUTF8"] = "1"

from nltk.tokenize import RegexpTokenizer
import tkinter as tk
from tkinter import simpledialog, messagebox
from gooey import Gooey, GooeyParser
import ujson as json
import pkg_resources
import sys
from autocorrect import Speller
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet

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

    print("\nInputted Ingredients:")
    for original, corrected in zip(input_ingredients, corrected_ingredients):
        print(f"{original} (Auto-corrected to: {corrected})")

    recipe_data = load_recipe_data()

    if not recipe_data:
        return

    matching_recipes = find_matching_recipes(recipe_data, corrected_ingredients)

    if not matching_recipes:
        print("No matching recipes found.")
        return

    print("\nMatching recipes:")
    for index, recipe in enumerate(matching_recipes, start=1):
        print(f"{index}. {recipe['recipe'].get('title', 'Title not available')} (Score: {recipe['score']})", flush=True)

    print("\nScoring System:")
    print("The score is based on the number of additional ingredients required for each recipe.")
    print("Lower score indicates a better match with your available ingredients.")
    
    sys.stdout.flush()

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

        sys.stdout.flush()

        create_pdf = messagebox.askyesno("Create PDF", "Do you want to create a PDF of this recipe so you can print it?")
        if create_pdf:
            create_recipe_pdf(selected_recipe)

    elif recipe_number is not None:
        print("\nInvalid recipe number.")

def create_recipe_pdf(recipe):
    try:
        pdf_file = f"{recipe.get('title', 'Recipe')}.pdf"

        if os.path.exists(pdf_file):
            confirm_override = messagebox.askyesno("File Exists", f"'{pdf_file}' already exists. Do you want to override it?")
            if not confirm_override:
                return

        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title = recipe.get('title', 'Title not available')
        title_text = Paragraph(f"<b>Recipe: {title}</b>", styles['Title'])
        story.append(title_text)

        story.append(Spacer(1, 12))

        ingredients_text = "<b>Ingredients:</b><br/>" + "<br/>".join(recipe.get("ingredients", []))
        ingredients = Paragraph(ingredients_text, styles['Normal'])
        story.append(ingredients)

        story.append(Spacer(1, 12))

        directions_label = Paragraph("<b>Directions:</b>", styles['Normal'])
        story.append(directions_label)

        directions = recipe.get("directions", [])
        for i, line in enumerate(directions, start=1):
            direction_text = f"{i}. {line}"
            direction = Paragraph(direction_text, styles['Normal'])
            story.append(direction)

        doc.build(story)
        messagebox.showinfo("PDF Created", f"Recipe PDF '{pdf_file}' created successfully.")
    except Exception as e:
        print(f"Error creating PDF: {e}")
        messagebox.showerror("PDF Error", "An error occurred while creating the PDF.")

if __name__ == "__main__":
    main()
