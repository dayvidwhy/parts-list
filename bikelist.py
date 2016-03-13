from Tkinter import *
import tkMessageBox
import tkFileDialog
from tkMessageBox import askokcancel

# Formatting for use in the __str__ methods
PART_FORMAT = "{0:10}{1:30}{2:>10}"
COMPOUND_FORMAT = "{0:10}{1:30}{2:>10}  {3}"
    

def load_items_from_file(products, filename):
    """Add the items in the supplied file to the products object.

    load_items_from_file(Products, str) -> None

    Precondition: Assumes the supplied is of the correct format
    """
    fid = open(filename, 'U')
    for line in fid:
        item_info = line.split(',')
        if len(item_info) > 2:     # ignores blank lines
            item_id = item_info[0].strip()
            item_name = item_info[1].strip()
            if ':' in item_info[2]:   # compound 
                items = item_info[2:]
                products.add_item(item_id, 
                                  Compound(item_id, item_name, products, 
                                           get_components(items)))
            else:   # part
                item_cost = int(item_info[2].strip())
                products.add_item(item_id, Part(item_id, item_name, item_cost))
    fid.close()

def get_components(items):
    """Return a list of pairs of IDs and numbers in items.

    get_components(list(str)) -> list((str, int))
    """
    components = []
    for item in items:
        item = item.strip()
        itemid, _, itemnumstr = item.partition(':')
        itemid = itemid.strip()
        itemnumstr = itemnumstr.strip()
        components.append((itemid, int(itemnumstr)))
    return components
 


def save_items_to_file(products, filename):
    """Save the items in products to the given file.

    save_items_to_file(Products, str) -> None
    """
    f = open(filename, 'w')
    keys = products.get_keys()
    for key in keys:
        f.write("{0}\n".format(repr(products.get_item(key))))
    f.close()

def items_string(items_list):
    """Convert a list of Id, number pairs into a string representation.

    items_string(list((str, int))) -> str
    """
    result = []
    for itemid, num in items_list:
        result.append("{0}:{1}".format(itemid, num))
    return ','.join(result)


class Item(object):
    """A representation of a basic Item which only has a name and an ID"""
    
    def __init__(self, itemID, name):
        """Initialises an item object with an item ID and name.

        Constructor: Item(int, str)
        
        """
        self._ID = itemID
        self._name = name

    def get_name(self):
        """Returns the name of the item.

        item.get_name() -> str
        
        """
        return self._name

    def get_ID(self):
        """Returns the item ID.

        item.get_ID() -> str
        
        """
        return self._ID

    def set_name(self, name):
        """Changes the name of the item to name.

        item.set_name(str) -> None
        
        """
        self._name = name

    def get_depend(self):
        """Returns an empty list for when there are no dependencies.

        item.get_depend() -> list<str>
        
        """
        return []

class Part(Item):
    """A representation of a bike part which is an item that also has a cost."""
    
    def __init__(self, itemID, name, cost):
        """Initialise a part with item name, item ID and cost.

        Constructor: Part(str, str, int)
        
        """
        Item.__init__(self, itemID, name)
        self._cost = cost

    def get_cost(self):
        """Returns the cost of the part.

        part.get_cost() -> int
        
        """
        return self._cost

    def get_type(self):
        """Return a boolean to identify the item type.  False means part.

        part.get_type() -> Bool

        """
        return False

    def set_cost(self, cost):
        """Change the cost of the part.

        part.set_cost(int) -> None

        """
        self._cost = cost

    def __repr__(self):
        """The format of the part to be saved to files."""
        
        return '{0}, {1}, {2}'.format(self.get_ID(), self.get_name(),
                                      self.get_cost())

    def __str__(self):
        """The listbox presentation format for a part."""
        
        return PART_FORMAT.format(self.get_ID(), self.get_name(),
                                  self.get_cost())

