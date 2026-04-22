import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkthemes
import pymysql
from openpyxl import Workbook
from openpyxl.styles import Font
import datetime
import logging
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
import os

# Email Configuration
SENDER_EMAIL = "adityananaware1234@gmail.com"
SENDER_PASSWORD = "kkwc etls qyif hlsb"

def send_email(to_email, subject, content):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(content, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logging.error(f"Email Error: {str(e)}")

# Logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Fee Mapping
STANDARD_FEES = {
    '1': 10000, '2': 12000, '3': 13000, '4': 14000, '5': 15000,
    '6': 16000, '7': 17000, '8': 18000, '9': 19000, '10': 20000
}

# Splash Screen
splash = tk.Tk()
splash.overrideredirect(True)
splash.geometry("400x300+500+250")
splash.configure(bg='white')
try:
    splash_logo = tk.PhotoImage(file="std2.png")
    tk.Label(splash, image=splash_logo, bg='white').pack(pady=20)
except:
    tk.Label(splash, text="Loading...", font=('Segoe UI', 20, 'bold'), bg='white', fg='steel blue').pack(pady=100)
tk.Label(splash, text="Student Management System", font=('Segoe UI', 14, 'bold'), bg='white', fg='dark green').pack(pady=10)
splash.update()
time.sleep(2)
splash.destroy()

def start_app():
    global root, con, connected, db_config

    root = ttkthemes.ThemedTk()
    try:
        root.set_theme('adapta')
    except:
        root.set_theme('clam')
    root.state('zoomed')
    root.title('Student Management System')

    try:
        bg_image = tk.PhotoImage(file="transparent_background.png")
        bg_label = tk.Label(root, image=bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        root.bind("<Configure>", lambda e: bg_label.place(x=0, y=0, relwidth=1, relheight=1))
    except:
        root.config(bg="white")

    topBar = tk.Frame(root, bg='white', bd=2, relief=tk.RIDGE)
    topBar.pack(fill=tk.X)
    datetimeLabel = tk.Label(topBar, font=('Segoe UI', 14, 'bold'), bg='white', fg='black')
    datetimeLabel.pack(side=tk.LEFT, padx=10)
    connectBtn = ttk.Button(topBar, text='Connect Database')
    connectBtn.pack(side=tk.RIGHT, padx=10)

    def clock():
        now = time.strftime("%d/%m/%y %H:%M:%S")
        datetimeLabel.config(text=now)
        datetimeLabel.after(1000, clock)
    clock()

    s = "Student Management System"
    count = 0
    text = ""
    sliderLabel = tk.Label(topBar, text="", font=('Segoe UI', 16, 'bold'), bg='white', fg='steel blue')
    sliderLabel.pack(side=tk.LEFT, padx=20)

    def slider():
        nonlocal count, text
        if count >= len(s):
            count = 0
            text = ""
        text += s[count]
        sliderLabel.config(text=text)
        count += 1
        sliderLabel.after(200, slider)
    slider()

    db_config = {'host': '', 'user': '', 'password': ''}
    connected = False
    con = None

    def connect_database():
        connect_window = tk.Toplevel()
        connect_window.title("Connect to Database")
        connect_window.geometry("400x250")
        connect_window.configure(bg='white')

        tk.Label(connect_window, text="Host: ", bg='white').pack(pady=5)
        host_entry = tk.Entry(connect_window)
        host_entry.insert(0, "localhost")
        host_entry.pack()

        tk.Label(connect_window, text="User: ", bg='white').pack(pady=5)
        user_entry = tk.Entry(connect_window)
        user_entry.insert(0, "root")
        user_entry.pack()

        tk.Label(connect_window, text="Password: ", bg='white').pack(pady=5)
        password_entry = tk.Entry(connect_window, show='*')
        password_entry.pack()

        def attempt_connect():
            global con, connected
            try:
                db_config['host'] = host_entry.get()
                db_config['user'] = user_entry.get()
                db_config['password'] = password_entry.get()
                con = pymysql.connect(
                    host=db_config['host'],
                    user=db_config['user'],
                    password=db_config['password']
                )
                cur = con.cursor()
                cur.execute("CREATE DATABASE IF NOT EXISTS studentmanagementsystem")
                cur.execute("USE studentmanagementsystem")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS student (
                        id VARCHAR(50) PRIMARY KEY,
                        roll_no INT AUTO_INCREMENT,
                        name VARCHAR(100),
                        mobile_no VARCHAR(20),
                        email VARCHAR(100),
                        address TEXT,
                        gender VARCHAR(10),
                        dob VARCHAR(20),
                        added_date VARCHAR(20),
                        added_time VARCHAR(20),
                        standard VARCHAR(10),
                        fee INT DEFAULT 0,
                        paid_fee INT DEFAULT 0,
                        UNIQUE KEY (roll_no)
                    )
                """)
                connected = True
                connect_window.destroy()
                messagebox.showinfo("Success", "Connected to Database and Table Ready")
                fetch_students()
            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", f"Database connection failed:\n{e}")
        ttk.Button(connect_window, text="Connect", command=attempt_connect).pack(pady=20)

    connectBtn.config(command=connect_database)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TButton",
                    font=('Segoe UI', 11, 'bold'),
                    padding=8,
                    background="#add8e6",
                    foreground="black",
                    relief="flat")
    style.map("TButton",
              background=[("active", "#87ceeb")],
              foreground=[("active", "black")])

    # Right Frame
    rightFrame = tk.Frame(root, bg='#fff8dc', bd=3, relief=tk.GROOVE)
    rightFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=(80, 10))
    scrollX = tk.Scrollbar(rightFrame, orient=tk.HORIZONTAL)
    scrollY = tk.Scrollbar(rightFrame, orient=tk.VERTICAL)
    studentTable = ttk.Treeview(
        rightFrame,
        columns=("ID", "Roll No", "Name", "Mobile", "Email", "Address", "Gender", "DOB", "Date", "Time", "Standard", "Fee", "Paid Fee"),
        xscrollcommand=scrollX.set,
        yscrollcommand=scrollY.set
    )
    scrollX.config(command=studentTable.xview)
    scrollY.config(command=studentTable.yview)
    scrollX.pack(side=tk.BOTTOM, fill=tk.X)
    scrollY.pack(side=tk.RIGHT, fill=tk.Y)
    studentTable.pack(fill=tk.BOTH, expand=1)
    for col in studentTable["columns"]:
        studentTable.heading(col, text=col)
        studentTable.column(col, width=100, anchor=tk.CENTER)
    studentTable.config(show='headings')

    # Left Frame
    leftFrame = tk.Frame(root, bg='#f0f8ff', bd=3, relief=tk.RIDGE)
    leftFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=(80, 10))
    try:
        logo = tk.PhotoImage(file="std2.png")
        tk.Label(leftFrame, image=logo, bg='#f0f8ff').pack(pady=10)
    except:
        tk.Label(leftFrame, text="LOGO", font=('Segoe UI', 20), bg='#f0f8ff').pack(pady=20)

    # ----------------- Functions like add_student, update_student, delete_student, etc. go here -----------------
    # ----------------- Student Functions -----------------

    def fetch_students():
        if not connected:
            messagebox.showerror("Error", "Connect to the database first")
            return
        try:
            cur = con.cursor()
            cur.execute("USE studentmanagementsystem")
            cur.execute("SELECT * FROM student")
            rows = cur.fetchall()
            studentTable.delete(*studentTable.get_children())
            for row in rows:
                studentTable.insert('', tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to fetch records:\n{e}")

    def add_student():
        if not connected:
            messagebox.showerror("Error", "Please connect to the database first.")
            return
        import_window = tk.Toplevel(root)
        import_window.title("Add Student")
        import_window.geometry("400x650")
        fields = ["Name", "Mobile", "Email", "Address", "Gender", "DOB", "Standard", "Paid Fee"]
        entries = {}
        for field in fields:
            tk.Label(import_window, text=field, font=('Segoe UI', 10)).pack(pady=5)
            if field == "Standard":
                entry = ttk.Combobox(import_window, values=[str(i) for i in range(1, 11)])
                entry.current(0)
            elif field == "Gender":
                entry = ttk.Combobox(import_window, values=["Male", "Female", "Other"])
                entry.current(0)
            else:
                entry = tk.Entry(import_window)
            entry.pack()
            entries[field] = entry

        def validate_inputs(data):
            if not data['Name'].replace(" ", "").isalpha():
                messagebox.showerror("Validation Error", "Name must contain only alphabets.", parent=import_window)
                return False
            if not data['Mobile'].isdigit() or len(data['Mobile']) != 10:
                messagebox.showerror("Validation Error", "Mobile number must be 10 digits.", parent=import_window)
                return False
            if "@" not in data['Email'] or "." not in data['Email']:
                messagebox.showerror("Validation Error", "Enter a valid email address.", parent=import_window)
                return False
            if not data['Address'].strip():
                messagebox.showerror("Validation Error", "Address cannot be empty.", parent=import_window)
                return False
            try:
                datetime.datetime.strptime(data['DOB'], "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Validation Error", "DOB must be in DD/MM/YYYY format.", parent=import_window)
                return False
            std = data['Standard']
            fee = STANDARD_FEES.get(std, 0)
            if not data['Paid Fee'].isdigit():
                messagebox.showerror("Validation Error", "Paid Fee must be a number.", parent=import_window)
                return False
            if int(data['Paid Fee']) > fee:
                messagebox.showerror("Validation Error", f"Paid Fee cannot exceed total fee (₹{fee}).", parent=import_window)
                return False
            return True

        def save():
            data = {k: v.get() for k, v in entries.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "All fields are required", parent=import_window)
                return
            if not validate_inputs(data):
                return
            try:
                sid = str(uuid.uuid4())[:8]
                date = datetime.date.today().strftime("%d/%m/%Y")
                time_ = datetime.datetime.now().strftime("%H:%M:%S")
                std = data['Standard']
                fee = STANDARD_FEES.get(std, 0)
                paid = int(data['Paid Fee'])
                due = fee - paid
                cur = con.cursor()
                cur.execute("USE studentmanagementsystem")
                cur.execute("""
                    INSERT INTO student 
                    (id, name, mobile_no, email, address, gender, dob, added_date, added_time, standard, fee, paid_fee)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    sid, data['Name'], data['Mobile'], data['Email'], data['Address'],
                    data['Gender'], data['DOB'], date, time_, std, fee, paid
                ))
                con.commit()

                content = f"""Hello {data['Name']},

You have been successfully added to the Student Management System.

Student ID: {sid}
Standard/Class: {std}
Total Fee: ₹{fee}
Paid Fee: ₹{paid}
Remaining Due: ₹{due}

Thank you.
"""
                send_email(data['Email'], "Student Admission Confirmed", content)
                messagebox.showinfo("Success", "Student added and email sent", parent=import_window)
                import_window.destroy()
                fetch_students()
            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", f"Failed to add student:\n{e}", parent=import_window)

        tk.Button(import_window, text="Save", command=save, bg="green", fg="white", font=('Segoe UI', 10, 'bold')).pack(pady=20)

    def update_student():
        selected = studentTable.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student to update")
            return
        values = studentTable.item(selected, 'values')
        top = tk.Toplevel(root)
        top.title("Update Student")
        top.geometry("400x650")
        fields = ["Name", "Mobile", "Email", "Address", "Gender", "DOB", "Standard", "Paid Fee"]
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(top, text=field, font=('Segoe UI', 10)).pack(pady=5)
            if field == "Standard":
                entry = ttk.Combobox(top, values=[str(i) for i in range(1, 11)])
                entry.set(values[10])
            else:
                entry = tk.Entry(top)
                entry.insert(0, values[i + 2])
            entry.pack()
            entries[field] = entry

        def update():
            data = {k: v.get() for k, v in entries.items()}
            if not all(data.values()):
                messagebox.showerror("Error", "All fields required", parent=top)
                return
            try:
                std = data['Standard']
                fee = STANDARD_FEES.get(std, 0)
                new_paid = int(data['Paid Fee'])
                old_values = {
                    "Name": values[2],
                    "Mobile": values[3],
                    "Email": values[4],
                    "Address": values[5],
                    "Gender": values[6],
                    "DOB": values[7],
                    "Standard": values[10],
                    "Paid Fee": values[12]
                }
                changed_fields = []
                for k in old_values:
                    if str(old_values[k]) != str(data[k]):
                        changed_fields.append(f"{k}: '{old_values[k]}' → '{data[k]}'")

                previous_paid = int(values[12])
                total_paid = previous_paid + new_paid
                due = fee - total_paid
                cur = con.cursor()
                cur.execute("USE studentmanagementsystem")
                cur.execute("""
                    UPDATE student SET name=%s, mobile_no=%s, email=%s, address=%s, gender=%s, dob=%s,
                    standard=%s, fee=%s, paid_fee=%s WHERE id=%s
                """, (
                    data['Name'], data['Mobile'], data['Email'], data['Address'],
                    data['Gender'], data['DOB'], std, fee, total_paid, values[0]
                ))
                con.commit()

                content = f"""Hello {data['Name']},

Your profile has been successfully updated.

Student ID: {values[0]}
Standard: {std}
Total Fee: ₹{fee}
Total Paid: ₹{total_paid}
Remaining Due: ₹{due}

The following details were updated:
{chr(10).join(changed_fields) if changed_fields else 'Only payment updated.'}

Thank you.
"""
                send_email(data['Email'], "Student Profile Updated", content)
                fetch_students()
                top.destroy()
            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", f"Update failed:\n{e}", parent=top)
        tk.Button(top, text="Update", command=update, bg="orange",fg="white", font=('Segoe UI', 10, 'bold')).pack(pady=20)



            # Now pack all labels, entries, and the Save button inside scrollable_frame

    def delete_student():
        selected = studentTable.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a student to delete")
            return
        values = studentTable.item(selected, 'values')
        confirm = messagebox.askyesno("Confirm", f"Delete student {values[2]}?")
        if confirm:
            try:
                cur = con.cursor()
                cur.execute("USE studentmanagementsystem")
                cur.execute("DELETE FROM student WHERE id=%s", (values[0],))
                con.commit()
                content = f"""Hello {values[2]},

Your student record (ID: {values[0]}) has been deleted from the system.

Thank you.
"""
                send_email(values[4], "Student Deleted", content)
                fetch_students()
            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", f"Deletion failed:\n{e}")

    def search_student():
        top = tk.Toplevel(root)
        top.title("Search Student")
        top.geometry("300x250")
        tk.Label(top, text="Search by ID or Name:", font=('Segoe UI', 10)).pack(pady=10)
        search_entry = tk.Entry(top)
        search_entry.pack(pady=5)

        def search():
            keyword = search_entry.get().strip()
            if not keyword:
                messagebox.showerror("Error", "Please enter Student ID or Name", parent=top)
                return
            try:
                cur = con.cursor()
                cur.execute("USE studentmanagementsystem")
                cur.execute("SELECT * FROM student WHERE id=%s OR name LIKE %s", (keyword, f"%{keyword}%"))
                rows = cur.fetchall()
                studentTable.delete(*studentTable.get_children())
                if rows:
                    for row in rows:
                        studentTable.insert('', tk.END, values=row)
                else:
                    messagebox.showinfo("Not Found", "No student found with this ID or Name", parent=top)
            except Exception as e:
                logging.error(str(e))
                messagebox.showerror("Error", f"Search failed:\n{e}", parent=top)

        tk.Button(top, text="Search", command=search, bg="blue", fg="white", font=('Segoe UI', 10, 'bold')).pack(pady=10)

    def export_data():
        if not connected:
            messagebox.showerror("Error", "Connect to database first")
            return
        file = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not file:
            return
        try:
            wb = Workbook()
            ws = wb.active
            ws.append(["ID", "Roll No", "Name", "Mobile", "Email", "Address", "Gender", "DOB", "Date", "Time", "Standard", "Fee", "Paid Fee"])
            for row in studentTable.get_children():
                ws.append(studentTable.item(row)['values'])
            for cell in ws[1]:
                cell.font = Font(bold=True)
            wb.save(file)
            messagebox.showinfo("Exported", f"Data exported to {file}")
        except Exception as e:
            logging.error(str(e))
            messagebox.showerror("Error", f"Export failed:\n{e}")

    # ----------------- Left Frame Buttons -----------------
    ttk.Button(leftFrame, text="Add Student", command=add_student).pack(pady=10)
    ttk.Button(leftFrame, text="Search Student", command=search_student).pack(pady=10)
    ttk.Button(leftFrame, text="Delete Student", command=delete_student).pack(pady=10)
    ttk.Button(leftFrame, text="Update Student", command=update_student).pack(pady=10)
    ttk.Button(leftFrame, text="Show Students", command=fetch_students).pack(pady=10)
    ttk.Button(leftFrame, text="Export Data", command=export_data).pack(pady=10)
    ttk.Button(leftFrame, text="Exit", command=root.destroy).pack(pady=10)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.mainloop()

# ----------------- Login Page -----------------
def login_page():
    login_win = tk.Tk()
    login_win.geometry("400x300+500+250")
    login_win.title("Login")
    login_win.resizable(False, False)
    login_win.configure(bg='white')

    tk.Label(login_win, text="Username:", font=('Segoe UI', 12), bg='white').pack(pady=10)
    user_entry = tk.Entry(login_win, font=('Segoe UI', 12), bd=2, relief=tk.SOLID)
    user_entry.pack()

    tk.Label(login_win, text="Password:", font=('Segoe UI', 12), bg='white').pack(pady=10)
    pass_entry = tk.Entry(login_win, show="*", font=('Segoe UI', 12), bd=2, relief=tk.SOLID)
    pass_entry.pack()

    def validate():
        if user_entry.get() == "admin" and pass_entry.get() == "Aditya220429":
            login_win.destroy()
            start_app()
        else:
            messagebox.showerror("Login Failed", "Invalid Credentials")

    tk.Button(login_win, text="Login", command=validate, bg='steel blue', fg='white',
              font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, padx=10, pady=5).pack(pady=20)
    login_win.mainloop()

# Start the app
login_page()
