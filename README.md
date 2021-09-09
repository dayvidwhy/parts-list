# Bike List
Interface for reading lists of parts from a file that can then have more parts added with prices or compounds of many parts that reflect the total price.

## Installation
The project makes use of `python2` to run.
```bash
git clone git@github.com:dayvidwhy/parts-list.git
cd parts-list
python2 parts_list.py
```

An interface built using Tkinter will then be displayed.

## How it works
It has the ability to load a CSV file containing the information you see above.

You can create a new part, and create a new compound part, made of parts.

When creating a compound part you need to follow the given syntax.

`VH139:2,TR102:1` would create a compound part with 2 VH139 and 1 TR102.
