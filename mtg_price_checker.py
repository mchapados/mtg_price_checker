'''
mtg_price_checker.py
by Morgan Chapados
March-April, 2022

This program gets a list of Magic: the Gathering (MTG) cards from one source on
the web, then looks up the current price (in Canadian dollars) for each card 
from a second source.
'''

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

# get the decklist from MTG Goldfish and put it in a dataframe
deck_url = "https://www.mtggoldfish.com/deck/download/4628878"
decklist = pd.read_csv(deck_url, sep="\n", header=None, names=["card"])
# separate the count and card name into two columns
# Note: count must be no more than 2 digits (i.e. between 0-99)
decklist['count'] = decklist['card'].str[0:2].astype(int)
decklist['card'] = decklist['card'].str[2:]
decklist['card'] = decklist['card'].str.strip() # trim any whitespace

# cards with any of these names are free (because most MTG players already have 
# piles of them and many local card shops will give them to new players)
basic_lands = {"Island", "Mountain", "Plains", "Swamp", "Forest"}

# this function looks up the price for a card, and returns that price * number
# of copies in the decklist
def process_card(data):
    card, count = data
    price = 0.0 # basic lands are $0.00
    if (card not in basic_lands):
        # search Wizard Tower for a card based on its name and save search
        # result to a dataframe
        df = pd.read_html("https://www.kanatacg.com/products/search?query={}"
            .format(card.replace(" ", "+")))
        # pull out the card price and multiply by count
        price = round(float(df[2][1][0][5:]) * count, 2)
    # output the price for each card
    print("price for {} {}: ${:.2f}".format(count, card, price))
    return price

# call the above function on each card in the decklist and save the prices
with ThreadPoolExecutor(6) as tp:
    decklist['price'] = list(tp.map(process_card, zip(decklist['card'], decklist['count'])))

# output the total price for the deck
print("\ntotal price: ${:.2f}".format(sum(decklist['price'])))

# create a column for price per copy (to use in visualization below)
decklist['price_each'] = decklist['price'] / decklist['count']

# this part visualizes the data as a scatter plot, showing number of copies X 
# card price per copy (gives the user an idea of how many expensive vs. cheap
# cards are in the decklist)
np.random.seed(13)
colours = np.random.rand(len(decklist))
plt.scatter(decklist['count'], decklist['price_each'], s=200, c=colours, alpha=0.5)
plt.title("Cards by Price", fontdict={'fontweight':'bold'})
plt.xlabel("Number of Copies", fontdict={'fontweight':'bold'})
plt.ylabel("Card Price (per Copy)", fontdict={'fontweight':'bold'})
plt.show()
