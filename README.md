Installation
1. Clone the repository:
   ```
   git clone [https://github.com/Elapatha2002/ADBMS_Group_AT.git]

2. Modify the database connection attributes in app.py:
   ```
   import pyodbc

    DRIVER='your_driver'(ODBC Driver 17 for SQL Server);
    Database connection attributes
    server = 'your_server_name'
    database = 'your_database_name'
    Trusted_Connection=yes;

3. Install necessary dependencies:
   ```
   pip install -r requirements.txt

4. To start the application, simply run:
   ```
   python app.py
