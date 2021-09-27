import json
import sys
import uuid
from datetime import datetime, timedelta

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout, QApplication, QMainWindow, QWidget, \
    QHBoxLayout, QRadioButton

DAYS_EVENT_LIMIT = 365


class Tickets:
    id_list = {
        uuid.uuid4(): ['Regular Ticket', 1],  # no discount
        uuid.uuid4(): ['Advance Ticket', 0.6],  # -40% discount
        uuid.uuid4(): ['Late Ticket', 1.1],  # +10% to the price
        uuid.uuid4(): ['Student Ticket', 0.5]  # -50% discount
    }

    def __init__(self, description='', regular_ticket='Regular Ticket', advance_ticket='Advance Ticket',
                 late_ticket='Late Ticket', student_ticket='Student Ticket'):
        with open('events.json') as f:
            self.data = json.load(f)

        # print(self.data['Introduction to Python'][1])
        # print(self.data.keys())

        self._regular_ticket = regular_ticket
        self._advance_ticket = advance_ticket
        self._late_ticket = late_ticket
        self._student_ticket = student_ticket

        self.ticket_price = 0  # unique price for each ticket
        self.description = description
        self.ticket_id = None  # unique id for each type of ticket

    def regular_ticket(self, event):
        self.ticket_id = self.getID(self._regular_ticket)
        self.ticket_price = self.data[event][1] * self.id_list[self.ticket_id][1]  # no discounts but the value is taken
        self.description = self._regular_ticket
        return self.regular_ticket

    def advance_ticket(self, event):
        self.ticket_id = self.getID(self._advance_ticket)
        self.ticket_price = int(self.data[event][1] * self.id_list[self.ticket_id][1])  # -40% of the regular price
        self.description = self._advance_ticket
        return self.advance_ticket

    def late_ticket(self, event):
        self.ticket_id = self.getID(self._late_ticket)
        self.ticket_price = int(self.data[event][1] * self.id_list[self.ticket_id][1])  # +10% of the regular price
        self.description = self._late_ticket
        return self.late_ticket

    def student_ticket(self, event):
        self.ticket_id = self.getID(self._student_ticket)
        self.ticket_price = int(self.data[event][1] * self.id_list[self.ticket_id][1])  # -50% of the regular price
        self.description = self._student_ticket
        return self.student_ticket

    def getPrice(self, value):
        ticket_prices = []
        for item in self.id_list:
            ticket_prices.append(f"{self.id_list[item][0]} --- "
                                 f"Price: {int(self.id_list[item][1] * self.data[value][1])} ₴")
        return ticket_prices

    def getID(self, value):
        for key in self.id_list:
            if self.id_list[key][0] == value:
                return key

    def constructByNumber(self, value, event):
        ticket_type = self.id_list[value][0]
        ticket_price = int(self.data[event][1] * self.id_list[value][1])
        return value, ticket_type, ticket_price


