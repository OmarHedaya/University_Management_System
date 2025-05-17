import time
import Library_DB
from multipledispatch import dispatch                                    

class Library:
    def __init__(self):
        self.__books = [(book[0],book[1]) for book in Library_DB.get_all_books()]
        self.__library_id = [student[1] for student in Library_DB.get_all_students_id()]
        self.__employee_id = [employee[1] for employee in Library_DB.get_all_employees_id()]

    def update_books(self):
        self.__books = [(book[0],book[1]) for book in Library_DB.get_all_books()]

    def update_library_id(self):
        self.__library_id = [student[1] for student in Library_DB.get_all_students_id()]

    def update_employee_id(self):
        self.__employee_id = [employee[1] for employee in Library_DB.get_all_employees_id()]

    def add_book(self, book_name):
        if not any(book[1] == book_name for book in self.__books):
            Library_DB.add_book(book_name)
            self.update_books()
            print(f"{book_name} book added to library")
        else:
            print("Book already registered")

    def remove_book(self, book_name):
        if any(book[1] == book_name for book in self.__books):
            Library_DB.remove_book(book_name)
            self.update_books()
            print(f"{book_name} book removed from library")
        else:
            print("Book not registered")

    @dispatch(str,str)
    def borrow_book(self, student_id, book_name):
        if any(book[0] == book_name for book in self.__books):
            Library_DB.borrow_book(student_id, book_name)
            self.update_books()
        else:
            print(f"{book_name} book not registered")

    @dispatch(str, int)
    def borrow_book(self, student_id, book_id):
        if any(book[1] == book_id for book in self.__books):
            Library_DB.borrow_book(student_id,book_id)
            self.update_books()
        else:
            print("book not registered")

    def return_book(self, book_name):
        if not any(book[1] == book_name for book in self.__books):
            Library_DB.return_book(book_name)
            self.update_books()
        else:
            print(f"{book_name} book already exists in library")

    def check_availability_books(self, book_name):
        if any(book[0] == book_name for book in self.__books):
            print(f"{book_name} book is available")
        else:
            print(f"{book_name} book is not available")

    def add_library_id(self,student_id):
        if id not in self.__library_id:
            Library_DB.add_student(student_id)
            self.update_library_id()
        else:
            print("ID already registered")

    def remove_library_id(self,student_id):
        try:
            student_id = int(student_id)
            if student_id in self.__library_id:
                Library_DB.remove_student(student_id)
                self.update_library_id()
            else:
                print("ID not registered")
        except ValueError:
            print("Invalid ID format. Please enter a numeric ID.")

    def students_login_id(self, student_id):
        if student_id.lower() == "register":
            while True:
                try:
                    student_id = int(input("Enter your ID: "))
                    if student_id in self.__library_id:
                        print(f"ID {student_id} already registered")
                        return -1
                    else:
                        self.add_library_id(student_id)
                        return -1
                except ValueError:
                    print("Please enter a valid numeric ID!")
        else:
            try:
                if int(student_id) in self.__library_id:
                    print(f"Welcome ID {student_id}!")
                else:
                    print(f"Please register")
                    return -1
            except ValueError:
                print("Invalid ID format. Please enter a numeric ID.")
                return -1

    def employees_login_id(self, student_id):
        try:
            if int(student_id) in self.__employee_id:
                print(f"Welcome ID {student_id}!")
            else:
                print("You are not an employee!")
                return -1
        except ValueError:
            print("Invalid ID format. Please enter a numeric ID.")
            return -1

    @staticmethod
    def finalization():
         while True:
            final = input("Any other services?(Y/N)").lower()
            if final == "y":
                return -2
            elif final == "n":
                print("Thank you for using this service!")
                return -3
            else:
                print("Please enter a valid input!")
                continue


    def services(self, student_id, is_student=True):
        while True:
            if is_student:
                menu = "1) Borrow\n2) Return\n3) Check availability books\n4) Exit\n"
            else:
                menu = "1) Add\n2) Remove\n3) Check availability\n4) Remove Student ID\n5) Exit\n"

            service = input(f"Please choose the number of the service:\n{menu}")
            try:
                if int(service) == 1:

                    if is_student:
                        Library_DB.show_books()
                        book = input("Please enter the name or index of the book:")
                        if book.isdigit():
                            book_id = int(book)
                            self.borrow_book(student_id, book_id)
                        else:
                            book = book.lower()
                            self.borrow_book(student_id, book)
                    else:
                        book=input("Please enter the name of the book:")
                        self.add_book(book)

                elif int(service) == 2:
                    if is_student:
                        book = input("Please enter the name of the book:").lower()
                        self.return_book(book)
                    else:
                        Library_DB.show_books()
                        book = input("Please enter the name or the index of the book:")
                        if book.isdigit():
                            book_id = int(book)
                            self.remove_book(book_id)
                        else:
                            book = book.lower()
                            self.remove_book(book)

                elif int(service) == 3:
                    book = input("Please enter the name of the book:")
                    self.check_availability_books(book)

                elif int(service) == 4:
                    if is_student:
                        print("Thank you for using this service!")
                        return -1
                    else:
                        student_id = input("Please enter the ID of the student to remove:")
                        self.remove_library_id(student_id)

                elif int(service) == 5:
                    print("Thank you for using this service!")
                    return -1
            except ValueError:
                print("Please enter a valid number!")
                continue

            final = self.finalization()
            if final == -2:
                continue
            elif final == -3:
                return -1

    def main(self):
        print("Welcome to the library service!")
        while True:
            person = input("Student or Employee?\n").lower()
            if person == "student":
                while True:
                    student_id = input("Please enter your ID (type register if you want to register):")
                    if self.students_login_id(student_id) == -1:
                        continue
                    if self.services(student_id, is_student=True) == -1:
                        time.sleep(3)
                        break
                break
            elif person == "employee":
                while True:
                    student_id = input("Please enter your ID: ")
                    if self.employees_login_id(student_id) == -1:
                        continue
                    if self.services(student_id, is_student=False) == -1:
                        time.sleep(3)
                        break
                break
            else:
                print("Please enter a valid input!")
                continue

library1 = Library()
library1.main()