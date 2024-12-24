import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random
import string
from tkinter import simpledialog



#left click can select row, right click remove the selected row


#write the name of your database
db = 'try.db'

# Font style definition for consistent UI
font_style = ('Arial', 16)

# Database setup
def setup_database():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT
        )
    """)
    connection.commit()
    connection.close()

# Add expense to database
def add_expense():
    date = date_entry.get()
    category = category_combobox.get()
    amount = amount_entry.get().replace(',', '')  # Remove commas for storage
    description = description_entry.get()
    characters = string.ascii_letters + string.digits + "@!#"
    key = ''.join(random.choice(characters) for _ in range(25))
    
    if not (date and category and amount):
        messagebox.showerror("Error", "Please fill out all required fields (Date, Category, Amount).")
        return

    try:
        amount = float(amount)
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")
        return

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO expenses (key, date, category, amount, description) VALUES (?, ?, ?, ?, ?)",
                   (key, date, category, amount, description))
    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "Expense added successfully!")
    load_expenses()
    clear_inputs()

# Load expenses from database
def load_expenses():
    # Clear the table
    for row in table.get_children():
        table.delete(row)

    # Connect to the database
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT id, key, date, category, amount, description FROM expenses")
    rows = cursor.fetchall()
    connection.close()

    total_amount = 0  # To keep track of the total amount

    for row in rows:
        formatted_amount = f"{row[4]:,}"  # Format the amount with commas

        # Insert row data into the table, including the hidden key column
        table.insert("", tk.END, values=(row[2], row[3], formatted_amount, row[5], row[1]), tags=('row',))  # Include the key in values

        total_amount += row[4]  # Add amount to total amount

    formatted_total = f"{total_amount:,.2f}"  # Format the total amount with commas

    # Apply the font style to the rows with the 'row' tag
    table.tag_configure('row', font=font_style)

    total_label.config(text=f"₪{formatted_total} :סך הכל")

# Delete expense from the database using the key
def delete_expense():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No expense selected.")
        return

    # Retrieve the key from the hidden column
    database_key = table.item(selected_item[0])["values"][4]

    # Connect to the database
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM expenses WHERE key=?", (database_key,))
    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "Expense deleted successfully!")
    load_expenses()



# Function to edit the description of a selected expense
def edit_description():
    selected_item = table.selection()
    if not selected_item:
        messagebox.showerror("Error", "No expense selected.")
        return

    # Retrieve the key and current description from the selected row
    database_key = table.item(selected_item[0])["values"][4]
    current_description = table.item(selected_item[0])["values"][3]
    # Prompt the user for a new description
    new_description = tk.simpledialog.askstring("ערוך תיאור", ":ערוך את התיאור", initialvalue=current_description)

    if new_description is None or new_description.strip() == "":
        messagebox.showerror("Error", "Description cannot be empty.")
        return

    # Update the database
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("UPDATE expenses SET description=? WHERE key=?", (new_description, database_key))
    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "Description updated successfully!")
    load_expenses()  # Reload the table to show the updated description



# Handle row selection
def on_row_select(event):
    selected_item = table.selection()
    if selected_item:
        # Display the delete button below the table
        delete_button.pack(pady=5)
        edit_button.pack(pady=5)
# Deselect row on right-click
def on_right_click(event):
    table.selection_remove(table.selection())  # Remove all current selections
    delete_button.pack_forget()  # Hide the delete button if no row is selected
    edit_button.pack_forget()

# Clear input fields
def clear_inputs():
    category_combobox.set("")
    amount_entry.delete(0, tk.END)
    description_entry.delete(0, tk.END)

# Delete all expenses
def delete_all_expenses():
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM expenses")
    connection.commit()
    connection.close()

    messagebox.showinfo("Success", "הכל נמחק בהצלחה")
    load_expenses()

def calculate_category_total(category):
    if not category:
        messagebox.showerror("Error", "בבקשה בחר קטגוריה")
        return

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("SELECT amount FROM expenses WHERE category=?", (category,))
    rows = cursor.fetchall()
    connection.close()

    total_amount = 0
    for row in rows:
        total_amount += row[0]
    
    formatted_total = f"{total_amount:,.2f}"
    messagebox.showinfo("Total Expense", f"The total expense for {category} is: ₪{formatted_total}")

# Main window setup
root = tk.Tk()
root.title("חתונה 17.12.25")
root.geometry("1000x700")  # Increased window size
root.configure(bg="#f4f4f4")

# Input Fields
today_date = datetime.today().strftime('%Y-%m-%d')

headline_label = tk.Label(root, text="Wedding", font=('Arial', 22, "bold"), fg="#333333", bg="#f4f4f4")
headline_label.pack(pady=12)

# Date Label and Entry
tk.Label(root, text=":תאריך", bg="#f4f4f4", font=font_style).pack(pady=5)
date_entry = tk.Entry(root, font=font_style, width=25)
date_entry.insert(0, today_date)
date_entry.pack(pady=5)

tk.Label(root, text=":קטגוריה", bg="#f4f4f4", font=font_style).pack(pady=5)
category_combobox = ttk.Combobox(root, values=["מקום אירוע", "מקדמה אירוע", "אלכוהול", "שמלה", "צלם", "דיגיי", "צלם מגנטים",
                                               "חליפה", "עיצוב חתונה", "רב", "אקום לחתונה", "נגן", "עיצוב שיער",
                                               "איפור", "רבנות", "אישורי הגעה", "התארגנות"], font=font_style)
category_combobox.pack(pady=5)

tk.Label(root, text=":סכום", bg="#f4f4f4", font=font_style).pack(pady=5)
amount_entry = tk.Entry(root, font=font_style, width=25)
amount_entry.pack(pady=5)

tk.Label(root, text=":תיאור", bg="#f4f4f4", font=font_style).pack(pady=5)
description_entry = tk.Entry(root, font=font_style, width=50)  # Increased width for better visibility
description_entry.pack(pady=5)

# Buttons
tk.Button(root, text="הוסף הוצאה", command=add_expense, font=font_style, bg="#d1e7dd").pack(pady=7)

# Table to Display Expenses
columns = ("תאריך", "קטגוריה", "סכום", "תיאור", "מפתח")
table = ttk.Treeview(root, columns=columns, show="headings", height=15)
style = ttk.Style()
style.configure("Treeview.Heading", font=font_style)  # Apply font to the headers
style.configure("Treeview", font=font_style)

for col in columns:
    if col == "תיאור":
        table.column(col, width=600, anchor="w", stretch=tk.NO)  # Make the description column wider
    else:
        table.column(col, width=200, anchor="w", stretch=tk.NO)
    table.heading(col, text=col)

table["displaycolumns"] = ("תאריך", "קטגוריה", "סכום", "תיאור")  # Hide the key column

table.pack(pady=15)

# Total label
total_label = tk.Label(root, text="₪0.00 :סך הכל", bg="#f4f4f4", font=("Arial", 18))
total_label.pack(pady=7)

# Initialize database and load data
setup_database()
load_expenses()

# Bind row select event
table.bind("<ButtonRelease-1>", on_row_select)
table.bind("<Button-3>", on_right_click)       # Right-click to deselect

# Delete button to appear beneath the table (initially hidden)
delete_button = tk.Button(root, text="מחק את השורה המודגשת", command=delete_expense, font=font_style, bg="#f8d7da")
delete_button.pack_forget()  # Initially hidden


# Add Edit button to appear beneath the table (initially hidden)
edit_button = tk.Button(root, text="ערוך תיאור", command=edit_description, font=font_style, bg="#ffeeba")
edit_button.pack_forget()

# Delete all expenses button
delete_all_button = tk.Button(root, text="מחק הכל", command=delete_all_expenses, font=font_style, bg="#f8d7da")
delete_all_button.pack(pady=10)




# Add button to show category total
# Create a frame to hold the combobox and button
category_frame = tk.Frame(root, bg="#f4f4f4")
category_frame.pack(pady=7)


# Add the combobox to the frame
# Add the button to the frame
category_total_button = tk.Button(category_frame, text="הצג סך כל ההוצאה עבור קטגוריה", command=lambda: calculate_category_total(category_combobox2.get()), font=font_style, bg="#d1e7dd")
category_total_button.pack(side=tk.LEFT, padx=5)
category_combobox2 = ttk.Combobox(category_frame, values=["מקום אירוע", "מקדמה אירוע", "אלכוהול", "שמלה", "צלם", "דיגיי", "צלם מגנטים", "חליפה",
                                                          "עיצוב חתונה", "רב", "אקום לחתונה", "נגן",
                                                          "עיצוב שיער", "איפור", "רבנות", "אישורי הגעה", "התארגנות"], font=font_style)
category_combobox2.pack(side=tk.LEFT, padx=5)
tk.Label(category_frame, text=":בחר קטגוריה לבדיקה", bg="#f4f4f4", font=font_style).pack(side=tk.LEFT, pady=5)




# Run the app
root.mainloop()
