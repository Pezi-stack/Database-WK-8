# main.py
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

app = FastAPI(title="Library Management System API", version="1.0.0")

# Database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Change as needed
            password="",  # Change as needed
            database="library_db"
        )
        return connection
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Pydantic models
class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    nationality: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    author_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    author_id: int
    isbn: str
    published_year: Optional[int] = None
    genre: Optional[str] = None
    quantity_available: int = 0

class BookCreate(BookBase):
    pass

class Book(BookBase):
    book_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class MemberBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    membership_date: date

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    member_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    book_id: int
    member_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
    loan_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Authors endpoints
@app.get("/authors", response_model=List[Author])
def get_authors(connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors")
    authors = cursor.fetchall()
    cursor.close()
    connection.close()
    return authors

@app.get("/authors/{author_id}", response_model=Author)
def get_author(author_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors WHERE author_id = %s", (author_id,))
    author = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

@app.post("/authors", response_model=Author, status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO authors (first_name, last_name, birth_date, nationality) VALUES (%s, %s, %s, %s)",
        (author.first_name, author.last_name, author.birth_date, author.nationality)
    )
    connection.commit()
    author_id = cursor.lastrowid
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors WHERE author_id = %s", (author_id,))
    new_author = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return new_author

@app.put("/authors/{author_id}", response_model=Author)
def update_author(author_id: int, author: AuthorCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE authors SET first_name = %s, last_name = %s, birth_date = %s, nationality = %s WHERE author_id = %s",
        (author.first_name, author.last_name, author.birth_date, author.nationality, author_id)
    )
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Author not found")
    
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors WHERE author_id = %s", (author_id,))
    updated_author = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return updated_author

@app.delete("/authors/{author_id}")
def delete_author(author_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM authors WHERE author_id = %s", (author_id,))
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Author not found")
    
    cursor.close()
    connection.close()
    return {"message": "Author deleted successfully"}

# Books endpoints
@app.get("/books", response_model=List[Book])
def get_books(connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()
    return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books (title, author_id, isbn, published_year, genre, quantity_available) VALUES (%s, %s, %s, %s, %s, %s)",
        (book.title, book.author_id, book.isbn, book.published_year, book.genre, book.quantity_available)
    )
    connection.commit()
    book_id = cursor.lastrowid
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    new_book = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return new_book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: BookCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE books SET title = %s, author_id = %s, isbn = %s, published_year = %s, genre = %s, quantity_available = %s WHERE book_id = %s",
        (book.title, book.author_id, book.isbn, book.published_year, book.genre, book.quantity_available, book_id)
    )
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Book not found")
    
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
    updated_book = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return updated_book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Book not found")
    
    cursor.close()
    connection.close()
    return {"message": "Book deleted successfully"}

# Members endpoints
@app.get("/members", response_model=List[Member])
def get_members(connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    cursor.close()
    connection.close()
    return members

@app.get("/members/{member_id}", response_model=Member)
def get_member(member_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    member = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return member

@app.post("/members", response_model=Member, status_code=status.HTTP_201_CREATED)
def create_member(member: MemberCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO members (first_name, last_name, email, phone_number, membership_date) VALUES (%s, %s, %s, %s, %s)",
        (member.first_name, member.last_name, member.email, member.phone_number, member.membership_date)
    )
    connection.commit()
    member_id = cursor.lastrowid
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    new_member = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return new_member

@app.put("/members/{member_id}", response_model=Member)
def update_member(member_id: int, member: MemberCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE members SET first_name = %s, last_name = %s, email = %s, phone_number = %s, membership_date = %s WHERE member_id = %s",
        (member.first_name, member.last_name, member.email, member.phone_number, member.membership_date, member_id)
    )
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Member not found")
    
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE member_id = %s", (member_id,))
    updated_member = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return updated_member

@app.delete("/members/{member_id}")
def delete_member(member_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM members WHERE member_id = %s", (member_id,))
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Member not found")
    
    cursor.close()
    connection.close()
    return {"message": "Member deleted successfully"}

# Loans endpoints
@app.get("/loans", response_model=List[Loan])
def get_loans(connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loans")
    loans = cursor.fetchall()
    cursor.close()
    connection.close()
    return loans

@app.get("/loans/{loan_id}", response_model=Loan)
def get_loan(loan_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loans WHERE loan_id = %s", (loan_id,))
    loan = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

@app.post("/loans", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date) VALUES (%s, %s, %s, %s, %s)",
        (loan.book_id, loan.member_id, loan.loan_date, loan.due_date, loan.return_date)
    )
    connection.commit()
    loan_id = cursor.lastrowid
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loans WHERE loan_id = %s", (loan_id,))
    new_loan = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return new_loan

@app.put("/loans/{loan_id}", response_model=Loan)
def update_loan(loan_id: int, loan: LoanCreate, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE loans SET book_id = %s, member_id = %s, loan_date = %s, due_date = %s, return_date = %s WHERE loan_id = %s",
        (loan.book_id, loan.member_id, loan.loan_date, loan.due_date, loan.return_date, loan_id)
    )
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Loan not found")
    
    cursor.close()
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM loans WHERE loan_id = %s", (loan_id,))
    updated_loan = cursor.fetchone()
    cursor.close()
    connection.close()
    
    return updated_loan

@app.delete("/loans/{loan_id}")
def delete_loan(loan_id: int, connection=Depends(get_db_connection)):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM loans WHERE loan_id = %s", (loan_id,))
    connection.commit()
    
    if cursor.rowcount == 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Loan not found")
    
    cursor.close()
    connection.close()
    return {"message": "Loan deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)