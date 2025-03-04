"""Recipes List - Created by Samantha Song - Started 2025.02.11"""
# Takes a csv file of recipes and csv file of grocery list
# Allows user to:
#   Find recipes they can make
#   Add ingredients to grocery list for recipes user wants to make
#   Allow multiple recipes (add to amount rather than replace)
#   If ingredient is in fridge, but need more, do math to find amount needed

# Recipes CSV: name,ingredients,prep_time,cook_time,directions,add_to_groceries
# Groceries CSV: food,food_type,is_stocked,is_low,need_to_buy,amount,in_cart

# Imports
import tkinter as tk
from tkinter import ttk
from tkinter import font
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
    return np.isin(which_list[column_name].values, looking_for).any()

def added_to_groceries(which_list, looking_for):
    """Returns number of added_to_groceries is added to grocery list"""
    food_index = get_index(which_list, looking_for, 'name')
    return which_list.at[food_index, 'add_to_groceries']

def get_ingredients(recipe_book, which_recipe, to_add=False):
    """Returns 2d array of ingredient amount and name"""
    if is_in_list(recipe_book, which_recipe, 'name'):
        # List of ingredients in one string
        ing_index = get_index(recipe_book, which_recipe, 'name')
        ing_list = recipe_book.at[ing_index, 'ingredients']
        # Splits ingredients by comma
        ing_list = ing_list.split(',')
        # Initialize array to be returned
        ing_array = np.empty((0, 2))
        # to_add is for add_to_groceries
        recipe_amount = 1
        if to_add:
            recipe_amount = recipe_book.at[ing_index, 'add_to_groceries']
        # For each ingredient string, split into amount and ingredient name
        for _, ing in enumerate(ing_list):
            if ing[0] == ' ':
                ing = ing[1:]
            space_index = ing.find(' ')
            ing_amount = int(ing[:space_index]) * int(recipe_amount)
            ing_name = ing[space_index + 1:]
            ing_array = np.append(ing_array, np.array([[ing_amount, ing_name]]), axis=0)
        return ing_array
    return np.empty((0, 2))

def get_groceries(all_groceries, where):
    """Returns 2d array of item amount and name that are in_stock"""
    groc_list = all_groceries.loc[all_groceries[where]]
    which_amount = 'stocked_num'
    if where == 'need_to_buy':
        which_amount = 'buy_num'
    groc_array = np.empty((0, 2))
    for _, row in groc_list.iterrows():
        groc_amount = row.loc[which_amount]
        groc_name = row.loc['food']
        groc_array = np.append(groc_array, np.array([[groc_amount, groc_name]]), axis=0)
    return groc_array

def get_directions(recipe_book, which_recipe):
    """Returns 2d array of step number and direction given recipe name"""
    if is_in_list(recipe_book, which_recipe, 'name'):
        # List of directions in one string
        directions = recipe_book.at[get_index(recipe_book, which_recipe, 'name'),
                                    'directions']
        # Splits directions by commas
        directions = directions.split(',')
        direction_array = np.empty((0, 2))
        for num, step in enumerate(directions):
            if step[0] == ' ':
                step = step[1:]
            direction_array = np.append(direction_array,
                                        np.array([[int(num+1), step]]),
                                        axis=0)
        return direction_array

def num_missing_ing(recipe_book, which_recipe, all_groceries, which_food):
    """Returns an int representing the number of which_food missing to make which_recipe"""
    num_missing = 0
    ingredients_list = get_ingredients(recipe_book, which_recipe)
    stocked_list = get_groceries(all_groceries, 'is_stocked')
    if which_food in ingredients_list:
        ing_x_ind, _ = np.where(ingredients_list == which_food)
        ing_amount = int(ingredients_list[ing_x_ind[0]][0])
        if which_food in stocked_list:
            groc_x_ind, _ = np.where(stocked_list == which_food)
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

def is_makable(recipe_book, which_recipe, all_groceries):
    """Returns boolean representing if which_recipe is makable"""
    if is_in_list(recipe_book, which_recipe, 'name'):
        if makable_percentage(recipe_book, which_recipe, all_groceries) == 1.0:
            return True
    return False

