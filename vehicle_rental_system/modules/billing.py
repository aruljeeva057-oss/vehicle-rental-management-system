from decimal import Decimal, ROUND_HALF_UP

from database import run_query
from utils import (
    CENT,
    ask_id,
    ask_int,
    ask_money,
    ask_text,
    ask_yes_no,
    header,
    show_table,
)

GST_RATE = Decimal("0.18")  # fixed 18% GST

HEADERS = [
    "Bill ID",
    "Booking ID",
    "Days",
    "Base Amount",
    "Late Fee",
    "GST (18%)",
    "Total Due",
    "Amount Paid",
    "Status",
]

BILL_COLUMNS = """id, booking_id, rental_days, base_amount,
                  late_fee, gst_amount, total_due, amount_paid, status"""


def generate_bill():
    print("\n--- Generate Bill ---")

    booking_id = ask_id("Booking ID: ")

    existing = run_query(
        "SELECT id FROM bills WHERE booking_id = %s", (booking_id,), fetch=True
    )

    if existing is None:
        print("Unable to check existing bill.")
        return

    if existing:
        print("A bill already exists for this booking.")
        return

    bookings = run_query(
        """SELECT rental_start, rental_end, daily_rate,
                  security_deposit, status
           FROM bookings WHERE id = %s""",
        (booking_id,),
        fetch=True,
    )

    if bookings is None:
        print("Unable to retrieve booking.")
        return

    if not bookings:
        print("Booking not found.")
        return

    booking = bookings[0]

    if booking[4] not in ("ACTIVE", "COMPLETED"):
        print("A bill can only be generated for an active or completed booking.")
        return

    rental_days = (booking[1] - booking[0]).days
    daily_rate = booking[2]
    base_amount = daily_rate * rental_days
    deposit = booking[3]

    print(f"Rental days: {rental_days}")
    print(f"Base amount: ₹{base_amount:.2f}")
    print(f"Security deposit: ₹{deposit:.2f}")
    late_fee = Decimal("0.00")
    if ask_yes_no("Was the customer late in returning the vehicle? (yes/no): "):
        late_days = ask_int("Number of days late: ", minimum=1, maximum=365)
        late_fee = daily_rate * late_days
    subtotal = base_amount + late_fee
    gst_amount = (subtotal * GST_RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    total_due = subtotal + gst_amount

    print("\n--- Bill Summary ---")
    print(f"Rental amount : ₹{base_amount:.2f}")
    print(f"Late fee      : ₹{late_fee:.2f}")
    print(f"Before GST    : ₹{subtotal:.2f}")
    print(f"GST (18%)     : ₹{gst_amount:.2f}")
    print(f"Total due     : ₹{total_due:.2f}")

    result = run_query(
        """INSERT INTO bills
           (booking_id, rental_days, base_amount, late_fee, gst_amount,
            deposit, total_due, amount_paid, status, deposit_status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, 0,
                   'UNPAID', 'NOT_SETTLED')""",
        (
            booking_id,
            rental_days,
            base_amount,
            late_fee,
            gst_amount,
            deposit,
            total_due,
        ),
    )

    if result is not None:
        print(f"\nBill generated successfully. Bill ID: {result}")
    else:
        print("Failed to generate bill.")


def view_bills():
    print("\n--- All Bills ---")

    rows = run_query(f"SELECT {BILL_COLUMNS} FROM bills ORDER BY id DESC", fetch=True)

    if rows is None:
        print("Unable to retrieve bills.")
    elif rows:
        show_table(HEADERS, rows)
    else:
        print("No bills found.")


def search_bill():
    print("\n--- Search Bill ---")

    bill_id = ask_id("Bill ID: ")

    rows = run_query(
        f"SELECT {BILL_COLUMNS} FROM bills WHERE id = %s", (bill_id,), fetch=True
    )

    if rows is None:
        print("Unable to search bill.")
    elif rows:
        show_table(HEADERS, rows)
    else:
        print("Bill not found.")


def record_payment():
    print("\n--- Record Payment ---")

    bill_id = ask_id("Bill ID: ")

    bills = run_query(
        """SELECT total_due, amount_paid, status
           FROM bills WHERE id = %s""",
        (bill_id,),
        fetch=True,
    )

    if bills is None:
        print("Unable to retrieve bill.")
        return

    if not bills:
        print("Bill not found.")
        return

    total_due, amount_paid, status = bills[0]

    if status == "PAID":
        print("This bill is already fully paid.")
        return

    remaining = total_due - amount_paid
    print(f"Remaining balance: ₹{remaining:.2f}")

    amount = ask_money("Payment amount (₹): ")

    if amount > remaining:
        print(f"Payment exceeds the remaining balance of ₹{remaining:.2f}.")
        return

    new_paid = amount_paid + amount

    if new_paid >= total_due:
        new_status = "PAID"
    else:
        new_status = "PARTIALLY_PAID"

    result = run_query(
        """UPDATE bills
           SET amount_paid = %s, status = %s
           WHERE id = %s""",
        (new_paid, new_status, bill_id),
    )

    if result is not None:
        print("Payment recorded successfully.")
        print(f"Amount paid: ₹{new_paid:.2f}")
        print(f"Remaining balance: ₹{total_due - new_paid:.2f}")
        print(f"Bill status: {new_status}")
    else:
        print("Failed to record payment.")


def settle_deposit():
    print("\n--- Settle Security Deposit ---")

    bill_id = ask_id("Bill ID: ")

    bills = run_query(
        """SELECT booking_id, deposit, deposit_status, status
           FROM bills WHERE id = %s""",
        (bill_id,),
        fetch=True,
    )

    if bills is None:
        print("Unable to retrieve bill.")
        return

    if not bills:
        print("Bill not found.")
        return

    bill = bills[0]

    if bill[2] != "NOT_SETTLED":
        print(f"Deposit already settled: {bill[2]}.")
        return

    if bill[3] != "PAID":
        print("The rental bill must be fully paid before settling the deposit.")
        return

    deposit = bill[1]

    print(f"Security deposit: ₹{deposit:.2f}")
    print("1. Refund deposit")
    print("2. Apply deposit to charges")

    choice = ask_text("Choose an option: ")

    if choice == "1":
        deposit_status = "REFUNDED"
    elif choice == "2":
        deposit_status = "APPLIED"
    else:
        print("Invalid choice.")
        return

    result = run_query(
        "UPDATE bills SET deposit_status = %s WHERE id = %s", (deposit_status, bill_id)
    )

    if result is not None:
        print(f"Deposit settled successfully: {deposit_status}.")
    else:
        print("Failed to settle deposit.")


def billing_menu():
    while True:
        header("BILLING MANAGEMENT")

        print("1. Generate Bill")
        print("2. View All Bills")
        print("3. Search Bill")
        print("4. Record Payment")
        print("5. Settle Security Deposit")
        print("6. Back")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            generate_bill()
        elif choice == "2":
            view_bills()
        elif choice == "3":
            search_bill()
        elif choice == "4":
            record_payment()
        elif choice == "5":
            settle_deposit()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Try again.")
