PRINTER PAGE COUNTER
========================
Used By Computer Department Of Yashwantrao Chavan Institute Of Polytechnic ,Beed - Maharashtrac -431122

PROJECT DESCRIPTION:
----------------------------------------------------------------------------------------------------------
A Windows-based printer page counter and logging system with a graphical user 
interface built using Python and PyQt5, integrated with a Microsoft SQL Server 
database for logging print activities. It allows you to track printer usage, 
log page counts, manage print records, and export reports.
------------------------------------------------------------------------------------------------------------
FEATURES:
- Track print jobs with:
 - Printer name
 - Document name
 - Number of pages printed
 - Username
 - Date and time of printing
- Admin login system (optional)
- Export logs to:
 - PDF
 - Excel (.xlsx)
 - CSV
- Clean, user-friendly GUI with PyQt5
- Windows printer interaction using pywin32
- SQL Server database integration via pyodbc
- Dark and light mode support (optional)
--------------------------------------------------------------------------------------------------------------
SYSTEM REQUIREMENTS:
- Operating System: Windows 10/11 (64-bit)
- Python: 3.9+
- Microsoft SQL Server: 2019 or newer
- Microsoft SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 18 for SQL Server
------------------------------------------------------------------------------------------------------------
PYTHON DEPENDENCIES:
--------------------------------------------------------------------------------------------------------------
Install all required packages using:
 pip install -r requirements.txt
requirements.txt content:
 PyQt5==5.15.10
 pyodbc==5.1.0
 SQLAlchemy==2.0.30
 pywin32==306
 pandas==2.2.2
 openpyxl==3.1.2
 fpdf==1.7.2
 reportlab==4.1.0
 python-docx==1.1.0
 Pillow==10.3.0
 PyYAML==6.0.1
 python-dateutil==2.9.0.post0
 bcrypt==4.1.3
 tabulate==0.9.0
 tqdm==4.66.2
--------------------------------------------------------------------------------
Database Name: PrinterLogs
Tables:
1) PrintLogs Table:
 LogID INT Primary Key, Identity (Auto Increment)
 PrinterName NVARCHAR(255) NOT NULL
 DocumentName NVARCHAR(255) NOT NULL
 PagesPrinted INT NOT NULL
 Username NVARCHAR(255) NOT NULL
 PrintDateTime DATETIME DEFAULT GETDATE()
2) AdminUsers Table (optional):
 UserID INT Primary Key, Identity
 Username NVARCHAR(100) UNIQUE, NOT NULL
 PasswordHash NVARCHAR(255) NOT NULL
===================================================================== 
SQL SERVER DATABASE REQUIREMENTS & SETUP
=====================================================================
📦 SOFTWARE REQUIRED:
---------------------------------------------------------------------------------------------------------------------
- Microsoft SQL Server 2019+ (Developer or Express Edition)
- SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 18 for SQL Server
=====================================================================
INSTALL MICROSOFT SQL SERVER 2019 (DEVELOPER OR EXPRESS)
---------------------------------------------------------------------------------------------------------------------
Download:
https://www.microsoft.com/en-us/sql-server/sql-server-downloads
Installation Steps:
1. Run the SQL Server installer.
2. Choose "Basic" or "Custom" installation type.
3. Accept the license terms.
4. Choose installation location.
5. Proceed with installation until successful.
=====================================================================
CONFIGURE AUTHENTICATION MODE (MIXED MODE)
--------------------------------------------------------------------------------------------------------------------
During SQL Server setup (or afterwards via SSMS):
- When prompted for Authentication Mode:
 * Select "Mixed Mode (SQL Server and Windows Authentication)".
 * Set a strong password for the 'sa' (System Administrator) account.
