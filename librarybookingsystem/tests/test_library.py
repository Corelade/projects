import pytest
from librarybookingsystem.library import Book, Person, Library


class BaseTest:
    def setup_method(self, method):
        self.lib = Library()

        self.b1 = Book(title="Rich Dad Poor Dad", author="Robert Kiyosaki")
        self.b2 = Book(title="Think Big", author="Kelly Rows")
        self.b3 = Book(title="Harry Potter", author="J.K. Rowling")
        self.b4 = Book(title="Nelson Biography", author="Nelson Mandela")
        self.not_book = "This is not a Book"

        self.p1 = Person("John")
        self.p2 = Person("Paul")
        self.p3 = Person("Peter")
        self.p4 = Person("Simon")

        # add books and members to library
        self.lib.add_book(self.b1)
        self.lib.add_book(self.b2)

        self.lib.add_member(self.p1)
        self.lib.add_member(self.p2)

    def teardown_method(self, method):
        del self.lib
        del self.b1
        del self.b2
        del self.b3
        del self.b4
        del self.not_book


class TestBook(BaseTest):

    def test_book_valid(self):
        assert isinstance(self.b1, Book)

    def test_book_not_valid(self):
        assert not isinstance(self.not_book, Book)


class TestPerson(BaseTest):
    @pytest.mark.parametrize(
        "instance,id",
        [
            (Person("James"), 0),
            (Person("Doe"), 1),
        ],
    )
    def test_person_id(self, instance, id):
        assert instance.id == id


class TestLibrarySystem(BaseTest):
    def test_person_eligibility_raise_error(self):
        with pytest.raises(ValueError, match="Not a Member"):
            self.lib.is_eligible(person=self.p3, book=self.b1)

    def test_person_eligible_unborrowed(self):
        "This user has not borrwed the book before"
        is_eligible = self.lib.is_eligible(person=self.p1, book=self.b1)
        assert is_eligible == True

    def test_person_eligible_borrowed(self):
        "This user has borrwed a book and returned it"
        self.lib._transactions[self.p1][self.b1] = [
            {
                "date_borrowed": "Today",
                "return_deadline": "Tomorrow",
                "return_date": None,
                "is_returned": True,
                "quantity": 2,
            },
            {
                "date_borrowed": "Today",
                "return_deadline": "Next Week",
                "return_date": None,
                "is_returned": True,
                "quantity": 2,
            },
        ]
        is_eligible = self.lib.is_eligible(person=self.p1, book=self.b1)
        assert is_eligible == True

    # @pytest.mark.skip
    def test_person_ineligible(self):
        "This user has not returned a borrowed book"
        self.lib._transactions[self.p1][self.b1] = [
            {
                "date_borrowed": "Today",
                "return_deadline": "Tomorrow",
                "return_date": None,
                "is_returned": False,
                "quantity": 2,
            },
            {
                "date_borrowed": "Today",
                "return_deadline": "Next Week",
                "return_date": None,
                "is_returned": True,
                "quantity": 2,
            },
        ]
        is_eligible = self.lib.is_eligible(person=self.p1, book=self.b1)
        assert is_eligible == False

    def test_book_not_valid_error(self):
        "Book not valid for borrow book function"
        with pytest.raises(ValueError, match="Not a Valid Book"):
            self.lib.borrow_book(person=self.p1, book="Invalid Book", number=2)

    def test_book_not_found_error(self):
        "Book not found for borrow book function"
        with pytest.raises(ValueError, match="Book Not Found"):
            self.lib.borrow_book(person=self.p1, book=self.b3, number=2)

    def test_borrow_book_success(self):
        res = self.lib.borrow_book(person=self.p1, book=self.b2, number=2)
        assert res == True

    def test_borrow_book_fail(self):
        self.lib._transactions[self.p1][self.b1] = [
            {
                "date_borrowed": "Today",
                "return_deadline": "Tomorrow",
                "return_date": None,
                "is_returned": False,
                "quantity": 2,
            },
            {
                "date_borrowed": "Today",
                "return_deadline": "Next Week",
                "return_date": None,
                "is_returned": True,
                "quantity": 2,
            },
        ]
        assert self.lib.borrow_book(person=self.p1, book=self.b1, number=1) == False

    @pytest.mark.parametrize("number, output", [(5, True), (1, True)])
    def test_return_book_with_different_numbers(self, number, output):
        "Return book with different return numbers"
        self.lib.borrow_book(person=self.p1, book=self.b1, number=2)
        res = self.lib.return_book(person=self.p1, book=self.b1, number=number)
        assert res == output

    @pytest.mark.parametrize("number", [0, -1])
    def test_return_book_with_different_numbers_less_than_one_raise_error(self, number):
        "For if a number less than zero tries to be returned"
        with pytest.raises(ValueError, match="Must return at least one book"):
            self.lib.borrow_book(person=self.p1, book=self.b1, number=2)
            self.lib.return_book(person=self.p1, book=self.b1, number=number)

    @pytest.mark.parametrize(
        "borrowed_number, returned_number, quantity_left",
        [
            (2, 1, 4),
            (1, 1, 5),
        ],
    )
    def test_return_book_with_book_quantity_changing(
        self, borrowed_number, returned_number, quantity_left
    ):
        "Check that the book quantity increases when returned"
        self.lib.borrow_book(person=self.p1, book=self.b1, number=borrowed_number)
        self.lib.return_book(person=self.p1, book=self.b1, number=returned_number)
        assert self.b1.quantity == quantity_left
