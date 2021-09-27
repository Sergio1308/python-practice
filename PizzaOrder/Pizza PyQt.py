""" Студент Гайдук Сергей КН-19-1"""
import os
import sys
import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QApplication, QMainWindow, QWidget, QCheckBox, QHBoxLayout
from PyQt5.QtGui import QPixmap


# order_list = []


class Pizza:
    """
    A class called Pizza which is used to represent the types of pizza of the day for a business lunch,
    and the type of pizza of the day depends on the day of the week. This class contains a constructor to initialize
    the data attributes including dictionary with additional pizza ingredients, method __str__ which returns
    a string representation our data attributes.
    """

    # This is a dictionary, the day of the week is used as the key, and the price and type of pizza is the key value
    type = {
        1: [120, 'Pepperoni'],
        2: [120, 'Hawaiian'],
        3: [120, 'BBQ'],
        4: [150, 'Carbonara'],
        5: [150, 'Bavarian'],
        6: [100, 'Margarita'],
        7: [130, 'Texas']
    }

    def __init__(self):
        """__init__ is a constructor with one data member that uses the parameters
        to initialize the data attributes.

        """
        self.now = datetime.datetime.today().isoweekday()

        try:
            if not isinstance(self.now, int):
                raise TypeError(f"'{type(self.now).__name__}' object cannot be interpreted as a type of pizza.")

            if not self.type.get(self.now):
                raise KeyError(f"Pizza type of the day '{self.now}' is unknown.")

        except (TypeError, ValueError, KeyError) as err:
            print(f'Error: {err}')
            sys.exit()

        self.price = self.type[self.now][0]
        self.type = self.type[self.now][1]
        self.ingredients = {
            'price': 1.15,  # +15% from the price of pizza for each ingredient
            'Pepperoni': {'Mozzarella', 'Pepperoni', 'Signature sauce'},
            'Hawaiian': {'Chicken', 'Pineapple', 'Mozzarella', 'Signature sauce'},
            'BBQ': {'Chicken', 'Bow', 'Bacon', 'Mushrooms', 'Mozzarella', 'Signature sauce'},
            'Carbonara': {'Bow', 'Bacon', 'Ham', 'Mushrooms', 'Mozzarella', 'Alfredo sauce'},
            'Bavarian': {'Parmesan', 'Bavarian sausages', 'Mozzarella', 'Barbecue sauce'},
            'Margarita': {'Mozzarella', 'Alfredo sauce', 'Barbecue sauce (top)'},
            'Texas': {'Corn', 'Bow', 'Mushrooms', 'Bavarian sausages', 'Mozzarella', 'Barbecue sauce'}
        }

    def getAvailableIngredients(self):
        return ', '.join(map(str, self.ingredients[self.type]))

    def show(self):
        return self.type


class Order(Pizza):
    """
    A class called Order that form customer orders through inheritance of Pizza class and
    contains a constructor to initialize the data attributes, method getPrice which returns the price for the pizza
    in the order, taking into account the selected ingredients,
    method attribute named addIngredients which adds selected pizza ingredients to the order,
    method __str__ which returns a string representation of the order.
    """

    def __init__(self, selected_ingredients):
        """__init__ is a constructor with data members that uses the parameters
        to initialize the data attributes.

        Keywords arguments:
        :param selected_ingredients: selected ingredients available for pizza of the day.

        """
        try:
            if not isinstance(selected_ingredients, str):
                raise TypeError(f"'{type(selected_ingredients).__name__}' cannot be interpreted as an ingredients.")

        except TypeError as err:
            print(f"{err}")
        else:
            self.selected_ingredients = selected_ingredients
            self.selected_list = set()
            super().__init__()

    def getPrice(self):
        """Method attribute which returns the price for the pizza in the order,
        taking into account the selected ingredients."""

        if self.selected_ingredients and self.selected_ingredients is not 'No':
            i = 0
            while i < len(self.selected_list):
                self.price *= self.ingredients['price']
                i += 1
            return int(self.price)
        else:
            return self.price

    def addIngredients(self):
        """Method attribute which adds selected pizza ingredients to the order."""

        selected_ingredients = self.selected_ingredients.split(sep=', ')
        for key in self.ingredients[self.type]:
            for x in selected_ingredients:
                if key == x:
                    self.selected_list.add(key)
                    break

        try:
            # Entered value "No" avoids selection of ingredients.
            if self.selected_ingredients == 'No':
                self.selected_list.add('Pizza without additional ingredients')

            elif not self.selected_list:
                raise AddIngredientsError(selected_ingredients)
        except AddIngredientsError as err:
            print(err)
            sys.exit()

        return ", ".join(self.selected_list)

    def getIngredients(self):
        return self.selected_ingredients


class AddIngredientsError(Exception):
    """Exception raised for errors in the in specifying pizza ingredients.

    Attributes:
        expression -- input pizza ingredients which caused the error
        message -- explanation of the error
    """

    def __init__(self, expression, message='The ingredients for the selected pizza are incorrect.'):
        self.expression = expression
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        """A method that returns a string representation of our error."""
        return f'{self.expression} -> {self.message}'


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = uic.loadUi('pizza.ui')

        p = Pizza()

        self.ui.label_2.setText(f'Available pizza: {p.show()}.')
        self.ui.label_3.setText(f'Available ingredients:\n {p.getAvailableIngredients()}.')

        self.ingredients_list = f'{p.getAvailableIngredients()}'.split(', ')

        self.checkbox_list = [self.ui.checkBox, self.ui.checkBox_2, self.ui.checkBox_3,
                              self.ui.checkBox_4, self.ui.checkBox_5, self.ui.checkBox_6]

        for i in range(0, len(self.ingredients_list)):
            self.checkbox_list[i].setText(self.ingredients_list[i])
            self.checkbox_list[i].clicked.connect(self.update_hint)
            self.checkbox_list[i].setEnabled(True)

        self.load_image(p.show())

    def load_image(self, value):
        self.ui.label.setPixmap(QPixmap(os.path.join('img/%s' % value)).scaled(261, 251))

    def update_hint(self):
        order_list = []

        for i in range(0, len(self.checkbox_list)):
            if self.checkbox_list[i].isChecked():
                order_list.append(self.ingredients_list[i])

        if order_list:
            o = Order(", ".join(order_list))
            self.ui.label_4.setText(f'Selected ingredients:\n {o.addIngredients()}.')
            self.ui.label_5.setText(f'Price: {o.getPrice()} ₴.')
        else:
            self.ui.label_4.setText(f'Selected ingredients:\n Nothing :(. Use checkbox buttons.')
            self.ui.label_5.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ui.show()
    sys.exit(app.exec())
