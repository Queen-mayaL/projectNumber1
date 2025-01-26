const apiUrl = 'http://127.0.0.1:5000'
function fetchBooks() {

  const name = document.getElementById('S-book-name').value;
  const author = document.getElementById('S-book-author').value;
  const publishYear = document.getElementById('S-book-year').value;
  
  const searchParams = {};
  if (name) searchParams.name = name;
  if (author) searchParams.author = author;
  if (publishYear) searchParams.publishYear = publishYear;

  let url = `${apiUrl}/books`;
  if (Object.keys(searchParams).length > 0) {
    url = `${apiUrl}/findBook`;
  }

  axios.get(url, { params: searchParams })
    .then(response => {
      const books = response.data;
      const booksTableBody = document.querySelector('#books-table tbody');
      booksTableBody.innerHTML = '';

      if (books.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" style="text-align: center;">No books found</td>`;
        booksTableBody.appendChild(row);
      } else {

        books.forEach(book => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${book.id}</td>
            <td>${book.name}</td>
            <td>${book.author}</td>
            <td>${book.publishYear}</td>
            <td>${book.isLoaned ? 'Yes' : 'No'}</td>
            <td>
              <button class="loan-button" onclick="loanBook(${book.id}, ${book.isLoaned})">
                Loan
              </button>
              <button class="loan-button" onclick="deleteBook(${book.id})">
                Delete
              </button>
            </td>
          `;
          booksTableBody.appendChild(row);
        });
      }
    })
    .catch(error => {
      console.error('Error fetching books data:', error);
    });
}


function addBook() {
  const name = document.getElementById('book-name').value;
  const author = document.getElementById('book-author').value;
  const publishYear = document.getElementById('book-year').value;
  const loanType = document.getElementById('loan-type').value;

  console.log("Length of book name:", name.length)
  console.log(name)

  if (!name || !author || !publishYear || !loanType) {
    alert("Please fill in all fields.");
    return;
  }

  if (!name || !name.length > 2 || !name.length > 100) {
    alert("Book Name should be between 3 to 100 characters.");
    return;
  }
  
  if (!author || author.length < 3 || author.length > 100) {
    alert("Author Name should be between 3 to 100 characters.");
    return;
  }
  
  if (!publishYear || isNaN(publishYear) || publishYear < 1000 || publishYear > new Date().getFullYear()) {
    alert("Publish Year must be a valid year between 1000 and the current year.");
    return;
  }
  
  if (!loanType || isNaN(loanType) || loanType <= 0 || loanType > 3) {
    alert("Loan Type must be 1, 2, or 3.");
    return;
  }
  
  const bookData = {
    name: name,
    author: author,
    publishYear: publishYear,
    bookLoanType: loanType
  };

  axios.post(`${apiUrl}/books`, bookData)
    .then(response => {
      alert(response.data.message);
      fetchBooks();
    })
    .catch(error => console.error('Error adding book:', error));
}

const loanBook = (id, isLoaned) => {
  if (isLoaned) {
    alert('This book is already loaned.');
    return;
  }

  const customerId = prompt('Enter customer ID:');

  axios.put(`${apiUrl}/books`, {
    id: id,
    custId: customerId
  })
    .then(response => {
      console.log("loan updated:", response.data);
      fetchBooks();
      fetchLoans();
    })
    .catch(error => {
      console.error("Error updating a loan:", error);
      alert("Error updating loan. Please try again.");
    })
}


function deleteBook(bookId) {
  axios.delete(`${apiUrl}/books`, { data: { id: bookId } })
    .then(response => {
      alert(response.data.message);
      fetchBooks();
    })
    .catch(error => console.error('Error deleting book:', error));
}

function fetchCustomers() {

  const firstName = document.getElementById('customer-first-name').value;
  const lastName = document.getElementById('customer-last-name').value;
  const email = document.getElementById('customer-email').value;
  const phoneNumber = document.getElementById('customer-phone-number').value;
  const city = document.getElementById('customer-city').value;
  const username = document.getElementById('customer-username').value;
  const id = document.getElementById('customer-id').value;
  const role = document.getElementById('update-role').value;


  const searchParams = {};
  if (firstName) searchParams.firstName = firstName;
  if (lastName) searchParams.lastName = lastName;
  if (email) searchParams.email = email;
  if (phoneNumber) searchParams.phoneNumber = phoneNumber;
  if (city) searchParams.city = city;
  if (username) searchParams.username = username;
  if (id) searchParams.id = id;
  if (role) searchParams.role = role;


  let url = `${apiUrl}/customers`;
  if (Object.keys(searchParams).length > 0) {
    url = `${apiUrl}/findCustomer`
  }


  axios.get(url, { params: searchParams })
    .then(response => {
      const customers = response.data;
      const customersTableBody = document.querySelector('#customers-table tbody');
      customersTableBody.innerHTML = ''; 

     
      if (customers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="8" style="text-align: center;">No customers found</td>`;
        customersTableBody.appendChild(row);
      } else {

        customers.forEach(customer => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${customer.id}</td>
            <td>${customer.firstName}</td>
            <td>${customer.lastName}</td>
            <td>${customer.age}</td>
            <td>${customer.city}</td>
            <td>${customer.email}</td>
            <td>${customer.phoneNumber}</td>
            <td>${customer.username}</td>
            <td>
              <button class="loan-button" onclick="deleteCustomer(${customer.id})">
                Delete
              </button>
              <button class="loan-button" onclick="updateCustomer(${customer.id})">
                Update
              </button>
            </td>
          `;
          customersTableBody.appendChild(row);
        });
      }
    })
    .catch(error => {
      console.error('Error fetching customers data:', error);
    });
}



function addCustomer() {
  const firstName = document.getElementById('first-name').value.trim();
  const lastName = document.getElementById('last-name').value.trim();
  const birthDate = document.getElementById('birthDate').value;
  const city = document.getElementById('city').value.trim();
  const email = document.getElementById('email').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!firstName || !lastName || !birthDate || !city || !email || !phone || !username || !password) {
    alert("Please fill in all fields.");
    return;
  }


  if (firstName.length < 3) {
    alert('First name must be at least 3 characters long.');
    return;
  }


  if (lastName.length < 3) {
    alert('Last name must be at least 3 characters long.');
    return;
  }

  const birthDatePattern = /^\d{4}-\d{2}-\d{2}$/;
  if (!birthDate || !birthDatePattern.test(birthDate)) {
    alert('Birthdate must be in the format YYYY-MM-DD.');
    return;
  }

  if (city.length < 2) {
    alert('City must be at least 2 characters long.');
    return;
  }


  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailPattern.test(email)) {
    alert('Please provide a valid email address.');
    return;
  }

  const phonePattern = /^[\d\s\-+()]{10,15}$/;
  if (!phone || !phonePattern.test(phone)) {
    alert('Phone number must be between 10 to 15 digits.');
    return;
  }

  if (username.length < 3) {
    alert('Username must be at least 3 characters long.');
    return;
  }

  if (password.length < 6) {
    alert('Password must be at least 6 characters long.');
    return;
  }


  const customerData = {
    firstName: firstName,
    lastName: lastName,
    birthDate: birthDate,
    city: city,
    email: email,
    phoneNumber: phone,
    username: username,
    password: password
  };


  axios.post(`${apiUrl}/customers`, customerData)
    .then(response => {
      alert(response.data.message);
      fetchCustomers();
    })
    .catch(error => {
      console.error('Error adding customer:', error);
      alert(error.response?.data?.error || 'Error adding customer. Please try again.');
    });
}



function deleteCustomer(customerId) {
  axios.delete(`${apiUrl}/customers`, { data: { id: customerId } })
    .then(response => {
      alert(response.data.message);
      fetchCustomers();
    })
    .catch(error => console.error('Error deleting customer:', error));
}

let globalCustomerId

function updateCustomer(customerId) {
  console.log(customerId);
  

  axios.get(`${apiUrl}/customerToUpdate`, { params: { id: customerId } })
    .then(response => {
      console.log("Customer Data: ", response.data);

      const customer = response.data;


      if (customer) {
      
        document.getElementById('update-first-name').value = customer.firstName;
        document.getElementById('update-last-name').value = customer.lastName;
        document.getElementById('update-birthDate').value = customer.birthDate;
        document.getElementById('update-city').value = customer.city;
        document.getElementById('update-email').value = customer.email;
        document.getElementById('update-phone').value = customer.phoneNumber;
        document.getElementById('update-username').value = customer.username;
        document.getElementById('update-role').value = customer.role;


        const modal = document.getElementById('update-customer-modal');
        modal.style.display = 'block';
        globalCustomerId = customerId;

        const inputs = document.querySelectorAll('#update-customer-modal input, #update-customer-modal select');
        inputs.forEach(input => {
          input.addEventListener('input', () => {
            document.getElementById('save-customer-button').style.display = 'inline';
          });
        });
      } else {
        console.error("Customer data not found.");
      }
    })
    .catch(error => {
      console.error('Error fetching customer data:', error);
    });
}


function saveCustomerChanges() {
  const firstName = document.getElementById('update-first-name').value;
  const lastName = document.getElementById('update-last-name').value;
  const birthDate = document.getElementById('update-birthDate').value;
  const city = document.getElementById('update-city').value;
  const email = document.getElementById('update-email').value;
  const phone = document.getElementById('update-phone').value;
  const username = document.getElementById('update-username').value;
  const role = document.getElementById('update-role').value;

  const updatedData = {
    id: globalCustomerId,
    firstName: firstName,
    lastName: lastName,
    birthDate: birthDate,
    city: city,
    email: email,
    phoneNumber: phone,
    username: username,
    role: role
  };
  console.log(updatedData);
  
  axios.put(`${apiUrl}/customers`, updatedData)
    .then(response => {
      alert(response.data.message);
      closeUpdateModal();
      fetchCustomers();
    })
    .catch(error => console.error('Error updating customer:', error));
}


function closeUpdateModal() {
  document.getElementById('update-customer-modal').style.display = 'none';
  document.getElementById('save-customer-button').style.display = 'none';
}



function fetchLoans() {
  axios.get(`${apiUrl}/loans`)
    .then(response => {
      const loans = response.data;
      const loansTableBody = document.querySelector('#loans-table tbody');
      loansTableBody.innerHTML = '';

      
      loans.forEach(loan => {
        const row = document.createElement('tr');
        row.innerHTML = `
              <td>${loan.id}</td>
              <td>${loan.bookId}</td>
              <td>${loan.custId}</td>
              <td>${loan.loanDate}</td>
              <td>${loan.expected_returnDate}</td>
              <td>
                    <button class="return-button" onclick="returnBook(${loan.id})">
                      return
                    </button>
              </td>
            `;
        loansTableBody.appendChild(row);
      });
    })
    .catch(error => console.error('Error fetching loans data:', error));
}

function fetchLateLoans() {
  axios.get(`${apiUrl}/lateLoans`)
    .then(response => {
      const lateLoans = response.data;
      const lateLoansTableBody = document.querySelector('#late-loans-table tbody');
      lateLoansTableBody.innerHTML = '';

      lateLoans.forEach(loan => {
        const row = document.createElement('tr');
        row.innerHTML = `
              <td>${loan.id}</td>
              <td>${loan.customerId}</td>
              <td>${loan.bookId}</td>
              <td>${loan.loanDate}</td>
              <td>${loan.expected_returnDate}</td>
              <td>${loan.lateDays_num}</td>
              <td>
                <button class="return-button" onclick="returnBook(${loan.id})">
                  Return
                </button>
              </td>
            `;
        lateLoansTableBody.appendChild(row);
      });
    })
    .catch(error => console.error('Error fetching late loans data:', error));
}

function returnBook(loanId) {
  console.log('Returning book with loanId:', loanId);

  axios.delete(`${apiUrl}/loans`, { data: { id: loanId } })
    .then(response => {
      console.log('Book returned successfully:', response.data);
      alert('Book returned successfully');
      fetchLoans();
      fetchLateLoans();
    })
    .catch(error => {
      console.error('Error returning book:', error.response || error);
      alert('Error returning book. Please try again.');
    });
}

function register() {
  const formData = {
      firstName: document.getElementById("userFirstName").value,
      lastName: document.getElementById("userLastName").value,
      email: document.getElementById("userEmail").value,
      password: document.getElementById("userPassword").value,
      birthDate: document.getElementById("userBirthDate").value,
      city: document.getElementById("userCity").value,
      phoneNumber: document.getElementById("userPhoneNumber").value,
      username: document.getElementById("userUsername").value
  };


  for (const key in formData) {
      if (!formData[key]) {
          document.getElementById("error-message").innerText = "Please fill in all the fields.";
          return;
      }
  }

  const phoneRegex = /^[\d\s\-+()]{10,15}$/;
  if (!phoneRegex.test(formData.phoneNumber)) {
      document.getElementById("error-message").innerText = "Please enter a valid phone number.";
      return;
  }

  const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  if (!passwordRegex.test(formData.password)) {
      document.getElementById("error-message").innerText = "Password must be at least 8 characters long and contain one uppercase letter, one number, and one special character.";
      return;
  }

  document.getElementById("error-message").innerText = "";


  axios.post(`${apiUrl}/register`, formData, {
      headers: {
          'Content-Type': 'application/json',
      },
  })
  .then(response => {
      if (response.data.message) {
          document.getElementById("message").innerText = response.data.message;
      } else if (response.data.error) {
          document.getElementById("error-message").innerText = response.data.error;
      }
  })
  .catch(error => {
      document.getElementById("error-message").innerText = "An error occurred. Please try again later.";
      console.error('Error:', error);
  });
}




window.onload = function () {
  fetchBooks();
  fetchCustomers();
  fetchLoans();
  fetchLateLoans();
}