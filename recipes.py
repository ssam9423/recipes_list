"""Recipes List - Created by Samantha Song - Started 2025.02.11"""
# Takes a csv file of recipes and csv file of grocery list
# Allows user to:
#   Find recipes they can make
#   Add ingredients to grocery list for recipes user wants to make
#   Allow multiple recipes (add to amount rather than replace)
#   If ingredient is in fridge, but need more, do math to find amount needed

# Recipes CSV: name,ingredients,prep_time,cook_time,directions
# Groceries CSV: food,food_type,is_stocked,is_low,need_to_buy,amount,in_cart

# Imports
import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np

RECIPES_FILE = 'recipes.csv'
GROCERIES_FILE = 'groceries.csv'
recipes_list = pd.read_csv(RECIPES_FILE)
grocery_list = pd.read_csv(GROCERIES_FILE)

# Functions
def get_index(which_list, looking_for, column_name):
    """Returns index of food_name in which_list"""
    return which_list.loc[which_list[column_name] == looking_for].index[0]

def is_in_list(which_list, looking_for, column_name):
    """Checks if looking_for is in column_name in which_list"""
    return np.isin(which_list[column_name].values, looking_for)[0]

def get_ingredients(recipe_book, which_recipe):
    """Returns 2d array of ingredient amount and name"""
    if is_in_list(recipe_book, which_recipe, 'name'):
        # List of ingredients in one string
        ing_list = recipe_book.at[get_index(recipe_book, which_recipe, 'name'),
                                  'ingredients']
        # Splits ingredients by comma
        ing_list = ing_list.split(',')
        # Initialize array to be returned
        ing_array = np.empty((0, 2))
        # For each ingredient string, split into amount and ingredient name
        for _, ing in enumerate(ing_list):
            if ing[0] == ' ':
                ing = ing[1:]
            space_index = ing.find(' ')
            ing_amount = ing[:space_index]
            ing_name = ing[space_index + 1:]
            ing_array = np.append(ing_array, np.array([[ing_amount, ing_name]]), axis=0)
        return ing_array
    return np.empty((0, 2))

def get_groceries(all_groceries, where):
    """Returns 2d array of item amount and name that are in_stock"""
    groc_list = all_groceries.loc[all_groceries[where]]
    groc_array = np.empty((0, 2))
    for _, row in groc_list.iterrows():
        groc_amount = row.loc['amount']
        groc_name = row.loc['food']
        groc_array = np.append(groc_array, np.array([[groc_amount, groc_name]]), axis=0)
    return groc_array

def num_missing_ing(recipe_book, which_recipe, all_groceries, which_food):
    """Returns an int representing the number of which_food missing to make which_recipe"""
    num_missing = 0
    ingredients_list = get_ingredients(recipe_book, which_recipe)
    stocked_list = get_groceries(all_groceries, 'is_stocked')
    if which_food in ingredients_list:
        ing_x_ind, ing_y_ind = np.where(ingredients_list == which_food)
        ing_amount = int(ingredients_list[ing_x_ind[0]][0])
        if which_food in stocked_list:
            groc_x_ind, groc_y_ind = np.where(stocked_list == which_food)
            groc_amount = int(stocked_list[groc_x_ind[0]][0])
            if ing_amount > groc_amount:
                num_missing = ing_amount - groc_amount
        else:
            num_missing = ing_amount
    return num_missing

def get_comparison_array(recipe_book, which_recipe, all_groceries):
    """Returns 2d array of booleans representing if item is in fridge & has enough"""
    ingredients_list = get_ingredients(recipe_book, which_recipe)
    stocked_list = get_groceries(all_groceries, 'is_stocked')
    can_make_array = np.empty((0, 2))
    for _, ing_row in enumerate(ingredients_list):
        ing_name = ing_row[1]
        amount_match = False
        name_match = False
        if ing_name in stocked_list:
            name_match = True
            if num_missing_ing(recipe_book, which_recipe, all_groceries, ing_name) == 0:
                amount_match = True
        can_make_array = np.append(can_make_array, np.array([[amount_match, name_match]]), axis=0)
    return can_make_array

def total_missing_ing(recipe_book, which_recipe, all_groceries):
    """Returns int representing the total number of missing ingredients for which_recipe"""
    ingredients_list = get_ingredients(recipe_book, which_recipe)
    total_missing = 0
    for _, ing_row in enumerate(ingredients_list):
        ing_name = ing_row[1]
        total_missing += num_missing_ing(recipe_book, which_recipe, all_groceries, ing_name)
    return total_missing

def total_num_ing(recipe_book, which_recipe):
    """Returns int representing the total number of ingredients for which_recipe"""
    ingredients_list = get_ingredients(recipe_book, which_recipe)
    total_ing = 0
    for _, ing_row in enumerate(ingredients_list):
        total_ing += int(ing_row[0])
    return total_ing

def makable_percentage(recipe_book, which_recipe, all_groceries):
    """Returns float representing percentage of makability given which_recipe"""
    makable_perc = 0.0
    if is_in_list(recipe_book, which_recipe, 'name'):
        missing = total_missing_ing(recipe_book, which_recipe, all_groceries)
        total = total_num_ing(recipe_book, which_recipe)
        makable_perc = (total - missing) / total
    return makable_perc

def find_makeable(recipe_book, all_groceries):
    """Returns 1d array of names of recipes that are makable with items in fridge"""
    makeable_recipes = np.array([])
    for _, recipe in recipe_book.iterrows():
        recipe_name = recipe.loc['name']
        if makable_percentage(recipe_book, recipe_name, all_groceries) == 1.0:
            makeable_recipes = np.append(makeable_recipes, np.array([recipe_name]))
    return makeable_recipes

# Sorting by Makable:
#   Have all ingrdients & amounts
#   Missing 1 ingredient
#   Missing 2 ingredients, etc, etc

def sort_by_makable(recipe_book, all_groceries):
    """Given recipes_list and groceries_list, returns sorted reciepes by makablity"""
    return np.array([])

def sort_by(recipe_book, sort_criteria):
    """Basic Sort Function - database defaults"""
    if sort_criteria in recipe_book.columns:
        recipe_book = recipe_book.sort_values(by=sort_criteria)
    if sort_criteria == 'Total Cook Time':
        recipe_book = recipe_book.sort_values(by='prep_time', key=recipe_book['cook_time'].add)
    return recipe_book

# Tkinter
def main():
    """Tkinter Window"""
    # Initialize Screen
    root = tk.Tk()
    root.title = 'Recipes'
    screen_w = 800
    screen_h = 600
    button_w = 10
    padding = int(screen_w/100)
    screen_size = str(screen_w) + 'x' + str(screen_h)
    root.geometry(screen_size)

    # Title - Frame, Label
    title_frame = tk.Frame(root)
    tk.Label(title_frame, text='Recipes').pack()
    title_frame.pack()

    # Sort - Frame, Label, ComboBox
    # Allow Sorting by: Alphabetical, Makable, # Ingredients, Total Cook Time
    sort_frame = tk.Frame(root)
    sort_frame.pack(side=tk.TOP)
    tk.Label(sort_frame, text='Sort By: ').pack(side=tk.LEFT)
    sort_by = ttk.Combobox(sort_frame, values=['Recipe Name', 'Makable',
                                               '# of Ingredients', 'Total Cook Time'])
    sort_by.set('Makable')
    sort_by.pack(side=tk.LEFT)

    # Main Loop
    root.mainloop()

# Start Program
if __name__ == "__main__":
    main()