def find_makeable(recipe_book, all_groceries):
    """Returns 1d array of names of recipes that are makable with items in fridge"""
    makeable_recipes = np.array([])
    for _, recipe in recipe_book.iterrows():
        recipe_name = recipe.loc['name']
        if is_makable(recipe_book, recipe_name, all_groceries):
            makeable_recipes = np.append(makeable_recipes, np.array([recipe_name]))
    return makeable_recipes

def sort_by_makable(recipe_book, all_groceries):
    """Given recipes_list and groceries_list, returns sorted reciepes by makablity"""
    indexes = np.empty((0, 3)) # index, makable %, # missing
    for index, recipe in recipe_book.iterrows():
        recipe_name = recipe['name']
        # ind = get_index(recipe_book, recipe_name, 'name')
        make_per = makable_percentage(recipe_book, recipe_name, all_groceries)
        num_miss = total_missing_ing(recipe_book, recipe_name, all_groceries)
        indexes = np.append(indexes, np.array([[index, make_per, num_miss]]), axis=0)
    # Sort by % makable
    indexes = indexes[indexes[:, 1].argsort()][::-1]
    # Sort by missing ingredients
    indexes = indexes[indexes[:, 2].argsort()]
    # Sort and return recipe_book
    indexes = indexes[:, 0]
    indexes = np.transpose(indexes)
    recipe_book = recipe_book.reindex(indexes)
    return recipe_book

def add(sorted_index, which_listbox, recipe_amount):
    """Add to Groceries"""
    global recipes_list, grocery_list
    try:
        recipe_amount = int(recipe_amount)
        recipe = recipes_list.take([sorted_index[0]])['name'].values[0]
        recipe_index = get_index(recipes_list, recipe, 'name')
        recipes_list.at[recipe_index, 'add_to_groceries'] = recipe_amount
        update_scroll_list(which_listbox, recipes_list, grocery_list)
    except ValueError:
        return 0

def remove(sorted_index, which_listbox):
    """Remove from Groceries"""
    global recipes_list, grocery_list
    try:
        recipe = recipes_list.take([sorted_index[0]])['name'].values[0]
        recipe_index = get_index(recipes_list, recipe, 'name')
        recipes_list.at[recipe_index, 'add_to_groceries'] = 0
        update_scroll_list(which_listbox, recipes_list, grocery_list)
    except IndexError:
        return 0

def consolidate(ing_list1, ing_list2):
    """Takes 2 ingredient lists and consolidates into one list, adding amounts"""
    for ing in ing_list2:
        # ing[0] = amount, ing[1] = name
        if np.isin(ing_list1[:,1], ing[1]).any():
            row, _ = np.where(ing_list1 == ing[1])
            row = row[0]
            ing_list1[row][0] = int(ing_list1[row][0]) + int(ing[0])
        else:
            ing_list1 = np.append(ing_list1, np.array([ing]), axis=0)
    return ing_list1

def update_groceries(recipe_book):
    """Updates groceries to add ingredients to grocery csv"""
    global grocery_list
    recipes_to_make = recipe_book[recipe_book['add_to_groceries']>0]['name'].values
    all_ingredients = np.empty((0,2))
    grocery_list['add_buy_num'] = 0
    for recipe_name in recipes_to_make:
        recipe_ingredients = get_ingredients(recipe_book, recipe_name, to_add=True)
        all_ingredients = consolidate(all_ingredients, recipe_ingredients)
    for ingredient in all_ingredients:
        ing_name = ingredient[1]
        ing_amount = int(ingredient[0])
        # If ingredient is in grocery list
        if is_in_list(grocery_list, ing_name, 'food'):
            ing_index = get_index(grocery_list, ing_name, 'food')
            # If ingredient is stocked
            if grocery_list.at[ing_index, 'is_stocked']:
                stocked_amount = grocery_list.at[ing_index, 'stocked_num']
                add_amount = ing_amount - stocked_amount
                # If amount stocked is not sufficient
                if add_amount > 0:
                    grocery_list.at[ing_index, 'need_to_buy'] = True
                    grocery_list.at[ing_index, 'add_buy_num'] = add_amount
            # If ingredient is in to buy list
            elif grocery_list.at[ing_index, 'need_to_buy']:
                grocery_list.at[ing_index, 'add_buy_num'] = ing_amount
            # If ingredient is in past items
            else:
                grocery_list.at[ing_index, 'need_to_buy'] = True
                grocery_list.at[ing_index, 'add_buy_num'] = ing_amount
        # If ingredient is not in grocery list
        else:
            new_item = [ing_name, '', False, 0, True, 0, False, ing_amount]
            grocery_list.loc[len(grocery_list)] = new_item
    # Save to csv files
    grocery_list.to_csv(GROCERIES_FILE, index=False)
    recipe_book.to_csv(RECIPES_FILE, index=False)

