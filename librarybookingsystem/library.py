from collections import defaultdict
import datetime
from pprint import pprint
import json
from typing import Literal

"""
This is a System that manages a Library's books and members.
1. Books can be added
2. Members can be added
3. Books can be borrowed / returned
4. Current inventory can be viewed i.e books that have been borrowed or in store.
"""


class Book:
    _book_id = 0

    def __init__(self, title, author, quantity=5) -> None:
        self.title = title
        self.author = author
        self.quantity = quantity
        self.id = Book._book_id
        Book._book_id += 1

    def __str__(self) -> str:
        return f"{self.title} by {self.author}"

    def __repr__(self) -> str:
        return f"{self.title}"


class Person:
    _user_id = 0

    def __init__(self, name) -> None:
        self.name = name
        self.id = Person._user_id
        Person._user_id += 1

    def __repr__(self) -> str:
        return self.name

    __str__ = __repr__


class Library:
    name = "Pioneeary"
    _transactions = defaultdict(lambda: defaultdict(list))
    _books = set()
    _members = set()

    def __init__(self) -> None:
        pass

    "Add books to library"

    def add_book(self, book):
        if not isinstance(book, Book):
            raise Exception("This is not a valid Book")
        else:
            self._books.add(book)
            return self._books

    "Make People Members of the Library"

    def add_member(self, person):
        if not isinstance(person, Person):
            return "This is not a valid Person"
        else:
            self._members.add(person)
            return self._members

    "Check if Person is Eligible to borrow a Book"

    def is_eligible(self, *, person, book):
        "To check if a Person is eligible to borrow a certain book"
        if person in self._members:
            transactions = self._transactions
            is_present = transactions.get(person)
            if is_present:
                # check if book is in the persons recent borrowings and has been returned
                if transactions[person].get(book) is not None:
                    book_borrowings = transactions[person][book]
                    unreturned = any(b["is_returned"] is False for b in book_borrowings)
                    "If at any point this book was borrrowed and not returned, return False"
                    if unreturned:
                        return False

            "person has not borrowed this book before"
            return True
        raise ValueError(f"Not a Member")

    def borrow_book(self, *, person, book, number=1):
        """
        - Should have borrowed date and date to return
        - When borrowed, quantity of book should reduce till it has been returned
        - Person can not borrow the same book if it has not been previously returned
        """
        if number < 1:
            raise ValueError("Must borrow at least one Book")

        if isinstance(book, Book):
            if book in self._books:
                if number <= book.quantity:
                    if self.is_eligible(person=person, book=book):
                        # first check if the book has been borrowed by this person and it hasnt been returned
                        current_time = datetime.datetime.now()
                        return_deadline = current_time + datetime.timedelta(days=5)
                        self._transactions[person][book].append(
                            {
                                "date_borrowed": str(current_time),
                                "return_deadline": str(return_deadline),
                                "is_returned": False,
                                "quantity": number,
                                "num_returned": 0,
                                "return_history": [],
                            }
                        )
                        book.quantity -= number
                        return True
                else:
                    print(f"Not Enough '{book}' available")
                return False
            raise ValueError("Book Not Found")
        raise ValueError("Not a Valid Book")

    def return_book(self, *, person, book, number):
        """
        - Must be a valid book instance
        - Book should not have been returned already
        """
        if isinstance(book, Book):
            if book in Library._books:
                "If Person has not borrowed this book, it shouldnt be returnable"
                if self.is_eligible(person=person, book=book):
                    return False

                if number < 1:
                    raise ValueError("Must return at least one book")

                transactions = self._transactions
                book_borrowings = transactions[person][book]
                unreturned = [b for b in book_borrowings if b["is_returned"] is False][
                    0
                ]

                quantity = unreturned["quantity"]
                remainder = quantity - unreturned["num_returned"]
                if unreturned["num_returned"] < quantity:
                    if number >= remainder:
                        unreturned["is_returned"] = True
                        number = remainder
                    unreturned["num_returned"] += number
                    current_date = datetime.datetime.now()
                    unreturned["return_history"].append(
                        {"date": str(current_date), "quantity": number}
                    )
                book.quantity += number
                return True
            raise ValueError("Book Not Found")
        raise ValueError("Not a Valid Book")

    "View books or members"

    def info(self):
        def to_normal_dict(obj):
            if isinstance(obj, defaultdict):
                obj = dict(obj)
            if isinstance(obj, dict):
                return {k: to_normal_dict(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [to_normal_dict(i) for i in obj]
            return obj

        # print("")
        # # if books:
        print((f" These books are owned by {Library.name} ").center(50, "*"))
        print("")
        for book in self._books:
            print(book)
        print("")

        # print("")
        # print("")

        # # if members:
        print(f" The current members of {Library.name} ".center(50, "*"))
        print("")
        for member in self._members:
            print(member)
        print("")
        return to_normal_dict(Library._transactions)


def get_instance(instance_container):
    while True:
        try:
            id = input("Enter instance ID: ")
            if id in ["c", "C"]:
                break
            id = int(id)
            instance = instance_container[id]
        except ValueError:
            continue
        except KeyError:
            print("Instance not found")
            continue
        return instance


def book_interaction(
    *,
    action: Literal["borrowing", "returning"],
    members,
    books,
    members_container,
    books_container,
    library
):
    print(f"Who is {action} this book? ")
    print({key.id: key.name for key in members})
    user = get_instance(members_container)
    if user:
        print({key.id: key.title for key in books})
        print(f"Which book are you {action}? ")
        book = get_instance(books_container)
        if book:
            while True:
                print('Input "C" to cancel')
                num = input(f"How many books are you {action}? ")
                if num in ["c", "C"]:
                    break
                try:
                    num = int(num)
                except ValueError:
                    print("Invalid Input! Only Numbers allowed")
                    continue
                try:
                    if action == 'borrowing':
                        library.borrow_book(person=user, book=book, number=num)
                    else:
                        library.return_book(person=user, book=book, number=num)
                except ValueError as e:
                    print("ERROR", e)
                break


def main():
    lib = Library()
    users = {}
    books = {}
    OPTIONS = [
        ("1", "create_person"),
        ("2", "create_book"),
        ("3", "add_user"),
        ("4", "add_book"),
        ("5", "borrow_book"),
        ("6", "return_book"),
        ("7", "edit_book"),
    ]

    for i, j in OPTIONS:
        print(f'Press {i} to "{j}"')
    print("")

    # Failure = False
    while True:
        user_input = input("Enter Action (Input 'q' to quit): ").strip().lower()
        if user_input in ["q", "quit"]:
            print("")
            print("You have successfully exited the program")
            break

        elif user_input == "1":
            'Create User'
            user_name = input("What is the person's name? ").strip()
            p = Person(user_name)
            users[p.id] = p
            print("")
            # print(users)

        elif user_input == "2":
            'Create Book'
            book_name = input("What is the book's name? ").strip()
            book_author = input("Who is the author? ").strip()
            book_quantity = None
            try:
                book_quantity = int(
                    input(f'How many "{book_name}" do you want to create? ')
                )
            except ValueError:
                pass
            b = Book(book_name, book_author)
            if book_quantity and book_quantity > 0:
                b.quantity = book_quantity
            books[b.id] = b
            # print(books)
            print("")

        elif user_input == "3":
            'Add Person to Library'
            if len(users) == 0:
                print("No user exists")
                continue
            print("You have chosen to make someone a member of the Library")
            print("Select the number in front of their name to make that user a member")
            print("Input 'C' to cancel")

            print({key: val for key, val in users.items() if val not in lib._members})

            user = get_instance(users)
            if user:
                lib.add_member(user)
                print("Current members - ", lib._members)
                print("")

        elif user_input == "4":
            'Add book tp library'
            if len(books) == 0:
                print("No book exists")
                continue
            print("Which book do you want to add to the Library? ")
            print("Input 'C' to cancel")

            print({key: val for key, val in books.items() if val not in lib._books})

            book = get_instance(books)
            if book:
                lib.add_book(book)
                print("Current books - ", lib._books)
                print("")

        elif user_input == "5":
            'To borrow a book'
            book_interaction(
                action='borrowing',
                members=lib._members,
                books=lib._books,
                members_container=users,
                books_container=books,
                library=lib
            )

        elif user_input == "6":
            'To return a book'
            book_interaction(
                action='returning',
                members=lib._members,
                books=lib._books,
                members_container=users,
                books_container=books,
                library=lib
            )
            
        elif user_input == "7":
            'Edit a book'
            print(books)
            print('Which book do you want to edit? ')
            book = get_instance(books)
            print("To Edit Book Title, Input 0")
            print('To Edit Author, Input 1')
            print('To Edit Quantity, Input 2')
            prompt = input('Select an action: ')
            if prompt not in ["0", "1", "2"]:
                continue
            elif prompt == "0":
                title = input(f"What do you want to rename {book.title} to? ")
                book.title = title
            elif prompt == "1":
                author = input(f"What do you want to rename {book.author} to? ")
                book.author = author
            elif prompt == "2":
                book_quantity = input(f"What do you want to change {book.quantity} to? ")
                book.quantity = book_quantity
            else:
                continue
            print(book.title, book.author, book.quantity)
            

        print("")
        print("Current Library State")
        pprint(lib.info())


if __name__ == "__main__":
    main()
    # TODO You can't edit the quantity of a book that has been borrowed