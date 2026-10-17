from database import run_query
from utils import (
    ask_email,
    ask_id,
    ask_licence,
    ask_phone,
    ask_text,
    header,
    show_table,
)

HEADERS = ["ID", "Name", "Phone", "Email", "Licence No"]


def add_customer():
    print("\n--- Add Customer ---")

    name = ask_text("Full name: ")
    phone = ask_phone("Phone number (10 digits): ")
    email = ask_email("Email: ")
    address = ask_text("Address: ")
    licence_no = ask_licence("Driving licence number (letters and numbers): ")

    existing = run_query(
        """SELECT id FROM customers
           WHERE phone = %s OR email = %s OR licence_no = %s""",
        (phone, email, licence_no),
        fetch=True,
    )

    if existing is None:
        print("Unable to check customer details.")
        return

    if existing:
        print("Phone, email or licence number already exists.")
        return

    result = run_query(
        """INSERT INTO customers
           (full_name, phone, email, address, licence_no)
           VALUES (%s, %s, %s, %s, %s)""",
        (name, phone, email, address, licence_no),
    )

    if result is not None:
        print(f"Customer added successfully. ID: {result}")
    else:
        print("Unable to add customer.")


def view_customers():
    print("\n--- All Customers ---")

    rows = run_query(
        """SELECT id, full_name, phone, email, licence_no
           FROM customers ORDER BY id""",
        fetch=True,
    )

    if rows is None:
        print("Unable to retrieve customers.")
        return

    show_table(HEADERS, rows)


def search_customer():
    keyword = ask_text("Enter name, phone or licence number: ")
    pattern = f"%{keyword}%"

    rows = run_query(
        """SELECT id, full_name, phone, email, licence_no
           FROM customers
           WHERE full_name LIKE %s
              OR phone LIKE %s
              OR licence_no LIKE %s
           ORDER BY id""",
        (pattern, pattern, pattern),
        fetch=True,
    )

    if rows is None:
        print("Unable to search customers.")
        return

    show_table(HEADERS, rows)


def view_customer_details():
    customer_id = ask_id("Customer ID: ")

    rows = run_query(
        """SELECT id, full_name, phone, email, address,
                  licence_no, created_at
           FROM customers WHERE id = %s""",
        (customer_id,),
        fetch=True,
    )

    if rows is None:
        print("Unable to retrieve customer details.")
        return

    if not rows:
        print("Customer not found.")
        return

    customer = rows[0]

    print("\n--- Customer Details ---")
    print(f"ID: {customer[0]}")
    print(f"Name: {customer[1]}")
    print(f"Phone: {customer[2]}")
    print(f"Email: {customer[3]}")
    print(f"Address: {customer[4]}")
    print(f"Licence number: {customer[5]}")
    print(f"Registered on: {customer[6]}")


def update_customer():
    customer_id = ask_id("Customer ID: ")

    rows = run_query(
        "SELECT id FROM customers WHERE id = %s", (customer_id,), fetch=True
    )

    if rows is None:
        print("Unable to check customer.")
        return

    if not rows:
        print("Customer not found.")
        return

    print("\n1. Update name")
    print("2. Update phone")
    print("3. Update email")
    print("4. Update address")
    print("5. Update licence number")

    choice = input("Enter your choice: ").strip()
    fields = {
        "1": ("full_name", lambda: ask_text("New full name: ")),
        "2": ("phone", lambda: ask_phone("New phone number (10 digits): ")),
        "3": ("email", lambda: ask_email("New email: ")),
        "4": ("address", lambda: ask_text("New address: ")),
        "5": (
            "licence_no",
            lambda: ask_licence("New licence number (letters and numbers): "),
        ),
    }

    if choice not in fields:
        print("Invalid choice.")
        return

    column, ask_value = fields[choice]
    value = ask_value()

    if column in ("phone", "email", "licence_no"):
        duplicate = run_query(
            f"SELECT id FROM customers WHERE {column} = %s AND id <> %s",
            (value, customer_id),
            fetch=True,
        )

        if duplicate is None:
            print("Unable to check duplicate details.")
            return

        if duplicate:
            print("That value is already used by another customer.")
            return

    result = run_query(
        f"UPDATE customers SET {column} = %s WHERE id = %s", (value, customer_id)
    )

    if result is not None:
        print("Customer updated successfully.")
    else:
        print("Unable to update customer.")


def delete_customer():
    customer_id = ask_id("Customer ID to delete: ")

    rows = run_query(
        "SELECT id FROM customers WHERE id = %s", (customer_id,), fetch=True
    )

    if rows is None:
        print("Unable to check customer.")
        return

    if not rows:
        print("Customer not found.")
        return

    bookings = run_query(
        "SELECT id FROM bookings WHERE customer_id = %s LIMIT 1",
        (customer_id,),
        fetch=True,
    )

    if bookings is None:
        print("Unable to check customer bookings.")
        return

    if bookings:
        print("Cannot delete a customer who has booking records.")
        return

    confirm = input("Delete this customer? (yes/no): ").strip().lower()

    if confirm != "yes":
        print("Deletion cancelled.")
        return

    result = run_query("DELETE FROM customers WHERE id = %s", (customer_id,))

    if result is not None:
        print("Customer deleted successfully.")
    else:
        print("Unable to delete customer.")


def customer_menu():
    while True:
        header("CUSTOMER MANAGEMENT")

        print("1. Add Customer")
        print("2. View All Customers")
        print("3. Search Customer")
        print("4. View Customer Details")
        print("5. Update Customer")
        print("6. Delete Customer")
        print("7. Back to Main Menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_customer()
        elif choice == "2":
            view_customers()
        elif choice == "3":
            search_customer()
        elif choice == "4":
            view_customer_details()
        elif choice == "5":
            update_customer()
        elif choice == "6":
            delete_customer()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Try again.")