class Order(Tickets):

    def __init__(self):
        super().__init__()
        self.orderDate = datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S")

    def getOrder(self, value, event):
        try:
            if value is not 'Student' and value is not 'Adult':
                raise ValueError(f'Invalid value. Current parameter cannot be interpreted as an order type. '
                                 f'The value should be "Student" or "Adult".')
        except ValueError as err:
            print(f"'{value}': {err}")
            sys.exit()

        try:
            eventDate = datetime.strptime(self.data[event][0], "%d.%m.%Y")

        except ValueError as err:
            print('The date of the event is incorrect.', err, sep='\n')
            sys.exit()

        if eventDate - timedelta(days=60) >= datetime.today() and value is not 'Student':
            self.advance_ticket(event)

        elif eventDate - timedelta(days=10) < datetime.today() and value is not 'Student':
            self.late_ticket(event)

        elif value == 'Student':
            self.student_ticket(event)

        else:
            self.regular_ticket(event)

    def show(self):
        return self.orderDate, self.ticket_id, self.description, self.ticket_price


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(500, 200, 1000, 700)
        self.setWindowTitle('IT Events')

        with open('events.json') as f:
            self.data = json.load(f)

        self.label_events = QLabel('Available events:', self)
        self.radioButtons = []
        self.rButtonTickets = []
        self.eventText = ''
        self.orderText = ''
        self.events = []

        # Events line
        container = QWidget(self)
        container.setContentsMargins(0, 0, 0, 0)
        container.setFixedSize(700, 150)
        container.move(200, 50)

        self.layout = QHBoxLayout(container)
        self.layout.addWidget(self.label_events)
        self.layout.setAlignment(Qt.AlignCenter)

        # Ticket types line
        rContainer = QWidget(self)
        rContainer.setFixedSize(600, 100)
        rContainer.move(300, 150)

        self.hbox = QHBoxLayout(rContainer)
        self.vbox = QVBoxLayout(self)

        self.label_order = QLabel('', self)
        self.label_getPrice = QLabel('', self)
        self.label_prompt = QLabel('' , self)

        self.label_order.setFont(QFont('Times', 12))
        self.vbox.addWidget(self.label_order)
        self.vbox.setAlignment(Qt.AlignCenter)

        # Build rButtons events
        for item in self.data.keys():
            self.events.append(item)
            text = f"{item}. \nDate: {self.data[item][0]}. \n(Price for regular ticket: {self.data[item][1]} ₴)"
            rButton = QRadioButton(text, self)
            self.radioButtons.append(rButton)
            rButton.clicked.connect(self.rButton_events)
            self.layout.addWidget(rButton)

    def rButton_events(self):
        for i in range(0, len(self.radioButtons)):
            if self.radioButtons[i].isChecked() and not self.rButtonTickets:
                self.orderText = self.radioButtons[i].text()
                self.eventText = self.events[i]

                label_tickets = QLabel('Select ticket type:', self)
                rButton = QRadioButton('Adult', self)
                rButton_2 = QRadioButton('Student', self)

                self.label_prompt.setText('CLICK ON THE \nRADIO BUTTON AGAIN\nTO UPDATE YOUR ORDER')
                self.label_prompt.setFont(QFont('Times', 11))
                self.label_prompt.setAlignment(Qt.AlignCenter)
                self.pushButton_getPrice = QPushButton('GET \nTICKET PRICES', self)
                self.pushButton_buildByNumber = QPushButton('BUILD TICKET \nBY ID NUMBER', self)

                rButton.clicked.connect(self.rButton_order)
                rButton_2.clicked.connect(self.rButton_order)
                self.pushButton_getPrice.clicked.connect(self.show_ticketsPrice)
                self.pushButton_buildByNumber.clicked.connect(self.build_byNumber)

                self.rButtonTickets.append(rButton)
                self.rButtonTickets.append(rButton_2)

                self.hbox.addWidget(self.label_prompt)
                self.hbox.addWidget(label_tickets)
                self.hbox.addWidget(rButton)
                self.hbox.addWidget(rButton_2)
                self.hbox.addWidget(self.pushButton_getPrice)
                self.hbox.addWidget(self.pushButton_buildByNumber)
                self.pushButton_buildByNumber.setEnabled(False)

            if self.radioButtons[i].isChecked():
                self.orderText = self.radioButtons[i].text()
                self.eventText = self.events[i]

    def rButton_order(self):
        # self.pushButton.setEnabled(True)
        self.pushButton_buildByNumber.setEnabled(True)
        self.o = Order()
        self.get_sender = self.sender()
        if self.get_sender.text() == 'Adult':
            self.o.getOrder('Adult', self.eventText)
        else:
            self.o.getOrder('Student', self.eventText)

        self.orderDate, self.ticket_id, self.description, self.ticket_price = self.o.show()
        self.label_order.setText(f"YOUR ODER:\n\nEvent: {self.orderText}\n\nOrder date: {self.orderDate}."
                                 f"\n\tTicket id: {self.ticket_id}. \n\tType: {self.description}. "
                                 f"\n\tPrice: {self.ticket_price} ₴.")

    def show_ticketsPrice(self):
        t = Tickets()
        text = ''
        for i in t.getPrice(self.eventText):
            text += i + '\n'
        self.label_getPrice.setText(text)
        self.label_getPrice.setAlignment(Qt.AlignCenter)
        self.label_getPrice.setGeometry(0, 0, 300, 400)

    def build_byNumber(self):
        t = Tickets()
        requestID = self.ticket_id
        tID, tIDType, tIDPrice = t.constructByNumber(requestID, self.eventText)
        self.label_order.setText(f'You requested a unique ticket ID: {tID}. \n\n\t'
                                 f'Event: {self.eventText}. \n\tGet ID: {tID}. \n\t'
                                 f'Type Ticket: "{self.description}". \n\tPrice: {tIDPrice} ₴.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