Example:
- Username: sa
- Password: YourStrongPassword
If SQL Server is already installed:
- Open SQL Server Management Studio (SSMS)
- Right-click server in Object Explorer → Properties
- Go to "Security" tab
- Choose "SQL Server and Windows Authentication mode"
- Click OK
- Restart SQL Server service using SQL Server Configuration Manager
INSTALL SQL SERVER MANAGEMENT STUDIO (SSMS)
---------------------------------------------------------------------------------------------------------------------
Download:
https://aka.ms/ssmsfullsetup
Installation Steps:
1. Run the installer.
2. Follow the on-screen instructions.
3. Launch SQL Server Management Studio after installation.
=====================================================================
INSTALL MICROSOFT ODBC DRIVER 18 FOR SQL SERVER
--------------------------------------------------------------------------------------------------------------------
Download:
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
Installation Steps:
1. Download the installer for your system.
2. Run the installer.
3. Accept license agreement.
4. Complete installation.
CREATE DATABASE AND TABLES
---------------------------------------------------------------------------------------------------------------------
Using SQL Server Management Studio (SSMS):
Connect to Server:
- Server name: localhost\SQLEXPRESS (or your custom instance)
- Authentication: SQL Server Authentication
- Login: sa
- Password: YourStrongPassword
Create Database:
1. In Object Explorer → Right-click "Databases"
2. Select "New Database"
3. Name: PrinterLogs
4. Click OK
Create Tables:
Open a New Query window and run:
-- PrintLogs Table
CREATE TABLE PrintLogs (
 LogID INT IDENTITY(1,1) PRIMARY KEY,
 PrinterName NVARCHAR(255) NOT NULL,
 DocumentName NVARCHAR(255) NOT NULL,
 PagesPrinted INT NOT NULL,
 Username NVARCHAR(255) NOT NULL,
 PrintDateTime DATETIME DEFAULT GETDATE()
);
-- AdminUsers Table (Optional)
CREATE TABLE AdminUsers (
 UserID INT IDENTITY(1,1) PRIMARY KEY,
 Username NVARCHAR(100) UNIQUE NOT NULL,
 PasswordHash NVARCHAR(255) NOT NULL
);
Execute the script (F5 or Execute button).
=====================================================================
TEST ODBC CONNECTION (OPTIONAL)
--------------------------------------------------------------------------------------------------------------------
1. Open "ODBC Data Sources (64-bit)" from Start menu.
2. Go to "System DSN" tab → Click "Add…"
3. Select "ODBC Driver 18 for SQL Server" → Click "Finish"
4. Name the data source (e.g. PrinterLogsDSN)
5. Enter server: localhost\SQLEXPRESS
6. Choose "SQL Server Authentication"
7. Enter:
 - Login ID: sa
 - Password: YourStrongPassword
8. Test the connection.
=====================================================================
✅ SETUP COMPLETE!
You can now connect your Printer Page Counter application to the database
-------------------------------------------------------------------------------------------------------------------
DATABASE CONNECTION STRING (Example for ODBC Driver 18):
DRIVER={ODBC Driver 18 for SQL Server};
SERVER=localhost\SQLEXPRESS;
DATABASE=PrinterLogs;
UID=sa;
PWD=YourStrongPassword;
Encrypt=yes;
TrustServerCertificate=yes;
-------------------------------------------------------------------------------------------------------------------
USAGE:
-------------------------------------------------------------------------------------------------------------------
1. Clone or download this repository.
2. Install dependencies via pip install -r requirements.txt
3. Configure the config.json file with your database connection details.
4. Run the main Python application:
 python printer_page_counter.py
5. Log print activity, export reports, and manage your printer logs via the GUI.
--------------------------------------------------------------------------------
SUPPORT:
---------------------------------------------------------------------------------------------------------------------
For any issues or feature requests, please contact:
Developer: Nisargandh Aditya Mahendra ( 2211580197 )
Email: your : adityanisargandh01@gmail.com
---------------------------------------------------------------------------------------------------------------------
-
LICENSE:
--------
This project is licensed under the MIT License.
==========================================================


Screenshot


![Screenshot](https://github.com/user-attachments/assets/8e78e30a-81b6-45ff-a190-a5f2e16f3470)
![Screenshot 2](https://github.com/user-attachments/assets/14f7fd6c-bae8-4ffa-a7c6-1450c9ffe9b3)
![Screenshot 3](https://github.com/user-attachments/assets/43ddd4c4-4bbd-46c2-b06f-412dee9be569)
![Screenshot 4](https://github.com/user-attachments/assets/ea257f5a-ef22-464c-9b8e-06f58ec3f6d9)
![Screenshot 5](https://github.com/user-attachments/assets/c6c6bc5e-a7bf-49ee-883c-dfa644d059da)
![Screenshot 6](https://github.com/user-attachments/assets/d3612855-4d23-4bce-8505-bb678233dcdc)




