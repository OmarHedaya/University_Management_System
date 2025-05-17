import sqlite3
from multipledispatch import dispatch

conn = sqlite3.connect('Library.db')

c = conn.cursor()

def show_books():
    c.execute("SELECT * FROM books ORDER BY book_id")
    items = c.fetchall()
    for item in items:
        print(item[1], item[0])

def get_all_books():
    c.execute("SELECT * FROM books")
    items = c.fetchall()
    return items

def add_book(book_name):
    c.execute("""
    INSERT INTO books (book_name)
    VALUES (?)
    """, (book_name,))
    conn.commit()

@dispatch(str)
def remove_book(book_name):
    c.execute("""
    DELETE FROM books WHERE book_name = ?
    """, (book_name,))
    conn.commit()

@dispatch(int)
def remove_book(book_id):
    c.execute("""
    DELETE FROM books WHERE book_id = ?
    """, (book_id,))
    conn.commit()

@dispatch(str, str)
def borrow_book(user_id, book_name):
    c.execute("SELECT * FROM books WHERE book_name = ?", (book_name,))
    item = c.fetchone()
    if item:
        book_id, book_name = item[1], item[0]
        c.execute("INSERT INTO borrowed_books (borrowed_books_name, borrowed_books_id) VALUES (?, ?)", (book_name, book_id))
        c.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        conn.commit()
        print(f"{user_id} borrowed '{book_name}' from library.")
    else:
        print("Book not found.")

@dispatch(str, int)
def borrow_book(user_id, book_id):
    c.execute("SELECT * FROM books WHERE book_id = ?", (book_id,))
    item = c.fetchone()
    if item:
        book_id, book_name = item[1], item[0]
        c.execute("INSERT INTO borrowed_books (borrowed_books_name, borrowed_books_id) VALUES (?, ?)", (book_name, book_id))
        c.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        conn.commit()
        print(f"{user_id} borrowed '{book_name}' from library.")
    else:
        print("Book not found.")

def return_book(book_name):
    c.execute("SELECT * FROM borrowed_books WHERE borrowed_books_name = ?", (book_name,))
    item = c.fetchone()
    if item:
        book_id, book_name = item[1], item[0]
        c.execute("INSERT INTO books (book_id, book_name) VALUES (?, ?)", (book_id, book_name))
        c.execute("DELETE FROM borrowed_books WHERE borrowed_books_name = ?", (book_name,))
        conn.commit()
        print(f"'{book_name}' returned to library.")
    else:
        print("Book not found in borrowed books.")

def check_availability_books(book_name):
    c.execute("""
    SELECT * FROM books WHERE book_name = ?
    """, (book_name,))
    item = c.fetchone()
    if item:
        print(f"{book_name} is available in the library")
    else:
        print(f"{book_name} is not available in the library")

def get_all_students_id():
    c.execute("SELECT rowid,* FROM students")
    items = c.fetchall()
    return items

def get_all_employees_id():
    c.execute("SELECT rowid,* FROM employees")
    items = c.fetchall()
    return items

def add_student(student_id):
    c.execute("""
    INSERT INTO students (student_id)
    VALUES (?)
    """, (student_id,))
    conn.commit()
    print(f"ID {student_id} added to library")

def remove_student(student_id):
    c.execute("""
    DELETE FROM students WHERE student_id = ?
    """, (student_id,))
    conn.commit()
    print(f"Student with ID {student_id} removed from library")