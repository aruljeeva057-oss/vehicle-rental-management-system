
from database import get_connection
from modules.billing import billing_menu
from modules.booking import booking_menu
from modules.customer import customer_menu
from modules.vehicle import vehicle_menu
from utils import header


def main():
    connection = get_connection()
    if connection is None:
        print("Could not connect to the database. Check your .env file.")
        return
    connection.close()

    menus = {
        "1": vehicle_menu,
        "2": customer_menu,
        "3": booking_menu,
        "4": billing_menu,
    }

    try:
        while True:
            header("VEHICLE RENTAL MANAGEMENT SYSTEM")
            print("1. Vehicle Management\n2. Customer Management")
            print("3. Booking\n4. Billing\n5. Exit")
            choice = input("Enter your choice: ").strip()

            if choice == "5":
                print("\nThank you for using the system!")
                break
            menu = menus.get(choice)
            if menu:
                menu()
            else:
                print("\nInvalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\n\nProgram closed.")


if __name__ == "__main__":
    main()
