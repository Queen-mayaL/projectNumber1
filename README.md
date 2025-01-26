# Project Name
A web application for user and manager dashboards, authentication, and customer-book management.

## Features
- **Signup**: Users can register with their details, including validation for inputs like email, phone, and birthdate.
- **Login**: Users can log in securely with JWT-based authentication.
- **Role-Based Dashboards**: Separate dashboards for managers and regular users, accessible based on roles.
- **Book Management**: Users can view their loaned books and associated details.
- **Guest Watch List**: Additional functionality for guest users (implementation pending).

## Technologies Used
- **Backend**: Flask (Python)
- **Database**: SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Password Hashing**: Flask-Bcrypt
- **Frontend**: (Optional, if any frontend is developed or integrated)
- **Logging**: Python's logging module for error tracking and debugging

## Endpoints
### Authentication
1. **POST** `/signup`: Create a new customer account.
2. **POST** `/login`: Login to retrieve a JWT token.

### Dashboards
1. **GET** `/manager`: Manager-specific dashboard (JWT required).
2. **GET** `/user`: User-specific dashboard (JWT required).

### Book Management
1. **GET** `/findCustomersBooks`: Retrieve the list of books loaned by the logged-in user.
2. **GET** `/guestWatchList`: Endpoint for guest users to view a watchlist (pending implementation).

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Queen-mayaL/projectNumber1.git
   cd projectNumber1
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   - Update the database connection string in the configuration file.
   - Run migrations or create tables manually using SQLAlchemy models.

5. Run the application:
   ```bash
   flask run
   ```

## Configuration
- Update environment variables for the following:
  - `SECRET_KEY` for Flask sessions.
  - `JWT_SECRET_KEY` for JWT authentication.
  - Database connection string.

## Logging
- The application uses Python's logging module to track actions and errors.
- Logs are categorized into `info`, `debug`, `warning`, and `error` levels for clarity.

## Future Enhancements
- Complete implementation of the `guestWatchList` endpoint.
- Add frontend support with frameworks like React or Angular.
- Improve unit and integration testing coverage.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

---

**Contributors**
- Maya Levi

Feel free to contribute or raise issues for improvement!