class Compound(Item):
    """A representation of a compound which contains is an item
    that may contain multiple parts."""
    
    def __init__(self, itemID, name, products, itemlist):
        """Initialise the compound with an item ID, name, associated
        products dictionary and list of item ID's specifying parts.

        Constructor: Compound(str, str, Products, list<[str, int]>)
        
        """
        Item.__init__(self,itemID, name)
        self._products = products
        self._itemlist = itemlist

    def get_cost(self):
        """Returns the cost of the compound item from the parts making it up.

        compound.get_cost() -> int

        """
        cost = 0
        for i in self.get_items_list():
            cost += self._products.get_item(i[0]).get_cost() * i[1]
        return cost
        
    def get_items_list(self):
        """Returns the list of items making up the compound.

        compound.get_items_list() -> list<str>
        
        """
        return self._itemlist

    def get_items_str(self):
        """Returns a string representation of the items list.

        compound.get_items_str() -> str

        """
        return items_string(self.get_items_list())

    def set_items(self, items):
        """Adjust the items making up the compound item.

        compound.set_items() -> 

        """
        self._itemlist = items

    def get_depend(self):
        """Gets a list of item ID's the compound contains.

        compound.get_depend() -> Bool

        """
        result = []
        for i in self.get_items_list():
            result.append(i[0])
        return result

    def get_type(self):
        """Return a boolean to tell it an item is a compound or a part.
        True means the item is a compound.

        compound.get_type() -> Bool

        """
        return True

    def __str__(self):
        """The listbox formatting of a compound."""
        if self.get_items_list() != []:
            return COMPOUND_FORMAT.format(self._ID, self._name, self.get_cost(),
                                      self.get_items_str())
        elif self.get_items_list() == []:
            return COMPOUND_FORMAT.format(self._ID, self._name, self.get_cost(),
                                      'None')

    def __repr__(self):
        """The format of a compound to be saved to an output file."""
        
        return '{0}, {1}, {2}, {3}'.format(self.get_ID(), self.get_name(),
                                           self.get_cost(),
                                           self.get_items_str())
    
class Products(object):
    """The dictionary containing information about each Part and Compound"""
    
    def __init__(self):
        """Initialises the products dictionary

        Constructor: Products()
        
        """
        self.pdict = {}
    
    def load_items(self, filename):
        """Loads Parts and Compounds from a file into the dictionary.

        products.load_items(str) -> None
        
        """
        load_items_from_file(self, filename)

    def save_items(self, filename):
        """Saves Parts and Compounds to a file from the dictionary.

        products.save_items(str) -> None
        
        """
        save_items_to_file(self, filename)

    def get_item(self, itemID):
        """Returns the Part or Compound associated with the itemID.

        products.get_item(str) -> Item

        """
        return self.pdict[itemID]

    def add_item(self, itemID, item):
        """Adds an item to the products dictionary

        products.add_item(str, Item) -> None

        """
        self.pdict[itemID] = item

    def remove_item(self, itemID):
        """Deletes an entry from the products dictionary

        products.remove_item(str) -> None

        """
        del self.pdict[itemID]
            
    def delete_all(self):
        """Resets the products dictionary to empty.

        products.delete_all() -> None

        """
        self.pdict = {}

    def get_keys(self):
        """Returns a list of item ID's of the Parts and the Compounds in the
        products dictionary.

        products.get_keys() -> list<str>

        """
        x = self.pdict.keys()
        x.sort()
        return x

    def check_depend(self, itemID):
        """Check to see if a Part is an item used by a Compound

        products.check_depend(str) -> bool

        """
        for i in self.pdict:
            if itemID in self.pdict[i].get_depend():
                return True
        return False

