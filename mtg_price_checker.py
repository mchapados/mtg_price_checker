'''
mtg_price_checker.py
by Morgan G. Chapados

Written: March-April, 2022
Updated: April, 2023
'''

import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from mtgsdk import Set

# returns a card name with punctuation removed and spaces replaced with -
def clean(name):
    return name.replace(" // ", "-").replace(" ", "-").replace("'", "").replace(",", "").lower()

# returns the full name of a set given its 3-letter code
def get_set_name(code):
    if code.upper() == 'MOM': # necessary because API is not updated with the latest sets
        return "march-of-the-machine"
    if code.upper() == 'ONE':
        return "phyrexia-all-will-be-one"
    while True:
        try:
            set_name = Set.find(code)
        except:
            continue
        break
    return clean(set_name.name)

# returns the url for a card page on Face to Face's website
# because FTF is annoying, a url may have any one of SIX possible formats (found so far):
# name-set_code || name-number-set_name || name-number-modifier-set_name || name-modifier-set_name || name-set_name || name-modifier-number-set_name
def build_url(name, set_name, number = None, modifier = None):
    url = "https://www.facetofacegames.com/"
    if number == None:
        url + clean(name)
        if modifier != None:
            url += "-" + modifier
        return url + "-" + set_name + "/"
    if modifier == None:
        return url + clean(name) + "-" + str(number) + "-" + set_name + "/"
    return url + clean(name) + "-" + str(number) + "-" + clean(modifier) + "-" + set_name + "/"

# fetches the current price for a card given its url; returns -1 on failure
def get_price(data):
    name, set_code, number = data
    modifiers = ['full-art', 'borderless', 'alternate-art', 'jumpstart-exclusive', 'planar-showcase']
    urls = [build_url(name, get_set_name(set_code), number), build_url(name, get_set_name(set_code)), build_url(name, set_code)]
    price = 0.0
    found = False
    
    for url in urls:
        try:
            df = pd.read_csv(url, sep="\n", header=None) # read the card page from Face to Face
        except:
            continue # if first url fails to find, try the next
        found = True # if we found the card, stop searching
        break 
    if not found: # if both urls failed, try with modifiers
        for mod in modifiers:
            urls = [build_url(name, get_set_name(set_code), number, mod), build_url(name, get_set_name(set_code), None, mod), build_url(name+"-"+mod, get_set_name(set_code), number)]
            for url in urls:
                try:
                    df = pd.read_csv(url, sep="\n", header=None) # get the card price from Face to Face
                except:
                    continue # if  modifier fails to find, try the next
                found = True # if we found the card, stop searching
                break 
            if found:
                break
    if not found: # if none of the urls worked, give up
        print(f"{name} could not be found")
        return price
    
    # this part extracts the actual price from the webpage
    for j in df.index:
        if '<meta itemprop="price"' in df[0][j]:
            start = df[0][j].find("content") + 9
            end = df[0][j].find(">", start) - 1
            price = float(df[0][j][start:end])
            print(f"Price for {name}: $ {price}")
            break
    return price

def import_csv(filename):
    return pd.read_csv(filename)

if __name__ == '__main__':
    # display the menu and get the user's selection
    while True:
        print("Select an Option: \n1: Import a CSV file \n2: Input cards one at a time \n3: Exit")
        choice = input(">> ")
        try:
            choice = int(choice)
        except:
            continue
        if choice == 3:
            exit()
        if choice == 1 or choice == 2:
            break
    
    # read card list from CSV file
    if choice == 1: 
        print("NOTE: your file must be in the same folder as this program, and you must include the extension." 
            "\n(Or you can input an absolute path to a file stored anywhere.)")
        filename = input("Enter filename >> ")
        try:
            card_list = import_csv(filename)
        except:
            print(f"ERROR: {filename} could not be opened.")
            exit()
        if 'name' not in card_list.columns or 'set' not in card_list.columns or 'number' not in card_list.columns:
            print("ERROR: Wrong format. Your CSV file must have columns named 'name', 'set', and 'number'. Please edit your file and try again.")
            exit()
    
    # input cards one at a time
    if choice == 2: 
        card_list = pd.DataFrame()
        card_list['name']   = ''
        card_list['set']    = ''
        card_list['number'] = ''
        card_list['count']  = ''
        print("Press ENTER (leaving name field blank) at any time to stop inputting cards." 
            "\nNOTES: Input is not case-sensitive. Punctuation is optional." 
            "\n       Double-faced cards must include both names separated by //." 
            "\n       If the number is not printed on the card (for older cards), leave blank.")
        while True:
            name     = input("Card Name >> ")
            if name == '':
                break
            set_code = input("Set Code >> ")
            number   = int(input("Card Number >> "))
            count    = int(input("Count >> "))
            card_data = pd.DataFrame({
                "name":   [name],
                "set":    [set_code],
                "number": [number],
                "count":  [count]
            })
            card_list = pd.concat([card_list, card_data], ignore_index=True)

    # get prices for each card in the list
    print("Searching...")
    with ThreadPoolExecutor(6) as tp:
        card_list['price'] = list(tp.map(get_price, zip(card_list['name'], card_list['set'], card_list['number'])))

    # set count column and calculate total prices
    if 'count' not in card_list.columns:
        card_list['count'] = 1
    card_list['total_price'] = card_list['price'] * card_list['count']
    # output the total price for the list
    print("\nTotal price for all cards: $ {:.2f}".format(sum(card_list['total_price'])))

    choice = input("Write data to a file? (Y/N) >> ")
    if choice.upper() == 'Y':
        print("NOTE: if filename already exists, it will be overwritten. \nDo not enter the file extension.")
        filename = input("Enter filename >> ") + ".csv"
        card_list.to_csv(filename)