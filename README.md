# Recipes List
## Description
A simple python program using tkinter to display recipes.

The number preceeding the recipe name is the amount that the user has added to their grocery list.
The user can click on the recipe they would like to look at.
Any recipes that are makable (all ingredients are in the user's fridge with sufficient amounts of each) are highlighted in light green.
Any recipes that are added to the user's grocery list (if the user's fridge does not have the sufficient amount of each ingredient, they are added to the to buy list) are highlighted in light blue.
To update the user's grocery list, `Update Grocery List` must be clicked.

<img src="https://github.com/user-attachments/assets/c0c80415-dee1-4204-8267-24212ca7d213" width="510" height="340"/>

The user can easily sort the recipe list by the following:
  - `Recipe Name`: alphabetically
  - `Makable`: if the user has all ingredients in the fridge
  - `Total Cook Time`: ascending


## CSV File Requirements - Recipe List
The csv file for requires the following column names:
  - `name`: (`String`) the name of the recipe
  - `ingredients`: (`String`) a list of ingredients, formatted as `<# of ingredient> <ingredient name>`, each ingredient seperated by commas
  - `prep_time`: (`int`) the prep time in minutes
  - `cook_time`: (`int`) the cook time in minutes
  - `directions`: (`String`) a list of directions, each step seperated by commas
  - `add_to_groceries`: (`int`) determines the amount of the recipe that will be added to the user's grocery list


## Adapting the Code
Adapting the code is simple, the user just needs to change the `RECIPES_FILE` and `GROCERIES_FILE` to the name of their csv files.
When saving, the files are overwritten.

```
RECIPES_FILE = 'recipes.csv'
GROCERIES_FILE = 'groceries.csv'
recipes_list = pd.read_csv(RECIPES_FILE)
grocery_list = pd.read_csv(GROCERIES_FILE)
```
