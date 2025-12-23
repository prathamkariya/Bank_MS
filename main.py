import tkinter as tk
from tkinter import messagebox
import mysql.connector
from PIL import Image, ImageTk
import bcrypt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Securely fetch database credentials
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'bank_management')

# Dynamic Path for Logo (Works on any computer)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

# Employee credentials (Username moved to .env for security)
employee_id = {
    "username": os.getenv('EMP_USERNAME', 'emp_007'),
    "password": bcrypt.hashpw(b"007", bcrypt.gensalt())
}

# Database Connection
def create_connection():
    """Establish a connection to the MySQL database using env variables."""
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Connection failed: {e}")
        return None

# Employee Login 
def employee_login(username, password):
    """Handle employee login."""
    if username == employee_id["username"] and bcrypt.checkpw(password.encode('utf-8'), employee_id["password"]):
        messagebox.showinfo("Login Successful", f"Welcome to DT Bank, {username}!")
        return True
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password.")
        return False

# --- Customer Account Management Functions ---

def create_customer(account_number, name, dob, phone, email, aadhar_number, address, account_type, initial_balance):
    try:
        initial_balance = float(initial_balance)
        if initial_balance < 0:
            raise ValueError("Initial balance must be non-negative.")
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
        return

    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = """INSERT INTO customers (account_number, name, date_of_birth, phone_number, email, aadhar_number, address, account_type, balance)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (account_number, name, dob, phone, email, aadhar_number, address, account_type, initial_balance))
            connection.commit()
            messagebox.showinfo("Success", "Customer created successfully!")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error: {err}")
        finally:
            cursor.close()
            connection.close()

def view_customer(account_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM customers WHERE account_number = %s"
        cursor.execute(query, (account_number,))
        customer = cursor.fetchone()
        if customer:
            details = (f"Account Number: {customer[0]}\nName: {customer[1]}\nDOB: {customer[2]}\n"
                       f"Phone: {customer[3]}\nEmail: {customer[4]}\nAadhar: {customer[5]}\n"
                       f"Address: {customer[6]}\nAccount Type: {customer[7]}\nBalance: ₹{customer[8]:,.2f}")
            messagebox.showinfo("Customer Details", details)
        else:
            messagebox.showerror("Error", "Customer not found.")
        cursor.close()
        connection.close()

def update_customer(account_number, field, new_value):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        allowed_fields = ['name', 'phone_number', 'email', 'aadhar_number', 'address', 'account_type']
        if field not in allowed_fields:
            messagebox.showerror("Error", "Invalid field.")
            return
        query = f"UPDATE customers SET {field} = %s WHERE account_number = %s"
        cursor.execute(query, (new_value, account_number))
        connection.commit()
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", f"Updated {field} successfully!")
        else:
            messagebox.showerror("Error", "Update failed.")
        cursor.close()
        connection.close()

def delete_customer(account_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "DELETE FROM customers WHERE account_number = %s"
        cursor.execute(query, (account_number,))
        connection.commit()
        if cursor.rowcount > 0:
            messagebox.showinfo("Success", "Customer deleted.")
        else:
            messagebox.showerror("Error", "Not found.")
        cursor.close()
        connection.close()

def perform_transaction(account_number, amount, transaction_type):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            amount = float(amount)
            if amount <= 0: raise ValueError
            if transaction_type == 'Deposit':
                query = "UPDATE customers SET balance = balance + %s WHERE account_number = %s"
                cursor.execute(query, (amount, account_number))
            else:
                cursor.execute("SELECT balance FROM customers WHERE account_number = %s", (account_number,))
                res = cursor.fetchone()
                if res and res[0] >= amount:
                    query = "UPDATE customers SET balance = balance - %s WHERE account_number = %s"
                    cursor.execute(query, (amount, account_number))
                else:
                    messagebox.showerror("Error", "Insufficient funds or account missing.")
                    return
            connection.commit()
            messagebox.showinfo("Success", f"{transaction_type} complete.")
        except:
            messagebox.showerror("Error", "Invalid amount.")
        finally:
            cursor.close()
            connection.close()

def check_balance(account_number):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name, balance FROM customers WHERE account_number = %s", (account_number,))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Balance", f"Holder: {result[0]}\nBalance: ₹{result[1]:,.2f}")
        else:
            messagebox.showerror("Error", "Account not found.")
        cursor.close()
        connection.close()

# --- GUI Window Functions ---

def create_customer_account():
    create_window = tk.Toplevel()
    create_window.title("Create Account")
    create_window.geometry("500x700")
    create_window.configure(bg="#E0F2F1")
    tk.Label(create_window, text="Create Customer Account", font=("Arial", 16, "bold"), bg="#E0F2F1").pack(pady=10)
    labels = ["Account Number", "Name", "DOB (YYYY-MM-DD)", "Phone", "Email", "Aadhar", "Address", "Type", "Initial Balance"]
    entries = []
    for lbl in labels:
        tk.Label(create_window, text=lbl, bg="#E0F2F1").pack()
        e = tk.Entry(create_window)
        e.pack(pady=2, padx=20, fill=tk.X)
        entries.append(e)
    tk.Button(create_window, text="Submit", bg="#87CEFA", command=lambda: create_customer(*(e.get() for e in entries))).pack(pady=20)

def view_customer_details():
    win = tk.Toplevel()
    win.title("View Details")
    win.geometry("400x250")
    win.configure(bg="#E0F2F1")
    tk.Label(win, text="Account Number:", bg="#E0F2F1").pack(pady=10)
    acc = tk.Entry(win)
    acc.pack(pady=5)
    tk.Button(win, text="View", command=lambda: view_customer(acc.get())).pack(pady=10)

def update_customer_details():
    win = tk.Toplevel()
    win.title("Update Details")
    win.geometry("400x350")
    win.configure(bg="#E0F2F1")
    tk.Label(win, text="Account Number:", bg="#E0F2F1").pack()
    acc = tk.Entry(win); acc.pack()
    tk.Label(win, text="Field (name, phone_number, etc.):", bg="#E0F2F1").pack()
    fld = tk.Entry(win); fld.pack()
    tk.Label(win, text="New Value:", bg="#E0F2F1").pack()
    val = tk.Entry(win); val.pack()
    tk.Button(win, text="Update", command=lambda: update_customer(acc.get(), fld.get(), val.get())).pack(pady=20)

def perform_transaction_window():
    win = tk.Toplevel(); win.title("Transaction"); win.geometry("400x400"); win.configure(bg="#E0F2F1")
    tk.Label(win, text="Account Number:", bg="#E0F2F1").pack()
    acc = tk.Entry(win); acc.pack()
    tk.Label(win, text="Amount:", bg="#E0F2F1").pack()
    amt = tk.Entry(win); amt.pack()
    t_type = tk.StringVar(value='Deposit')
    tk.Radiobutton(win, text="Deposit", variable=t_type, value='Deposit', bg="#E0F2F1").pack()
    tk.Radiobutton(win, text="Withdrawal", variable=t_type, value='Withdrawal', bg="#E0F2F1").pack()
    tk.Button(win, text="Submit", command=lambda: perform_transaction(acc.get(), amt.get(), t_type.get())).pack(pady=20)

def check_balance_window():
    win = tk.Toplevel(); win.title("Balance"); win.geometry("400x250"); win.configure(bg="#E0F2F1")
    tk.Label(win, text="Account Number:", bg="#E0F2F1").pack()
    acc = tk.Entry(win); acc.pack()
    tk.Button(win, text="Check", command=lambda: check_balance(acc.get())).pack(pady=20)

def delete_customer_account():
    win = tk.Toplevel(); win.title("Delete"); win.geometry("400x250"); win.configure(bg="#E0F2F1")
    tk.Label(win, text="Account Number:", bg="#E0F2F1").pack()
    acc = tk.Entry(win); acc.pack()
    tk.Button(win, text="Delete", bg="#F44336", command=lambda: delete_customer(acc.get())).pack(pady=20)

# --- Main Menu & Login ---

def show_menu():
    menu_window = tk.Tk()
    menu_window.title("DT Bank - Management Menu")
    menu_window.geometry("850x650")
    menu_window.configure(bg="#FFFFFF")

    # Header with Logo
    header_frame = tk.Frame(menu_window, bg="#00796B", pady=10)
    header_frame.pack(fill=tk.X)

    try:
        img = Image.open(LOGO_PATH)
        img = img.resize((200, 100), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(img)
        logo_label = tk.Label(header_frame, image=logo, bg="#00796B")
        logo_label.image = logo # Keep reference
        logo_label.pack()
    except Exception as e:
        tk.Label(header_frame, text="DT BANK", font=("Arial", 24, "bold"), fg="white", bg="#00796B").pack()

    menu_frame = tk.Frame(menu_window, bg="#E0F2F1", padx=20, pady=20)
    menu_frame.pack(expand=True, fill=tk.BOTH)

    options = {
        "Create New Account": create_customer_account,
        "View Account Details": view_customer_details,
        "Update Account Details": update_customer_details,
        "Perform Transaction": perform_transaction_window,
        "Check Account Balance": check_balance_window,
        "Delete Account": delete_customer_account,
        "Exit": menu_window.destroy
    }

    for text, cmd in options.items():
        tk.Button(menu_frame, text=text, font=("Arial", 12), width=30, pady=5, command=cmd).pack(pady=5)

    menu_window.mainloop()

def handle_login(u_entry, p_entry, win):
    if employee_login(u_entry.get(), p_entry.get()):
        win.destroy()
        show_menu()

def create_login_window():
    login_window = tk.Tk()
    login_window.title("Employee Login - DT Bank")
    login_window.geometry("600x500")
    login_window.configure(bg="#FFFFFF")

    header = tk.Frame(login_window, bg="#00796B", pady=10)
    header.pack(fill=tk.X)

    try:
        img = Image.open(LOGO_PATH)
        img = img.resize((150, 75), Image.Resampling.LANCZOS)
        logo = ImageTk.PhotoImage(img)
        lbl = tk.Label(header, image=logo, bg="#00796B")
        lbl.image = logo
        lbl.pack()
    except:
        tk.Label(header, text="DT BANK", font=("Arial", 20, "bold"), fg="white", bg="#00796B").pack()

    body = tk.Frame(login_window, bg="#E0F2F1", pady=30)
    body.pack(expand=True, fill=tk.BOTH)

    tk.Label(body, text="Username:", bg="#E0F2F1").pack()
    u_ent = tk.Entry(body); u_ent.pack(pady=5)
    tk.Label(body, text="Password:", bg="#E0F2F1").pack()
    p_ent = tk.Entry(body, show="*"); p_ent.pack(pady=5)

    tk.Button(body, text="Login", bg="#00796B", fg="white", width=15, 
              command=lambda: handle_login(u_ent, p_ent, login_window)).pack(pady=20)

    login_window.mainloop()

if __name__ == "__main__":
    create_login_window()