class Controller(object):
    """The container for all of the grouped widgets and data processing"""
    
    def __init__(self, master):
        """A controller class for handling all commands and passing
        information to the View class for display.

        Constructor: Controller(root)
        
        """
        self._master = master
        menubar = Menu(master)
        master.config(menu=menubar)
        filemenu = Menu(menubar)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Open Products File", command=self.open_file)
        filemenu.add_command(label="Save Products File", command=self.save_file)
        filemenu.add_command(label="Exit", command=self.close)
        self._listbox = View(master, self)
        self._listbox.pack(side=TOP, expand=True, pady=10,
                     ipady=150, ipadx= 450, fill=BOTH)
        self._inputs = Input(master, self)
        self._inputs.pack(side=TOP)
        self._entry = Entbox(master, self)
        self._entry.pack(side=TOP)
        self._products = Products()

    def open_file(self):
        """A method for openning a file selected by the user.

        controller.open_file() -> None

        """
        self._filename = tkFileDialog.askopenfilename()
        if self._filename:
            self._listbox.delete(0, END)
            self._products.delete_all()
            self._products.load_items(self._filename)
            self._listbox.update(self.items_list())
        
    def save_file(self):
        """A method for saving the information to a filename selected
        by the user.

        controller.save_file() -> None

        """
        self._filename = tkFileDialog.asksaveasfilename()
        if self._filename:
            self._products.save_items(self._filename)

    def get_indexed(self):
        """Returns the item associated with the listbox index

        controller.get_indexed() -> Item

        """
        index = int(self._listbox.curselection()[0])
        return self._products.get_item(self._products.get_keys()[index])

    def items_list(self):
        """Returns a regenerated list of strings for the listbox to display
        after any change is made to the products dictionary.

        controller.items_list() -> list<str>

        """
        result = []
        for i in self._products.get_keys():
            result.append(str(self._products.get_item(i)))
        return result
        
    def close(self):
        """Exit the application.

        controller.close() -> None

        """
        ans = askokcancel('Verify exit', 'Really quit?')
        if ans:
            self._master.destroy()

    def add_part(self):
        """The method that is called when the add_part button is pressed.
        The use can then add a new part ID.

        controller.add_part() -> None

        """
        self._entry.label('Add Part ID')
        self._entry.button_command(self.add_part_button)
        
    def add_part_button(self):
        """The functionality of the OK button once the Add Part button is
        pressed and checks to see if an item ID already exists and if it
        does not it creates a Part and adds it to the Products.
        
        controller.add_part_button() -> None

        """
        e = self._entry.grab_it()
        if e not in self._products.get_keys():
            self._products.add_item(e, Part(e, 'No Name', 0))
            self._listbox.update(self.items_list())
        else:
            tkMessageBox.showwarning('Add Part', 'ID already exists')

    def add_compound(self):
        """The method that is called when the add_compound button is pressed.
        The user can then enter a new compound ID.

        controller.add_compound() -> None

        """
        self._entry.label('Add Compound ID')
        self._entry.button_command(self.add_compound_button)

    def add_compound_button(self):
        """The functionality of the OK button once the Add Compound button is
        pressed and checks to see if an item ID already exists.
        
        controller.add_compound_button() -> None

        """
        e = self._entry.grab_it()
        if e not in self._products.get_keys():
            self._products.add_item(e, Compound(e, 'No Name',self._products,[]))
            self._listbox.update(self.items_list())
        else:
            tkMessageBox.showwarning('Add Compound', 'ID already exists')

    def update_name(self):
        """The method that is called when the update_name button is pressed.
        The user can then enter a new name into the entry box to change the
        name.

        controller.add_compound() -> None

        """
        if self._listbox.curselection():
            self._entry.label('Update Name')
            self._entry.button_command(self.updateName_button)
            self._entry.set_it((self.get_indexed()).get_name())
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')

    def updateName_button(self):
        """The functionality of the OK button once the Update Name button is
        pressed. The user can then enter a new name and press OK.
        
        controller.add_compound_button() -> None

        """
        if self._listbox.curselection():
            name = self._entry.grab_it()
            self.get_indexed().set_name(name)
            self._listbox.update(self.items_list())
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')

    def update_cost(self):
        """This method changes the functionality of the OK button
        to allow the user to update the cost by entering a number.

        controller.update_cost() -> None

        """
        if self._listbox.curselection():
            if not self.get_indexed().get_type():
                self._entry.label('Update Cost')
                self._entry.button_command(self.updateCost_button)
                self._entry.set_it((self.get_indexed()).get_cost())
            else:
                tkMessageBox.showwarning('Part Error',
                                         'This item is not a part')
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')

    def updateCost_button(self):
        """The functionality of the OK button after the Update Cost button is
        pressed.  Pressing OK will change the cost of the selected item.

        controller.updateCost_button() -> None

        """
        if self._listbox.curselection():
            try:
                cost = int(self._entry.grab_it())
            except ValueError:
                tkMessageBox.showwarning('Value error', 'That is not a number')
                return
            self.get_indexed().set_cost(cost)
            self._listbox.update(self.items_list())
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')

    def update_items(self):
        """This method changes the functionality of the OK button
        to allow the user to change the items associated with a compound.

        controller.update_items() -> None

        """
        if self._listbox.curselection():
            if not self.get_indexed().get_type():
                tkMessageBox.showwarning('Compound Error',
                                        'This item is not a compound')
            else:
                self._entry.label('Update Compound Items')
                self._entry.button_command(self.updateItems_button)
                self._entry.set_it((self.get_indexed()).get_items_str())
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')

    def updateItems_button(self):
        """The functionality of the OK button after the Update Items button
        is pressed.  By entering a string of item ID's and numbers the
        items list string will be updated.

        controller.updateItems_button() -> None

        """
        if self._listbox.curselection():
            selectName = self.get_indexed().get_ID()
            itemsList = self._entry.grab_it()
            if selectName not in itemsList:
                try:
                    itemsList = get_components(itemsList.split(','))
                except ValueError:
                    tkMessageBox.showwarning('Compound item',
                                             'Invalid items list')
                    return
                self.get_indexed().set_items(itemsList)
                try:
                    self._listbox.update(self.items_list())
                except KeyError:
                    tkMessageBox.showwarning('Compound item',
                                             'Invalid items list')
                    return
            else:
                tkMessageBox.showwarning("Compound item", "Invalid items list")
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')
        
    def remove_item(self):
        """Delete the selected item from the listbox and products dictionary.

        controller.remove_item() -> None

        """
        if self._listbox.curselection():
            index = int((self._listbox.curselection()[0]))
            itemID = self._products.get_keys()[index]
            if self._products.check_depend(itemID):
                tkMessageBox.showwarning('Remove Error',
                            'At least one compound item refers to this item')
            else:
                self._products.remove_item(itemID)
                self._listbox.delete(ANCHOR)
        else:
            tkMessageBox.showwarning('Selection error', 'No item selected')
      
