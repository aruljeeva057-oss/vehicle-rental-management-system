from datetime import date

from database import run_query
from utils import (
    ask_choice, ask_id, ask_int, ask_money, ask_text, header
)

VEHICLE_TYPES = ("CAR", "BIKE", "SUV", "VAN")
STATUSES = ("ACTIVE", "MAINTENANCE", "RETIRED")

COLUMNS = """id, registration_no, make, model, manufacture_year,
             vehicle_type, seating_capacity, rental_rate_per_day,
             operational_status, created_at, updated_at"""


def get_vehicle(vehicle_id):
    result = run_query(
        f"SELECT {COLUMNS} FROM vehicles WHERE id = %s",
        (vehicle_id,),
        fetch=True
    )
    return result[0] if result else None


def add_vehicle():
    print("\n--- Add Vehicle ---")

    registration_no = ask_text("Registration number: ").upper()
    make = ask_text("Make/brand: ")
    model = ask_text("Model: ")
    manufacture_year = ask_int(
        "Manufacture year: ", minimum=1886, maximum=date.today().year + 1
    )
    seating_capacity = ask_int("Seating capacity: ", minimum=1, maximum=100)
    rental_rate = ask_money("Rental rate per day: ")
    vehicle_type = ask_choice("Type (CAR/BIKE/SUV/VAN): ", VEHICLE_TYPES)

    duplicate = run_query(
        "SELECT id FROM vehicles WHERE registration_no = %s",
        (registration_no,),
        fetch=True
    )

    if duplicate is None:
        print("Unable to check registration number.")
        return

    if duplicate:
        print("This registration number already exists.")
        return

    result = run_query(
        """INSERT INTO vehicles
           (registration_no, make, model, manufacture_year,
            vehicle_type, seating_capacity, rental_rate_per_day)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            registration_no, make, model, manufacture_year,
            vehicle_type, seating_capacity, rental_rate
        )
    )

    if result is not None:
        print(f"Vehicle added successfully. ID: {result}")
    else:
        print("Unable to add vehicle.")


def view_vehicles():
    print("\n--- All Vehicles ---")

    vehicles = run_query(
        """SELECT id, registration_no, make, model, manufacture_year,
                  vehicle_type, seating_capacity,
                  rental_rate_per_day, operational_status
           FROM vehicles ORDER BY id""",
        fetch=True
    )

    if vehicles is None:
        print("Unable to retrieve vehicles.")
        return

    if not vehicles:
        print("No vehicles found.")
        return

    for v in vehicles:
        print("-" * 45)
        print(f"ID: {v[0]}")
        print(f"Registration: {v[1]}")
        print(f"Make and model: {v[2]} {v[3]}")
        print(f"Year: {v[4]}")
        print(f"Type: {v[5]}")
        print(f"Seats: {v[6]}")
        print(f"Rate per day: ₹{v[7]}")
        print(f"Status: {v[8]}")


def search_vehicle():
    registration_no = ask_text("Enter registration number: ").upper()

    vehicles = run_query(
        """SELECT id, registration_no, make, model, manufacture_year,
                  vehicle_type, seating_capacity,
                  rental_rate_per_day, operational_status
           FROM vehicles WHERE registration_no LIKE %s ORDER BY id""",
        (f"%{registration_no}%",),
        fetch=True
    )

    if vehicles is None:
        print("Unable to search vehicles.")
        return

    if not vehicles:
        print("No matching vehicles found.")
        return

    for v in vehicles:
        print(
            f"{v[1]} | {v[2]} {v[3]} | {v[5]} | "
            f"₹{v[7]}/day | {v[8]} | ID: {v[0]}"
        )


def filter_vehicles():
    vehicle_type = ask_choice("Enter type (CAR/BIKE/SUV/VAN): ", VEHICLE_TYPES)

    vehicles = run_query(
        """SELECT id, registration_no, make, model,
                  rental_rate_per_day, operational_status
           FROM vehicles WHERE vehicle_type = %s ORDER BY id""",
        (vehicle_type,),
        fetch=True
    )

    if vehicles is None:
        print("Unable to filter vehicles.")
        return

    if not vehicles:
        print("No vehicles found for this type.")
        return

    for v in vehicles:
        print(
            f"{v[1]} | {v[2]} {v[3]} | "
            f"₹{v[4]}/day | {v[5]} | ID: {v[0]}"
        )


def view_vehicle_details():
    vehicle_id = ask_id("Enter vehicle ID: ")
    vehicle = get_vehicle(vehicle_id)

    if not vehicle:
        print("Vehicle not found.")
        return

    labels = (
        "ID", "Registration", "Make", "Model", "Year", "Type",
        "Seats", "Rate", "Status", "Created at", "Updated at"
    )
    print("\n--- Vehicle Details ---")
    for name, value in zip(labels, vehicle):
        print(f"{name}: {value}")


def update_vehicle_rate():
    vehicle_id = ask_id("Enter vehicle ID: ")

    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        print("Vehicle not found.")
        return

    rate = ask_money("New rental rate per day: ")

    result = run_query(
        "UPDATE vehicles SET rental_rate_per_day = %s WHERE id = %s",
        (rate, vehicle_id)
    )

    if result is not None:
        print("Rental rate updated.")
    else:
        print("Unable to update rental rate.")


def update_vehicle_status():
    vehicle_id = ask_id("Enter vehicle ID: ")

    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        print("Vehicle not found.")
        return

    status = ask_choice("New status (ACTIVE/MAINTENANCE/RETIRED): ", STATUSES)

    result = run_query(
        "UPDATE vehicles SET operational_status = %s WHERE id = %s",
        (status, vehicle_id)
    )

    if result is not None:
        print("Vehicle status updated.")
    else:
        print("Unable to update vehicle status.")


def vehicle_summary():
    result = run_query(
        """SELECT operational_status, COUNT(*)
           FROM vehicles GROUP BY operational_status""",
        fetch=True
    )

    if result is None:
        print("Unable to retrieve vehicle summary.")
        return

    print("\n--- Vehicle Summary ---")
    if not result:
        print("No vehicles found.")
    for status, count in result:
        print(f"{status}: {count}")


def delete_vehicle():
    vehicle_id = ask_id("Enter vehicle ID: ")

    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        print("Vehicle not found.")
        return

    bookings = run_query(
        "SELECT id FROM bookings WHERE vehicle_id = %s LIMIT 1",
        (vehicle_id,),
        fetch=True
    )

    if bookings is None:
        print("Unable to check vehicle bookings.")
        return

    if bookings:
        print("Cannot delete a vehicle that has bookings.")
        return

    confirm = input("Delete this vehicle? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Deletion cancelled.")
        return

    result = run_query(
        "DELETE FROM vehicles WHERE id = %s",
        (vehicle_id,)
    )

    if result is not None:
        print("Vehicle deleted.")
    else:
        print("Unable to delete vehicle.")


def vehicle_menu():
    while True:
        header("VEHICLE MANAGEMENT")
        print("1. Add Vehicle")
        print("2. View All Vehicles")
        print("3. Search Vehicle")
        print("4. Filter Vehicles by Type")
        print("5. View Vehicle Details")
        print("6. Update Rental Rate")
        print("7. Update Vehicle Status")
        print("8. Vehicle Summary")
        print("9. Delete Vehicle")
        print("10. Back to Main Menu")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_vehicle()
        elif choice == "2":
            view_vehicles()
        elif choice == "3":
            search_vehicle()
        elif choice == "4":
            filter_vehicles()
        elif choice == "5":
            view_vehicle_details()
        elif choice == "6":
            update_vehicle_rate()
        elif choice == "7":
            update_vehicle_status()
        elif choice == "8":
            vehicle_summary()
        elif choice == "9":
            delete_vehicle()
        elif choice == "10":
            break
        else:
            print("Invalid choice. Try again.")
