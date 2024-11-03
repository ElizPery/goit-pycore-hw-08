from collections import UserDict
from datetime import datetime
import pickle
from re import match

# Common class for fields
class Field:
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

# Class for name
class Name(Field):
		pass

# Class for phone with validation (10 numbers)
class Phone(Field):
    def __init__(self, phone: str):
        # Validation of name
        if len(phone) == 10 and all([el.isdigit() for el in phone]):
            super().__init__(phone)
        else:
            raise ValueError('Invalid date format. Phone must contain 10 numbers!')

# Class for birthday with validation (format 'DD.MM.YYYY')
class Birthday(Field):
    def __init__(self, date: str):
        try:
            value = datetime.strptime(date, '%d.%m.%Y').date()
            super().__init__(value)
        except ValueError:
            raise ValueError('Invalid date format. Use DD.MM.YYYY.')
    
    def __str__(self):
        return datetime.strftime(self.value, '%d.%m.%Y')

# Class for record whoch contain name and list of Phones
class Record:
    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Add phone to the record by taking phone, if phone is already exist return
    def add_phone(self, phone: str):
        if str(Phone(phone)) in self.phones:
            raise ValueError('Phone is already exist.')
        self.phones.append(str(Phone(phone)))
        return self.phones
    
    # Edit phone from the record by taking phone and new phone, if phone not exist return
    def edit_phone(self, phone: str, new_phone: str):
        # Check if phone exist
        self.find_phone(phone)

        phone_index = self.phones.index(phone)
        self.phones.remove(phone)
        self.phones.insert(phone_index, new_phone)
        return self.phones

    # Find phone from the record by taking phone, if phone not exist return
    def find_phone(self, phone: str):
        if str(Phone(phone)) not in self.phones:
            raise KeyError
        return phone
    
    # Add birthday to the record by taking birthday (format 'DD.MM.YYYY')
    def add_birthday(self, date: str):
        self.birthday = str(Birthday(date))
        return self.birthday

    def __str__(self):
        return f'Contact name: {self.name}, phones: {'; '.join(p for p in self.phones)}, birthday: {self.birthday if self.birthday else "unknown"}'

# Class for address book
class AddressBook(UserDict):

    # Add record to the dict by taking record
    def add_record(self, record: Record):
        self.data[str(record.name)] = record

        return self.data[str(record.name)]

    # Find record in dict by taking name
    def find(self, name: str):
        if name in self.data:
            return self.data[name]
        return None
    
    # Function that return list of users that have birthdays in upcoming week
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []

        for info in self.data.values():
            if not info.birthday: continue
            birthday_date = datetime.strptime(info.birthday, '%d.%m.%Y').date()
            date_today = datetime.today().date()
            upcoming_birthday = datetime(year=date_today.year, month=birthday_date.month, day=birthday_date.day).date()

            # check if birthday already was this year, if yes, change date to the next year
            if(upcoming_birthday < date_today):
                upcoming_birthday = datetime(year=date_today.year + 1, month=birthday_date.month, day=birthday_date.day).date()

            # check if birthday in upcomming week
            if(upcoming_birthday.toordinal() - date_today.toordinal() <= 7):

                # check if birthday on weekend, if yes, change congratulation date to Monday
                if(upcoming_birthday.weekday() == 5):
                    upcoming_birthday = datetime(year=date_today.year, month=birthday_date.month, day=birthday_date.day + 2).date()
                if(upcoming_birthday.weekday() == 6):
                    upcoming_birthday = datetime(year=date_today.year, month=birthday_date.month, day=birthday_date.day + 1).date()

                upcoming_birthdays.append({'name': str(info.name), 'congratulation_date': datetime.strftime(upcoming_birthday, '%d.%m.%Y')})

        return upcoming_birthdays
    
    # Function that serialize address book in file using pickle, by default filename = 'addressbook.pkl'
    def save_data(self, filename='addressbook.pkl'):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    # Function that deserialize file into address book using pickle, by default filename = 'addressbook.pkl'
    @classmethod
    def load_data(cls, filename='addressbook.pkl'):
        try:
            with open(filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return AddressBook()

    def __str__(self):
        return f'{'\n'.join([str(contact) for contact in self.data.values()])}'
    
# Decorator for handling errors of input
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return e
        except IndexError:
            return "Enter user name!"
        except KeyError:
            return "Contact is not in contacts."
    return inner

# Function take user input (first command) and return parsed data 
def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Decorator to handle ValueError
@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    # Function add contact with data in args (name, phone) to the dict contacts or add phone if contact is already exist
    try:
        name, phone, *_ = args
    except ValueError:
        return 'Give me name and phone please.'
    
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
        
    if phone:
        record.add_phone(phone)
    return message

# Decorator to handle ValueError
@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    # Function takes data about contact and update phone of contact by name
    try:
        name, phone, new_phone, *_ = args
    except ValueError:
        return 'Please enter name, old phone and new phone!'
    
    record: Record = book.find(name)
    message = "Contact updated."

    if record is None:
        message = "Contact is not in contacts!"
        return message
    
    record.edit_phone(phone, new_phone)
    return message

# Decorator to handle IndexError and KeyError
@input_error
def show_phone(args: str, book: AddressBook) -> str:
    # Function takes name of contact and return its phone
    name = args[0]

    record: Record = book.find(name)

    if record is None:
        return "Contact is not in contacts!"

    phones = record.phones
    return f"Phones: {'; '.join(p for p in phones)}"

# Decorator to handle ValueError   
@input_error
def show_all(book: AddressBook) -> str:
    # Function takes dict of contacts and return it, if no contacts return 'No contacts found'
    if len(book) == 0:
        return 'No contacts found'
    
    return book

# Decorator to handle ValueError
@input_error
def add_birthday(args: list, book: AddressBook):
    # Function add birthday with data in args (name, date of birthday) to the dict contacts
    try:
        name, date, *_ = args
    except ValueError:
        return 'Please enter name and date of birthday!'
    
    record: Record = book.find(name)

    if record is None:
        return "Contact is not in contacts!"
    
    record.add_birthday(date)
    return 'Birthday added'


# Decorator to handle ValueError
@input_error
def show_birthday(args: list, book: AddressBook):
    # Function takes name of contact and return its birthday
    name = args[0]    

    record: Record = book.find(name)

    if record is None:
        return "Contact is not in contacts!"
    return record.birthday

# Function takes dict of contact and return upcoming birthdays
def birthdays(book: AddressBook):

    if len(book) == 0:
        return 'No contacts found'
    
    birthdays = book.get_upcoming_birthdays()
    if len(birthdays) == 0:
        return 'No upcoming birthdays found'
    return f'{'\n'.join([f'Congratulate {birthday['name']} on {birthday['congratulation_date']}' for birthday in birthdays])}'

def main():
    book: AddressBook = AddressBook.load_data()

    print('Welcome to the assistance bot!')

    while True:
        user_input = input('Enter a command >>> ')
        command, *args = parse_input(user_input)

        if command in ['close', 'exit']:
            book.save_data()
            print('Goodbye!')
            break
        elif command == 'hello':
            print('Hello, how can I help you?')
        elif command == 'add':
            print(add_contact(args, book))
        elif command == 'change':
            print(change_contact(args, book))
        elif command == 'phone':
            print(show_phone(args, book))
        elif command == 'all':
            print(show_all(book))
        elif command == 'add-birthday':
            print(add_birthday(args, book))
        elif command == 'show-birthday':
            print(show_birthday(args, book))
        elif command == 'birthdays':
            print(birthdays(book))
        else:
            print('Invalid command')

if __name__ == '__main__':
    main()