# Tkinter Functions Functions
def create_scroll_list(root, recipe_book, all_groceries):
    """Create a Scrollbar and Listbox"""
    frame = tk.Frame(root)
    list_scroll = tk.Scrollbar(frame)
    list_scroll.pack(side=tk.RIGHT)
    # Listboxes
    list_box = tk.Listbox(frame, yscrollcommand=list_scroll.set)
    update_scroll_list(list_box, recipe_book, all_groceries)
    list_box.pack(side=tk.LEFT)
    list_scroll.config(command=list_box.yview)
    return frame, list_box

def create_scroll_tb(root):
    """Create Textbox to show recipe instructions"""
    frame = tk.Frame(root)
    tb_scroll = tk.Scrollbar(frame)
    tb_scroll.pack(side=tk.RIGHT)
    # Textbox
    small_font = font.Font(family='Segoe UI', size=12)
    textbox = tk.Text(frame, wrap='word', state='disabled', font=small_font,
                      width=25, height=11)
    textbox.pack(side=tk.LEFT)
    return frame, textbox

def update_scroll_list(which_listbox, recipe_book, all_groceries):
    """Update Listbox"""
    which_listbox.delete(0, tk.END)
    index = 0
    for _, recipe in recipe_book.iterrows():
        recipe_name = recipe['name']
        recipe_amount = recipe['add_to_groceries']
        recipe_string = str(recipe_amount) + ' ' + recipe_name
        which_listbox.insert(tk.END, recipe_string)
        # Highlights makable recipes
        if is_makable(recipe_book, recipe_name, all_groceries):
            which_listbox.itemconfig(index, bg='#C6DAAD')
        if added_to_groceries(recipe_book, recipe_name,):
            which_listbox.itemconfig(index, bg='#D0E6F5')
        index += 1
    return 0

def show_selected_recipe(recipe_book, textbox, sorted_index):
    """Show instructions for selected recipe"""
    textbox.config(state=tk.NORMAL)
    textbox.delete(1.0, tk.END)
    recipe = recipe_book.take([sorted_index])['name'].values[0]
    recipe_index = get_index(recipe_book, recipe, 'name')
    ingredients = get_ingredients(recipe_book, recipe)
    directions = get_directions(recipe_book, recipe)
    prep_time = '\nPrep Time: ' + str(recipe_book.loc[recipe_index, 'prep_time']) + '\n'
    cook_time = 'Cook Time: ' + str(recipe_book.loc[recipe_index, 'cook_time']) + '\n'
    textbox.insert(tk.END, recipe.upper())
    textbox.insert(tk.END, prep_time)
    textbox.insert(tk.END, cook_time)
    textbox.insert(tk.END, '\nIngredients:\n')
    for _, ing in enumerate(ingredients):
        textbox.insert(tk.END, str(ing[0]) + ' ' + ing[1] + '\n')
    textbox.insert(tk.END, '\nDirections:\n')
    for _, step in enumerate(directions):
        textbox.insert(tk.END, str(step[0]) + ') ' + step[1] + '\n')
    textbox.config(state=tk.DISABLED)

