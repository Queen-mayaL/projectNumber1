import logging
import jwt
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, get_jwt, get_jwt_identity
from sqlalchemy import Column, Integer, String, Boolean, create_engine, ForeignKey, Date, and_
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import re

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5502"}})

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler("app.log"),
#         logging.StreamHandler()
#     ]
# )
logging.basicConfig(level=logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.orm').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///library.db"
engine = create_engine(DATABASE_URL, echo=True, pool_size=10, max_overflow=20, pool_timeout=30)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=180)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
app.config['JWT_SECRET_KEY'] = 'your-very-secret-key'


jwt = JWTManager(app)
bcrypt = Bcrypt(app)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    age = Column(Integer(), nullable=True)
    birthDate = Column(Date(), nullable=False)
    city = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phoneNumber = Column(String(15), unique=True, nullable=False)
    role = Column(String(20), nullable=False, default="user")
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Customer(id={self.id}, firstName={self.firstName}, lastName={self.lastName}, city={self.city}, age={self.age}, birthDate={self.birthDate}, active={self.active}, phoneNumber={self.phoneNumber}, email={self.email}, role={self.role}, username={self.username}, password={self.password})>"

class Loan(Base):
    __tablename__ = "loans"
    custId = Column(Integer, ForeignKey("customers.id"), nullable=False)
    bookId = Column(Integer, ForeignKey("books.id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    loanDate = Column(Date(), nullable=False)
    expected_returnDate = Column(Date(), nullable=False)
    returnDate = Column(Date(), nullable=True)
    lateDays_num = Column(Integer, nullable=True)
    isLate = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Loan(id={self.id}, custId={self.custId}, bookId={self.bookId}, loanDate={self.loanDate}, expected_returnDate={self.expected_returnDate}, returnDate={self.returnDate}, lateDays_num={self.lateDays_num}, isLate={self.isLate}, active={self.active})>"

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    author = Column(String(100), nullable=False)
    publishYear = Column(String(4), nullable=False)
    bookLoanType = Column(Integer, nullable=False)
    isLoaned = Column(Boolean, default=True)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Book(id={self.id}, name={self.name}, author={self.author}, publishYear={self.publishYear}, bookLoanType={self.bookLoanType}, isLoaned={self.isLoaned}, active={self.active})>"

class Type(Base):
    __tablename__ = "loanTypes"
    loanType = Column(Integer, primary_key=True, autoincrement=True)
    num_of_days = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Type(loanType={self.loanType}, num_of_days={self.num_of_days})>"

Base.metadata.create_all(bind=engine)

def get_db_session():
    return SessionLocal()

@app.route("/")
def hello():
    logger.debug("Hello endpoint accessed")
    return {"msg":"hello!"}

@app.route("/books", methods=["GET", "POST", "DELETE", "PUT"])
def books_endpoint():
    db = get_db_session()
    try:
        if request.method == 'GET':
            books = db.query(Book).filter(Book.active == True).all()
            return jsonify([{
                "id": Book.id,
                "name": Book.name,
                "author": Book.author,
                "publishYear": Book.publishYear,
                "bookLoanType": Book.bookLoanType,
                "isLoaned": Book.isLoaned
            }
            for Book in books])

        if request.method == 'POST':
            data = request.get_json()
            name = data.get("name")
            author = data.get("author")
            publishYear = data.get("publishYear")
            bookLoanType = data.get("bookLoanType")

            current_year = datetime.now().year

            if not name or not author or not publishYear or not bookLoanType:
                return jsonify({"error": "Missing required fields"}), 400
            
            if len(name) < 2 or len(name) > 100:
                return jsonify({"error": "Book Name should be between 3 to 100 characters."}), 400
       
            if len(author) < 3 or len(author) > 100:
                return jsonify({"error": "Author Name should be between 3 to 100 characters."}), 400
            
            if not publishYear or int(publishYear) < 1000 or int(publishYear) > datetime.now().year:
                return jsonify({"error": "Publish Year must be a valid year between 1000 and the current year."}), 400

            if not bookLoanType or int(bookLoanType) < 1 or int(bookLoanType) > 3:
                return jsonify({"error": "Loan Type must be a positive number between 1 and 3."}), 400

            try:
                new_book = Book(name=name, author=author, publishYear=publishYear, bookLoanType=bookLoanType, isLoaned=False, active=True)
                db.add(new_book)
                db.commit()
                return jsonify({'status': 201, 'message': 'Book created successfully'}), 201
            except Exception as e:
                print(f"Error occurred while adding book: {e}")
                return jsonify({"error": "Failed to create book due to internal error."}), 500
        
        if request.method == 'DELETE':
            data = request.get_json()
            id = data.get("id")

            book = db.query(Book).filter(Book.id == id).first()
            if Book:
                book.active = False
                db.commit()
                logger.info(f"Deleted book with ID: {book_id}")
                return jsonify({"message": "Book deleted successfully"})
            logger.warning(f"Book with ID {book_id} not found for deletion")
            return jsonify({"error": "Book bot found"}),404

        if request.method == 'PUT':
            data = request.get_json()
            id = data.get('id')
            custId = data.get("custId")

            book = db.query(Book).filter(Book.id == id).first()
            customer = db.query(Customer).filter(Customer.id == custId).first()
            
            loanDate = datetime.today().date()        
            if book:
                loanType = db.query(Type).filter(Type.loanType == book.bookLoanType).first()
                loanType = db.query(Type).filter(Type.loanType == book.bookLoanType).first()
                if not loanType:
                    return jsonify({"error": "Invalid loan type"}), 400
                numOfDays = loanType.num_of_days
                expected_returnDate = loanDate + timedelta(days=numOfDays)

                if book.isLoaned == 0:
                    book.isLoaned = True
                    new_loan = Loan(bookId=id, custId=custId, loanDate=loanDate, expected_returnDate=expected_returnDate, returnDate=None, lateDays_num=0)
                    db.add(new_loan)
                db.commit()
                logger.info(f"Updated book: {book}")
                return jsonify({"message": "loan updated successfully"})
            logger.warning(f"Book with ID {book_id} not found for update")
            return jsonify({"error": "loan not found"}), 404
    except Exception as e:
        logger.error(f"Error in books endpoint: {e}")
    return jsonify({"error": "An error occurred"}), 500


@app.route("/customers", methods=["GET", "POST", "DELETE", "PUT"])
def customers_endpoint():
    db = get_db_session()
    try:
        if request.method == 'GET':
            customers = db.query(Customer).filter(Customer.active == True).all()
            today = datetime.today()
            updated_customers = []

            for customer in customers:
                calculated_age = (
                    today.year - customer.birthDate.year
                    - ((today.month, today.day) < (customer.birthDate.month, customer.birthDate.day))
                )
                
                if customer.age != calculated_age:
                    customer.age = calculated_age
                    updated_customers.append(customer)

            if updated_customers:
                db.commit()
                logger.info(f"Updated ages for {len(updated_customers)} customers.")

            return jsonify([{
                "id": Customer.id,
                "firstName": Customer.firstName,
                "lastName": Customer.lastName,
                "age": Customer.age,
                "city": Customer.city,
                "email": Customer.email,
                "phoneNumber": Customer.phoneNumber
            }
            for Customer in customers])
        
        if request.method == 'POST':
            data = request.get_json()
            firstName = data.get("firstName")
            lastName = data.get("lastName")
            birthDate = data.get("birthDate")
            city = data.get("city")
            email = data.get("email")
            phoneNumber = data.get("phoneNumber")
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")

            if not all([firstName, lastName, birthDate, city, email, phoneNumber, username, password]):
                return jsonify({"error": "All fields are required."}), 400

            if not firstName or len(firstName) < 3:
                return jsonify({"error": "First name must be at least 3 characters long."}), 400

            if not lastName or len(lastName) < 3:
                return jsonify({"error": "Last name must be at least 3 characters long."}), 400

            if not birthDate:
                return jsonify({"error": "Birthdate is required."}), 400
            try:
                birthDate_obj = datetime.strptime(birthDate, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Birthdate must be in the format YYYY-MM-DD."}), 400

            today = datetime.today()
            calculated_age = today.year - birthDate_obj.year - ((today.month, today.day) < (birthDate_obj.month, birthDate_obj.day))

            if calculated_age < 5 or calculated_age > 120:
                return jsonify({"error": "Age must be between 5 and 120."}), 400

            age = calculated_age

            if not city or len(city) < 2:
                return jsonify({"error": "City must be at least 2 characters long."}), 400

            if not email or not validate_email(email):
                return jsonify({"error": "Please provide a valid email address."}), 400
            
            phone_regex = r'^[\d\s\-+()]{10,15}$'
            if not phoneNumber or not re.match(phone_regex, phoneNumber):
                return jsonify({"error": "Phone number must be between 10 and 15 characters and include digits, spaces, '-', '+', or '()'."}), 400
            
            if db.query(Customer).filter(Customer.username == username).first():
                 return jsonify({"error": "Username is already taken."}), 400
            if db.query(Customer).filter_by(email=email).first():
                return jsonify({"error": "Email is already registered."}), 400
            if db.query(Customer).filter_by(phoneNumber=phoneNumber).first():
                return jsonify({"error": "Phone number is already registered."}), 400
            
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_customer = Customer(
                    firstName=firstName,
                    lastName=lastName,
                    age=age,
                    birthDate=birthDate_obj,
                    city=city,
                    email=email,
                    phoneNumber=phoneNumber,
                    username=username,
                    password=hashed_password,
                    role=role,
                    active=True
                )
            db.add(new_customer)
            db.commit()
            logger.info(f"Added new customer: {new_customer}")
            return jsonify({'status': 201, 'message': 'Customer created successfully'}), 201
        
        if request.method == 'DELETE':
            data = request.get_json()
            id = data.get("id")

            customer = db.query(Customer).filter(Customer.id == id).first()
            if customer:
                customer.active = False
                db.commit()
                logger.info(f"Deleted customer with ID: {customer_id}")
                return jsonify({"message": "Customer deleted successfully"})
            logger.warning(f"Customer with ID {customer_id} not found for deletion")
            return jsonify({"error": "Customer bot found"}),404
        
        if request.method == 'PUT':
            data = request.get_json()
            new_firstName = data.get('firstName')
            new_lastName = data.get('lastName')
            new_birthDate = data.get('birthDate')
            new_city = data.get('city')
            new_email = data.get('email')
            new_phoneNumber = data.get('phoneNumber')
            username = data.get("username")
            password = data.get("password")
            role = data.get("role", "user")
            id = data.get('id')

            customer = db.query(Customer).filter(Customer.id == id).first()
            if customer:

                if new_firstName and len(new_firstName) < 3:
                    return jsonify({"error": "First name must be at least 3 characters long."}), 400

                if new_lastName and len(new_lastName) < 3:
                    return jsonify({"error": "Last name must be at least 3 characters long."}), 400

                if new_birthDate:
                    try:
                        new_birthDate_obj = datetime.strptime(new_birthDate, '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({"error": "Birthdate must be in the format YYYY-MM-DD."}), 400

                    today = datetime.today()
                    calculated_age = today.year - new_birthDate_obj.year - ((today.month, today.day) < (new_birthDate_obj.month, new_birthDate_obj.day))

                    if calculated_age < 5 or calculated_age > 120:
                        return jsonify({"error": "Age must be between 5 and 120."}), 400

                    new_age = calculated_age
                else:
                    new_age = customer.age

                if new_city and len(new_city) < 2:
                    return jsonify({"error": "City must be at least 2 characters long."}), 400

                if new_email and (not validate_email(new_email) or db.query(Customer).filter_by(email=new_email).first()):
                    return jsonify({"error": "Please provide a valid email address, or email is already registered."}), 400
                
                phone_regex = r'^[\d\s\-+()]{10,15}$'
                if new_phoneNumber and (not re.match(phone_regex, new_phoneNumber) or db.query(Customer).filter_by(phoneNumber=new_phoneNumber).first()):
                    return jsonify({"error": "Phone number must be between 10 and 15 characters and include digits, spaces, '-', '+', or '()'."}), 400

                if password:
                    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                    customer.password = hashed_password

                if new_firstName:
                    customer.firstName = new_firstName
                if new_lastName:
                    customer.lastName = new_lastName
                if new_age:
                    customer.age = new_age
                if new_birthDate:
                    customer.birthDate = new_birthDate_obj
                if new_city:
                    customer.city = new_city
                if new_email:
                    customer.email = new_email
                if new_phoneNumber:
                    customer.phoneNumber = new_phoneNumber
                if role:
                    customer.role = role

                db.commit()
                logger.info(f"Updated customer: {customer}")
                return jsonify({"message": "Customer updated successfully"})
            logger.warning(f"Customer with ID {id} not found for update")
            return jsonify({"error": "Customer not found"}), 404
    except Exception as e:
        logger.error(f"Error in customers endpoint: {e}")
        return jsonify({"error": "An error occurred"}), 500



@app.route("/loans", methods=["GET", "POST", "DELETE", "PUT"])
def loans_endpoint():
    db = get_db_session()
    try:
        if request.method == 'GET':
            loans = db.query(Loan).filter(Loan.active == True).all()
            logger.info("Fetched all active loans")
            return jsonify([{
                "id": Loan.id,
                "custId": Loan.custId,
                "bookId": Loan.bookId,
                "loanDate": Loan.loanDate.strftime('%Y-%m-%d'),
                "expected_returnDate": Loan.expected_returnDate.strftime('%Y-%m-%d'),
            }
            for Loan in loans])

        #post is in books.

        if request.method == 'DELETE':
            data = request.get_json()
            id = data.get("id")

            loan = db.query(Loan).filter(Loan.id == id).first()
            today = datetime.today().date()

            if loan:
                loan.active = False
                loan.returnDate = today
                if today > loan.expected_returnDate: 
                    late_days = (today - loan.expected_returnDate).days
                    
                    loan.isLate = True
                    loan.lateDays_num = late_days
                book = db.query(Book).filter(Book.id == loan.bookId).first()
                if book:
                    book.isLoaned = False
                db.commit()
                logger.info(f"Deleted loan with ID: {id}")
                return jsonify({"message": "Loan deleted successfully"})
            logger.warning(f"Loan with ID {id} not found for deletion")
            return jsonify({"error": "Loan not found"}),404

    except Exception as e:
        logger.error(f"Error in loans endpoint: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/lateLoans", methods=["GET"])
def lateLoans_endpoint():
    db = get_db_session()
    try:
        if request.method == 'GET':
            loans = db.query(Loan).filter(and_(Loan.active == True, Loan.isLate == True)).all()
            logger.info("Fetched all late loans")
            return jsonify([{
                "id": Loan.id,
                "custId": Loan.custId,
                "bookId": Loan.bookId,
                "loanDate": Loan.loanDate.strftime('%Y-%m-%d'),
                "expected_returnDate": Loan.expected_returnDate.strftime('%Y-%m-%d'),
                "lateDays_num": Loan.lateDays_num
            }
            for Loan in loans])
    except Exception as e:
        logger.error(f"Error in lateLoans endpoint: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/findCustomer", methods=["GET"])
def findCustomer():
    db = get_db_session()
    try:
        if request.method == 'GET':
            firstName = request.args.get("firstName")
            lastName = request.args.get("lastName")
            email = request.args.get("email")
            phoneNumber = request.args.get("phoneNumber")
            city = request.args.get("city")
            username = request.args.get("username")
            role = request.args.get("role")
            id = request.args.get("id")

            filters = []
            if firstName:
                filters.append(Customer.firstName.ilike(f"%{firstName}%"))
            if lastName:
                filters.append(Customer.lastName.ilike(f"%{lastName}%"))
            if email:
                filters.append(Customer.email.ilike(f"%{email}%"))
            if phoneNumber:
                filters.append(Customer.phoneNumber.ilike(f"%{phoneNumber}%"))
            if city:
                filters.append(Customer.city.ilike(f"%{city}%"))
            if id:
                filters.append(Customer.id == int(id))
            if username:
                filters.append(Customer.username.ilike(f"%{username}%"))
            if role:
                filters.append(Customer.role == role)

            customers = db.query(Customer).filter(and_(*filters)).all()
            logger.info(f"Fetched {len(customers)} customers based on search filters")
            return jsonify([{
                "id": customer.id,
                "firstName": customer.firstName,
                "lastName": customer.lastName,
                "age": customer.age,
                "city": customer.city,
                "email": customer.email,
                "phoneNumber": customer.phoneNumber,
                "username": customer.username,
                "role": customer.role
            } for customer in customers])

    except Exception as e:
        logger.error(f"Error in findCustomer endpoint: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/findBook", methods=["GET"])
def findBook():
    db = get_db_session()
    try:
        if request.method == 'GET':
            logger.info(f"find book succeded!")
            name = request.args.get("name")
            author = request.args.get("author")
            publishYear = request.args.get("publishYear")

            filters = []
            if name:
                filters.append(Book.name.ilike(f"%{name}%"))
            if author:
                filters.append(Book.author.ilike(f"%{author}%"))
            if publishYear:
                filters.append(Book.publishYear == publishYear)


            books = db.query(Book).filter(and_(*filters)).all()

            return jsonify([{
                "id": Book.id,
                "name": Book.name,
                "author": Book.author,
                "publishYear": Book.publishYear,
                "bookLoanType": Book.bookLoanType,
                "isLoaned": Book.isLoaned
            }
            for Book in books])

    except Exception as e:
        logger.error(f"Error in findBook endpoint: {e}")
        return jsonify({"error": "An error occurred"}), 500

@app.route("/customerToUpdate", methods=["GET"])
def getCustomerData():
    db = get_db_session()
    try:
        if request.method == 'GET':
            id = int(request.args.get('id'))
            customer = db.query(Customer).filter(Customer.id == id).first()
            logger.info(f"Fetched customer data for ID: {id}")
            formatted_birth_date = customer.birthDate.strftime("%Y-%m-%d") if customer.birthDate else None
            
            return jsonify({
                "firstName": customer.firstName,
                "lastName": customer.lastName,
                "birthDate": formatted_birth_date,
                "city": customer.city,
                "email": customer.email,
                "phoneNumber": customer.phoneNumber,
                "username": customer.username,
                "role": customer.role
            })

    except Exception as e:
        logger.error(f"Error fetching customer data: {e}")
        return jsonify({"error": "An error occurred"}), 500

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


@app.route('/signup', methods=['POST'])
def signup():
    db = get_db_session()
    logger.info("Signup endpoint accessed")
    if request.method == 'POST':
        data = request.get_json()
        logger.debug(f"Received signup data: {data}")
        firstName = data.get("firstName")
        lastName = data.get("lastName")
        birthDate = data.get("birthDate")
        city = data.get("city")
        email = data.get("email")
        phoneNumber = data.get("phoneNumber")
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "user")

        if not all([firstName, lastName, birthDate, city, email, phoneNumber, username, password]):
            logger.warning("Missing required fields in signup data")
            return jsonify({"error": "All fields are required."}), 400

        try:
            birthDate_obj = datetime.strptime(birthDate, '%Y-%m-%d').date()
            today = datetime.today()
            calculated_age = today.year - birthDate_obj.year - (
                (today.month, today.day) < (birthDate_obj.month, birthDate_obj.day)
            )
            if calculated_age < 5 or calculated_age > 120:
                logger.warning(f"Invalid age: {calculated_age}")
                return jsonify({"error": "Age must be between 5 and 120."}), 400
        except ValueError:
            logger.error(f"Invalid birthdate format: {birthDate}")
            return jsonify({"error": "Birthdate must be in the format YYYY-MM-DD."}), 400

        if db.query(Customer).filter(Customer.username == username).first():
            logger.warning(f"Username already taken: {username}")
            return jsonify({"error": "Username is already taken."}), 400
        if db.query(Customer).filter_by(email=email).first():
            logger.warning(f"Email already registered: {email}")
            return jsonify({"error": "Email is already registered."}), 400
        if db.query(Customer).filter_by(phoneNumber=phoneNumber).first():
            logger.warning(f"Phone number already registered: {phoneNumber}")
            return jsonify({"error": "Phone number is already registered."}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_customer = Customer(
            firstName=firstName,
            lastName=lastName,
            age=calculated_age,
            birthDate=birthDate_obj,
            city=city,
            email=email,
            phoneNumber=phoneNumber,
            username=username,
            password=hashed_password,
            role=role,
            active=True
        )
        db.add(new_customer)
        db.commit()
        logger.info(f"New customer added: {new_customer}")
        return jsonify({'status': 201, 'message': 'Customer created successfully'}), 201


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    db = get_db_session()
    logger.info("Login endpoint accessed")
    try:
        data = request.get_json()
        logger.debug(f"Login data received: {data}")
        if not data:
            logger.warning("No data provided in login request")
            return jsonify({"error": "No data provided"}), 400

        Nusername = data.get("username")
        Npassword = data.get("password")

        if not Nusername or not Npassword:
            logger.warning("Username or password missing in login request")
            return jsonify({"error": "Username or password missing"}), 400

        customer = db.query(Customer).filter_by(username=Nusername).first()
        if not customer or not bcrypt.check_password_hash(customer.password, Npassword):
            logger.warning(f"Invalid login attempt for username: {Nusername}")
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = create_access_token(identity=customer.username)
        logger.info(f"Login successful for username: {Nusername}")
        return jsonify({
            "access_token": access_token,
            "role": customer.role,
            "message": "Login successful"
        }), 200
    except Exception as e:
        logger.error(f"Error during login: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


@app.route('/manager', methods=['GET'])
@jwt_required()
def manager_dashboard():
    db = get_db_session()
    username = get_jwt_identity()
    logger.info(f"Manager dashboard accessed by username: {username}")

    customer = db.query(Customer).filter_by(username=username).first()
    if not customer or customer.role != 'manager':
        logger.warning(f"Access denied for username: {username}")
        return jsonify({"error": "Access denied"}), 403

    logger.info(f"Manager dashboard access granted for username: {username}")
    return jsonify({"message": "Welcome to the Manager Dashboard"}), 200


@app.route('/user', methods=['GET'])
@jwt_required()
def user_dashboard():
    db = get_db_session()
    username = get_jwt_identity()
    logger.info(f"User dashboard accessed by username: {username}")

    customer = db.query(Customer).filter_by(username=username).first()
    if not customer or customer.role != 'user':
        logger.warning(f"Access denied for username: {username}")
        return jsonify({"error": "Access denied"}), 403

    logger.info(f"User dashboard access granted for username: {username}")
    return jsonify({"message": "Welcome to the User Dashboard"}), 200


@app.route("/findCustomersBooks", methods=["GET"])
@jwt_required()
def findCustomersBooks():
    db = get_db_session()
    try:
        username = get_jwt_identity()
        logger.info(f"findCustomersBooks accessed by username: {username}")

        customer = db.query(Customer).filter_by(username=username).first()
        if not customer:
            logger.warning(f"User not found: {username}")
            return jsonify({"error": "User not found"}), 404

        loans = db.query(Loan).filter(Loan.custId == customer.id).all()
        loaned_books = []
        for loan in loans:
            book = db.query(Book).filter_by(id=loan.bookId).first()
            if not book:
                logger.warning(f"Book not found for loan ID: {loan.id}")
                continue
            loaned_books.append({
                "book_name": book.name,
                "author": book.author,
                "publish_year": book.publishYear,
                "isLate": loan.isLate
            })

        logger.info(f"Loaned books retrieved for username: {username}")
        return jsonify(loaned_books)
    except Exception as e:
        logger.error(f"Error in findCustomersBooks: {e}")
        return jsonify({"error": "An error occurred"}), 500


@app.route("/guestWatchList", methods=["GET"])
def guestWatchList_endpoint():
    logger.info("Guest watch list accessed")
    db = get_db_session()
    if request.method == 'GET':
        books = db.query(Book).filter(Book.active == True).all()
        return jsonify([{
            "name": Book.name,
            "author": Book.author,
            "publishYear": Book.publishYear,
            "isLoaned": Book.isLoaned
        }
        for Book in books])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)