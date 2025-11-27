from collections import defaultdict
import datetime
from pprint import pprint
import json

"""
This is a System that manages a Library's books and members.
1. Books can be added
2. Members can be added
3. Books can be borrowed / returned
4. Current inventory can be viewed i.e books that have been borrowed or in store.
"""



class Book:
    def __init__(self, title, author, quantity=5) -> None:
        self.title = title
        self.author = author
        self.quantity = quantity

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

    def borrow_book(self, *, person, book, number):
        """
        - Should have borrowed date and date to return
        - When borrowed, quantity of book should reduce till it has been returned
        - Person can not borrow the same book if it has not been previously returned
        """
        if number < 1:
            raise ValueError('Must borrow at least one Book')
        
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
                    raise ValueError('Must return at least one book')

                transactions = self._transactions
                book_borrowings = transactions[person][book]
                unreturned = [b for b in book_borrowings if b["is_returned"] is False][
                    0
                ]
                # num_returned = unreturned["num_returned"]
                quantity = unreturned["quantity"]
                if unreturned["num_returned"] < quantity:
                    if number >= quantity:
                        unreturned["is_returned"] = True
                        number = quantity
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

        return to_normal_dict(Library._transactions)
        # print("")
        # # if books:
        # print((f" These books are owned by {Library.name} ").center(100, "*"))
        # print("==========================")
        # for book in self._books:
        #     print(book)
        # print("==========================")

        # print("")
        # print("")

        # # if members:
        # print(f" The current members of {Library.name} ".center(100, "*"))
        # print("==========================")
        # for member in self._members:
        #     print(member)
        # print("==========================")