def on_select(selected, textbox, recipe_book):
    """Shows instructions for selected recipe"""
    if len(selected) == 1:
        show_selected_recipe(recipe_book, textbox, selected[0])

def sort(sort_criteria, listbox):
    """Sort function"""
    global recipes_list, grocery_list
    if sort_criteria == 'Recipe Name':
        recipes_list = recipes_list.sort_values(by='name')
    elif sort_criteria == 'Total Cook Time':
        recipes_list['total_time'] = recipes_list['cook_time'] + recipes_list['prep_time']
        recipes_list = recipes_list.sort_values(by='total_time')
        recipes_list = recipes_list.drop('total_time', axis=1)
    elif sort_criteria == 'Makable':
        recipes_list = sort_by_makable(recipes_list, grocery_list)
    update_scroll_list(listbox, recipes_list, grocery_list)

# Tkinter
def main():
    """Main Loop - Tkinter"""
    global recipes_list, grocery_list

    # Initialize Screen
    root = tk.Tk()
    root.title("Recipes")
    screen_w = 800
    screen_h = 600
    button_w = 10
    button_h = 1
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
                                               'Total Cook Time'])
    sort_by.set('Makable')
    sort_by.pack(side=tk.LEFT)

    # Recipe List and Recipe - Frame, Label, Scrollable ListBox
    list_recipe_frame = tk.Frame(root)
    list_recipe_frame.pack(side=tk.TOP, padx=padding, pady=padding)
    list_frame = tk.Frame(list_recipe_frame)
    list_frame.pack(side=tk.LEFT, padx=padding, pady=padding)
    recipe_frame = tk.Frame(list_recipe_frame)
    recipe_frame.pack(side=tk.LEFT, padx=padding, pady=padding)

    tk.Label(list_frame, text='Recipes List').pack(side=tk.TOP)
    tk.Label(recipe_frame, text='Selected Recipe').pack(side=tk.TOP)

    recipe_lb_frame, recipe_tb = create_scroll_tb(recipe_frame)
    recipe_lb_frame.pack(side=tk.TOP, padx=padding, pady=padding)

    list_lb_frame, list_lb = create_scroll_list(list_frame, recipes_list, grocery_list)
    list_lb_frame.pack(side=tk.TOP, padx=padding, pady=padding)
    list_lb.bind('<<ListboxSelect>>', lambda event: on_select(list_lb.curselection(),
                                                              recipe_tb, recipes_list))

    # Add/Remove - Frame, Label
    add_remove_frame = tk.Frame(root)
    add_remove_frame.pack(side=tk.TOP, padx=padding, pady=padding)
    tk.Label(add_remove_frame, text='Amount: ').pack(side=tk.LEFT)
    add_amount = tk.Entry(add_remove_frame)
    add_amount.pack(side=tk.LEFT, padx=padding)

    # Update - Frame, Label
    update_frame = tk.Frame(root)
    update_frame.pack(side=tk.TOP, padx=padding)

    # Buttons
    sort_button = tk.Button(sort_frame, text="Sort",
                            width=button_w, height=button_h,
                            command= lambda: sort(sort_by.get(), list_lb))
    sort_button.pack(side=tk.LEFT, padx=padding, pady=padding)

    add_button = tk.Button(add_remove_frame, text="Add to Groceries",
                           width=button_w*2, height=button_h,
                           command=lambda: add(list_lb.curselection(), list_lb, add_amount.get()))
    add_button.pack(side=tk.LEFT, padx=padding, pady=padding)

    remove_button = tk.Button(add_remove_frame, text="Remove from Groceries",
                              width=button_w*2, height=button_h,
                              command=lambda: remove(list_lb.curselection(), list_lb))
    remove_button.pack(side=tk.LEFT, padx=padding, pady=padding)

    update_button = tk.Button(update_frame, text="Update Grocery List",
                              width=button_w*2, height=button_h,
                              command=lambda: update_groceries(recipes_list))
    update_button.pack(side=tk.LEFT, padx=padding)

    # Main Loop
    root.mainloop()

# Start Program
if __name__ == "__main__":
    main()