class View(Listbox):
    """The listbox container and methods for adjusting it"""

    def __init__(self, master, controller):
        """Constructor: View(root, controller)"""
        
        Listbox.__init__(self, master, font='Courier 10')
        self._controller = controller

    def update(self, itemslist):
        """Recreate the listbox when changes are made.

        view.update(list<str>) -> None

        """
        self.delete(0, END)
        for i in itemslist:
            self.insert(END, i)
       
class Input(Frame):
    """The container group for the input buttons"""
    
    def __init__(self, master, controller):
        """Constructor: Input(root, controller)"""
        
        Frame.__init__(self, master)
        self._controller = controller

        Button(self, text='Add Part',
               command=controller.add_part).pack(side=LEFT,padx=10,ipadx=10)
        Button(self, text='Add Compound',
               command=controller.add_compound).pack(side=LEFT,padx=10,ipadx=10)
        Button(self, text='Update Name',
               command=controller.update_name).pack(side=LEFT,padx=10,ipadx=10)
        Button(self, text='Update Cost',
               command=controller.update_cost).pack(side=LEFT,padx=10,ipadx=10)
        Button(self, text='Update Items',
               command=controller.update_items).pack(side=LEFT,padx=10,ipadx=10)
        Button(self, text='Remove Item',
               command=controller.remove_item).pack(side=LEFT,padx=10,ipadx=10)

class Entbox(Frame):
    """The container group for the entry box, the displayed label
    and the OK button"""
    
    def __init__(self, master, controller):
        """Constructor: Entbox(root, controller)"""
        
        Frame.__init__(self, master)
        self._controller = controller
        self.type = Label(self, text='', width=17)
        self.type.pack(side=LEFT, ipadx=10, ipady=20)
        self.v = StringVar()
        self.entry = Entry(self, bd=2, textvariable=self.v)
        self.entry.pack(side=LEFT, ipadx=230)
        self.grab = Button(self, text='OK', command=self.grab_it)
        self.grab.pack(side=LEFT, padx=10, ipadx=10)

    def grab_it(self):
        """A method for returning what the user has entered into the entry box.

        entbox.grab_it() -> str
        
        """
        a = self.entry.get()
        self.entry.delete(0, END)
        return a

    def set_it(self, text):
        """A method to set the entry box text to what already exists in the
        section the user is attempting to change.

        entbox.set_it() -> None

        """
        self.v.set(text)

    def button_command(self, action):
        """Change the command associated with the OK button as different
        input buttons are pressed.

        entbox.button_command(function) -> None

        """
        self.grab.config(command=action)

    def label(self, text):
        """Change the text on the label to reflect which input button
        has been pressed by the user.

        entbox.label(str) -> None

        """
        self.type.config(text=text)


class StoreApp():
    def __init__(self, master=None):
        master.title("Bikes R Us: Products")
        self.controller = Controller(master)

def main():
    root = Tk()
    app = StoreApp(root)
    root.mainloop()
    
if  __name__ == '__main__':
    main()
