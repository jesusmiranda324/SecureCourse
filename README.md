# SecureCourse – Cybersecurity Final Project

## 1. Project Overview

SecureCourse is a web-based course portal built with Python Flask, SQLite, and Apache on Ubuntu Server.

The application supports three account types:

- **Faculty:** Upload course materials, assignments, and public files. View student submissions.
- **Students:** View course materials and assignments. Submit assignments.
- **Guests:** View public files only.

The purpose of this project is to demonstrate authentication, role-based access control, Linux file permissions, and basic web security.

---

## 2. Apache Setup and Configuration

SecureCourse is hosted on Ubuntu using Apache with the mod_wsgi module to run the Flask application.

### Software Used

- Ubuntu Server
- Apache2
- Python 3
- Python virtual environment
- Flask
- SQLite
- mod_wsgi

### Apache Installation

The following commands were used to install Apache and the required WSGI module:

```bash
sudo apt update
sudo apt install apache2 libapache2-mod-wsgi-py3
```

Apache was enabled and started using:

```bash
sudo systemctl enable apache2
sudo systemctl start apache2
```

### Apache Configuration

The application uses an Apache virtual host configuration located at:

```text
/etc/apache2/sites-available/securecourse.conf
```

The configuration connects Apache to the Flask application through the WSGI file:

```text
/home/lifes/SecureCourse/securecourse.wsgi
```

The WSGI module allows Apache to run the Python Flask application.

### Checking Apache

Apache status can be checked with:

```bash
sudo systemctl status apache2
```

The application was tested through a web browser to confirm that Apache successfully served the SecureCourse website.

---

## 3. Directory Structure

The main application directory is:

```text
/home/lifes/SecureCourse
```

The project uses the following structure:

```text
SecureCourse/
├── app.py
├── create_users.py
├── README.txt
├── requirements.txt
├── securecourse.wsgi
├── instance/
│   └── securecourse.db
├── materials/
├── assignments/
├── submissions/
├── public/
├── static/
│   └── style.css
└── templates/
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── resources.html
    ├── upload.html
    ├── submit.html
    └── submissions.html

```

### Directory Descriptions

| Directory/File | Purpose |
|---|---|
| `app.py` | Main Flask application |
| `create_users.py` | Creates application accounts |
| `requirements.txt` | Lists Python dependencies |
| `securecourse.wsgi` | Connects Flask to Apache |
| `instance/` | Stores the SQLite database |
| `materials/` | Stores course materials |
| `assignments/` | Stores assignments |
| `submissions/` | Stores student submissions |
| `public/` | Stores files available to guests |
| `static/` | Stores CSS and static resources |
| `templates/` | Stores HTML pages |

---

## 4. Linux Permissions and Groups

Linux permissions provide an additional layer of access control for application files and directories.

Two Linux groups were created:

- `faculty`
- `students`

The Apache service account, `www-data`, was added to both groups so the web application can access the required directories.

The groups can be checked using:

```bash
getent group faculty students
```

The project directories use restricted permissions. The materials, assignments, submissions, and public directories were configured to prevent unrestricted access by other local users.

Access Control Lists (ACLs) were also used to grant the Apache `www-data` account the required permissions.

ACL permissions can be inspected with:

```bash
getfacl ~/SecureCourse/materials
getfacl ~/SecureCourse/assignments
getfacl ~/SecureCourse/submissions
getfacl ~/SecureCourse/public
```

The SQLite database is stored in the `instance` directory. Its permissions were configured so Apache can read and write to the database without giving access to everyone.

The application also uses Flask role checks. Linux permissions protect files at the operating-system level, while Flask controls what each logged-in account can do through the website.

---

## 5. Security Features Implemented

The following security features were implemented:

### User Authentication
Users must log in with an account before accessing protected areas of the application.

### Password Hashing
Passwords are stored as password hashes rather than plain text.

### Role-Based Access Control
The application distinguishes between Faculty, Student, and Guest accounts. Each role has different permissions.

### Session Management
Flask sessions maintain the user's authenticated state while navigating the website.

### Secure Session Cookie Settings
The application uses:

- `SESSION_COOKIE_HTTPONLY = True`
- `SESSION_COOKIE_SAMESITE = "Lax"`

These settings help protect session cookies.

### Debug Mode Disabled
Flask debug mode is disabled in the application configuration.

### Linux File Permissions
Linux groups, directory permissions, and ACLs restrict access to application files and the SQLite database.

---

## 6. Testing

The following tests were performed:

- Faculty account login.
- Student account login.
- Guest account login.
- Faculty access to upload functionality.
- Student access to materials and assignments.
- Student assignment submissions.
- Guest access to public files.
- File upload and download functionality.
- Role-based access restrictions.

All three account types and the file upload/download functionality were tested successfully.

---

## 7. Conclusion

SecureCourse demonstrates how Apache, Flask, SQLite, authentication, role-based access control, and Linux file permissions can work together to create a course portal with different levels of access.

The project demonstrates basic web security and operating-system-level file protection.