# Magic: the Gathering Price Checker

## Project Summary

Many Magic: the Gathering (MTG) players are concerned about the prices of cards, especially because card prices are arbitrary, fluctuate widely, and change often. For example, card prices tend to range from $0.25 to $50.00 or more, with some worth hundreds or even thousands of dollars, and a card that costs $1.00 today could cost $20.00 next month, or vice versa.

This program is a tool that MTG players could use to efficiently price out a list of cards without having to manually look up each one, a process that can be very time-consuming if they’re interested in the prices of many different cards.

The program pulls current price data from Face to Face Games (https://www.facetofacegames.com/), a Canadian online retailer.

NOTE: This program can only find prices for near-mint non-foil cards; however, it _should_ work for special versions of cards such as alternate art and borderless.

## Instructions (Non-Programmer Friendly)

1. You need to install Python. To check if you have it installed already, open a terminal (or command prompt on Windows) and run: `python --version`. If no version is displayed, or you don't have Python 3 or higher, you can download it from: https://www.python.org/downloads/

2. Once Python is installed, you need to install two packages. Open a terminal and run the following (one at a time):
    - `pip install pandas`
    - `pip install mtgsdk`

3. Now you can run the program. Open a terminal in the same folder where you downloaded mtg_price_checker.py, and run: `python mtg_price_checker.py`

## CSV File Format

If you want to import a list of cards in a CSV file, it must have a header row containing the headers 'name', 'number', and 'set'. You can optionally also include a column named 'count' for the number of copies of a card. Columns can be in any order, but the names must be exactly correct.

### Example:

name, number, set, count <br />
Archangel Elspeth, 320, MOM, 1 <br />
heliod the radiant dawn // heliod the warped eclipse, 293, mom, 1

### Notes:

- All input is case insensitive (except for the column names, those must be lower case)
- Card names must be exact and complete, but you don't need to include commas or apostrophes
- Any card that has two names (such as double-faced or adventure cards) must include both names separated by //
- If the card number is not printed on the card (for older cards), leave it blank (but you must include the set code)