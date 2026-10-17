from datetime import date

from database import run_query
from utils import ask_date, ask_id, ask_money, ask_text, header, show_table

HEADERS = [
    "Booking ID",
    "Customer ID",
    "Vehicle ID",
    "Start Date",
    "End Date",
    "Daily Rate",
    "Status",
]


def add_booking():
    print("\n--- Add Booking ---")

    customer_id = ask_id("Customer ID: ")
    vehicle_id = ask_id("Vehicle ID: ")

    customers = run_query(
        "SELECT id FROM customers WHERE id = %s", (customer_id,), fetch=True
    )

    if customers is None:
        print("Unable to check customer.")
        return

    if not customers:
        print("Customer not found.")
        return

    vehicles = run_query(
        """SELECT id, rental_rate_per_day, operational_status
           FROM vehicles WHERE id = %s""",
        (vehicle_id,),
        fetch=True,
    )

    if vehicles is None:
        print("Unable to check vehicle.")
        return

    if not vehicles:
        print("Vehicle not found.")
        return

    vehicle = vehicles[0]

    if vehicle[2] != "ACTIVE":
        print("This vehicle is not available for rental.")
        return

    print("\nBooking type:")
    print("1. Current booking (starts today)")
    print("2. Future booking (you choose the start date)")

    while True:
        booking_type = ask_text("Choose 1 or 2: ")
        if booking_type in ("1", "2"):
            break
        print("Please enter 1 or 2.")

    today = date.today()

    if booking_type == "1":
        start = today
        status = "ACTIVE"
        print(f"Start date (today): {start}")
    else:
        status = "RESERVED"
        while True:
            start = ask_date("Start date (YYYY-MM-DD): ")
            if start > today:
                break
            print(
                "A future booking must start after today. "
                "Choose 'Current booking' to start today."
            )

    while True:
        end = ask_date("End date / return date (YYYY-MM-DD): ")
        if end > start:
            break
        print("End date must be after the start date.")

    overlapping = run_query(
        """SELECT id FROM bookings
           WHERE vehicle_id = %s
           AND status IN ('RESERVED', 'ACTIVE')
           AND rental_start < %s
           AND rental_end > %s
           LIMIT 1""",
        (vehicle_id, end, start),
        fetch=True,
    )

    if overlapping is None:
        print("Unable to check vehicle availability.")
        return

    if overlapping:
        print("Vehicle is already booked for these dates.")
        return

    deposit = ask_money("Security deposit (enter 0 for no deposit): ", allow_zero=True)

    daily_rate = vehicle[1]
    rental_days = (end - start).days
    total = daily_rate * rental_days

    print("\n--- Booking Summary ---")
    print(f"Booking type: {'Current' if status == 'ACTIVE' else 'Future'}")
    print(f"Start date: {start}")
    print(f"End date: {end}")
    print(f"Rental days: {rental_days}")
    print(f"Daily rate: ₹{daily_rate}")
    print(f"Estimated rental amount (before GST): ₹{total:.2f}")
    print(f"Security deposit: ₹{deposit:.2f}")
    print(f"Booking status: {status}")

    confirm = ask_text("Confirm booking? (yes/no): ").lower()

    if confirm != "yes":
        print("Booking cancelled.")
        return

    result = run_query(
        """INSERT INTO bookings
           (customer_id, vehicle_id, rental_start, rental_end,
            daily_rate, security_deposit, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (customer_id, vehicle_id, start, end, daily_rate, deposit, status),
    )

    if result is not None:
        print(f"Booking created successfully. ID: {result}")
    else:
        print("Failed to create booking.")


def view_bookings():
    print("\n--- All Bookings ---")

    rows = run_query(
        """SELECT id, customer_id, vehicle_id, rental_start,
                  rental_end, daily_rate, status
           FROM bookings ORDER BY id DESC""",
        fetch=True,
    )

    if rows is None:
        print("Unable to retrieve bookings.")
    elif rows:
        show_table(HEADERS, rows)
    else:
        print("No bookings found.")


def search_booking():
    print("\n--- Search Booking ---")

    booking_id = ask_id("Booking ID: ")

    rows = run_query(
        """SELECT id, customer_id, vehicle_id, rental_start,
                  rental_end, daily_rate, status
           FROM bookings WHERE id = %s""",
        (booking_id,),
        fetch=True,
    )

    if rows is None:
        print("Unable to search booking.")
    elif rows:
        show_table(HEADERS, rows)
    else:
        print("Booking not found.")


def view_customer_bookings():
    print("\n--- Customer Bookings ---")

    customer_id = ask_id("Customer ID: ")

    rows = run_query(
        """SELECT id, customer_id, vehicle_id, rental_start,
                  rental_end, daily_rate, status
           FROM bookings WHERE customer_id = %s
           ORDER BY id DESC""",
        (customer_id,),
        fetch=True,
    )

    if rows is None:
        print("Unable to retrieve customer bookings.")
    elif rows:
        show_table(HEADERS, rows)
    else:
        print("No bookings found for this customer.")


def cancel_booking():
    print("\n--- Cancel Booking ---")

    booking_id = ask_id("Booking ID: ")

    rows = run_query(
        "SELECT status FROM bookings WHERE id = %s", (booking_id,), fetch=True
    )

    if rows is None:
        print("Unable to retrieve booking.")
        return

    if not rows:
        print("Booking not found.")
        return

    if rows[0][0] != "RESERVED":
        print("Only reserved bookings can be cancelled.")
        return

    confirm = ask_text("Cancel this booking? (yes/no): ").lower()

    if confirm != "yes":
        print("Cancellation aborted.")
        return

    result = run_query(
        "UPDATE bookings SET status = 'CANCELLED' WHERE id = %s", (booking_id,)
    )

    if result is not None:
        print("Booking cancelled successfully.")
    else:
        print("Failed to cancel booking.")


def update_booking_status():
    print("\n--- Update Booking Status ---")

    booking_id = ask_id("Booking ID: ")

    rows = run_query(
        "SELECT status FROM bookings WHERE id = %s", (booking_id,), fetch=True
    )

    if rows is None:
        print("Unable to retrieve booking.")
        return

    if not rows:
        print("Booking not found.")
        return

    print("1. RESERVED")
    print("2. ACTIVE")
    print("3. COMPLETED")
    choice = ask_text("Select new status: ")

    statuses = {"1": "RESERVED", "2": "ACTIVE", "3": "COMPLETED"}

    if choice not in statuses:
        print("Invalid choice.")
        return

    new_status = statuses[choice]

    if rows[0][0] in ("CANCELLED", "COMPLETED"):
        print("This booking cannot be updated.")
        return

    result = run_query(
        "UPDATE bookings SET status = %s WHERE id = %s", (new_status, booking_id)
    )

    if result is not None:
        print("Booking status updated successfully.")
    else:
        print("Failed to update booking status.")


def booking_menu():
    while True:
        header("BOOKING MANAGEMENT")

        print("1. Add Booking")
        print("2. View All Bookings")
        print("3. Search Booking")
        print("4. View Customer Bookings")
        print("5. Cancel Booking")
        print("6. Update Booking Status")
        print("7. Back")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_booking()
        elif choice == "2":
            view_bookings()
        elif choice == "3":
            search_booking()
        elif choice == "4":
            view_customer_bookings()
        elif choice == "5":
            cancel_booking()
        elif choice == "6":
            update_booking_status()
        elif choice == "7":
            break
        else:
            print("Invalid choice. Try again.")
