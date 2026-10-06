PaperGuard
Secure Exam Paper Access & Leakage Prevention System
PaperGuard is a cybersecurity-based web application designed to protect examination papers from unauthorized access and potential leakage.
It uses authentication, role-based access control, paper encryption, faculty-specific authorization, access logging, and suspicious activity detection to provide a secure environment for managing exam papers.
Problem Statement
Exam papers are sensitive documents. If they are stored or shared without proper security controls, unauthorized users may gain access to them, leading to exam paper leakage.
Traditional file storage systems generally do not provide sufficient control over:
- Who can access an exam paper
- Which faculty member is authorized to access a specific paper
- Whether unauthorized access attempts are occurring
- How exam paper access is tracked
- How sensitive papers are protected when stored
PaperGuard addresses these problems through a centralized and security-focused exam paper management system.
Objective
The main objective of PaperGuard is to provide a secure system for:
- Managing examination papers
- Encrypting sensitive exam documents
- Controlling access based on user roles
- Assigning papers to specific faculty members
- Preventing unauthorized access
- Recording access attempts
- Detecting suspicious access behavior
Key Features
1. Authentication
PaperGuard provides secure login for administrators and faculty members.
Passwords are stored as hashed values rather than plain text.
2. Role-Based Access Control
The system supports two main roles:
- Admin
- Faculty
Admins can manage faculty accounts and exam papers, while faculty members can access only the papers assigned to them.
3. Secure Exam Paper Upload
Administrators can upload examination papers through the system.
Uploaded papers are encrypted before being stored.
4. Paper Encryption
Exam papers are encrypted using the Fernet symmetric encryption mechanism provided by the Python cryptography library.
The original unencrypted file is removed after encryption.
5. Faculty-Specific Authorization
Each exam paper can be assigned to a specific faculty member.
For example:
DBMS Exam → Faculty 1
OS Exam   → Faculty 2

Faculty 1 cannot access the OS examination paper.
6. Unauthorized Access Prevention
If a faculty member attempts to access a paper that has not been assigned to them, PaperGuard denies the request.
The attempt is also recorded in the security logs.
7. Access Logging
PaperGuard records important security events such as:
- Authorized paper access
- Unauthorized access attempts
- Username
- Paper ID
- IP address
- Timestamp
8. Suspicious Activity Detection
Repeated unauthorized access attempts are analyzed.
If a user makes 3 or more unauthorized access attempts, the system identifies the user as suspicious.
9. Admin Security Dashboard
Administrators can view security statistics including:
- Total papers
- Total faculty
- Authorized accesses
- Unauthorized attempts
- Suspicious users
- Recent security logs
Security Mechanisms
PaperGuard implements multiple cybersecurity concepts:
Security Mechanism	Purpose
Password Hashing	Protect user passwords
Authentication	Verify user identity
Authorization	Control access to papers
Role-Based Access Control	Separate Admin and Faculty privileges
File Encryption	Protect exam papers at rest
Secure Decryption	Decrypt papers only when authorized
Access Logging	Track security events
Suspicious Activity Detection	Identify repeated unauthorized attempts
IP Logging	Record the source of access attempts


System Workflow
                    PaperGuard
                        |
                  User Login
                        |
              Authentication Check
                        |
             +----------+----------+
             |                     |
           Admin                 Faculty
             |                     |
      Manage Faculty          View Assigned
      Upload Papers              Papers
             |                     |
             ↓                     ↓
      Encrypt Exam Paper     Authorization Check
             |                     |
             ↓              +------+------+
      Encrypted Storage     |             |
                            ↓             ↓
                         Allowed       Denied
                            |             |
                            ↓             ↓
                     Decrypt in       Log Attempt
                       Memory             |
                            |              ↓
                            ↓        Suspicious Activity
                       View Paper
                            |
                            ↓
                       Log Access

Technology Stack
Backend
- Python
- Flask
Database
- SQLite
Security
- Cryptography
- Fernet Encryption
- Password Hashing
- Role-Based Access Control
Frontend
- HTML
- CSS
- Jinja2 Templates
Development Tools
- Visual Studio Code
- Git
- GitHub
Project Structure
PaperGuard/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── security.py
│   └── utils.py
│
├── database/
│
├── encrypted_papers/
│
├── logs/
│
├── static/
│   ├── css/
│   └── js/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   └── add_faculty.html
│
├── tests/
│
├── uploads/
│
├── .gitignore
├── requirements.txt
├── run.py
└── README.md

Installation & Setup
1. Clone the repository
git clone https://github.com/YOUR_USERNAME/PaperGuard.git

Move into the project:
cd PaperGuard

2. Create a virtual environment
python3 -m venv .venv

Activate it on macOS/Linux:
source .venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Run the application
python3 run.py

Open:
http://127.0.0.1:5000

Default Login
Admin
Username: admin
Password: ASk_me if you need to assess

Faculty
Username: faculty
Password: ask_mee

These credentials are intended for local development/testing. They should be changed or removed before production deployment.

Testing
PaperGuard was tested for the following scenarios:
Authentication Testing
- Valid admin login
- Valid faculty login
- Invalid username/password
Authorization Testing
- Faculty accessing assigned paper
- Faculty attempting to access another faculty's paper
- Admin accessing papers
Encryption Testing
- Uploaded PDF is encrypted before storage
- Original unencrypted PDF is removed
- Authorized users can view the decrypted paper
Security Logging Testing
- Authorized paper access is logged
- Unauthorized access attempts are logged
- IP address and timestamp are recorded
Suspicious Activity Testing
Repeated unauthorized attempts are detected.
Example:
Faculty 2
Unauthorized attempts: 3
Status: SUSPICIOUS

Example Security Scenario
Suppose an administrator uploads:
DBMS_Internal_Exam.pdf

and assigns it to:
Faculty 1

Faculty 1:
Login
  ↓
Authorization Check
  ↓
Access Granted
  ↓
Encrypted Paper Decrypted
  ↓
Paper Displayed
  ↓
Access Logged

If Faculty 2 attempts to access the same paper:
Login
  ↓
Authorization Check
  ↓
Access Denied
  ↓
Unauthorized Attempt Logged

After repeated unauthorized attempts:
Suspicious Activity Detected


Future Scope
Possible future improvements include:
- Multi-factor authentication
- Email/security alerts
- More advanced anomaly detection
- Stronger document watermarking
- Cloud-based secure storage
- Centralized security monitoring
- More detailed audit reports
These features are outside the current scope of the mini-project.
Disclaimer
PaperGuard is an educational cybersecurity project developed to demonstrate secure document management, authentication, authorization, encryption, and security monitoring concepts.
It is not intended to replace a production-grade examination security infrastructure.
Author
Yateesh Majjara
B.Tech — Computer Science & Engineering (AI & ML)