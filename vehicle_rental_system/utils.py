import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

CENT = Decimal("0.01")
MAX_MONEY = Decimal("9999999999.99")


def header(title):
    print("\n" + "=" * 45)
    print(f" {title}")
    print("=" * 45)


def show_table(headers, rows):

    if not rows:
        print("\nNo records found.")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print("\n" + line)
    print("-" * len(line))
    for row in rows:
        print(" | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)))


def ask_text(prompt, required=True):
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field cannot be empty.")


def ask_int(prompt, minimum=None, maximum=None):

    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("Please enter a whole number.")
            continue
        if minimum is not None and value < minimum:
            print(f"Number must be at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"Number must not be more than {maximum}.")
            continue
        return value


def ask_id(prompt):

    return ask_int(prompt, minimum=1, maximum=4294967295)


def ask_money(prompt, allow_zero=False):

    while True:
        try:
            value = Decimal(input(prompt).strip())
        except InvalidOperation:
            print("Please enter a valid amount.")
            continue
        if not value.is_finite():
            print("Please enter a valid amount.")
            continue
        if abs(value) > MAX_MONEY:
            print("That amount is too large.")
            continue
        value = value.quantize(CENT, rounding=ROUND_HALF_UP)
        if value < 0:
            print("Amount cannot be negative.")
            continue
        if value == 0 and not allow_zero:
            print("Amount must be greater than zero.")
            continue
        return value


def ask_choice(prompt, options):

    while True:
        value = input(prompt).strip().upper()
        if value in options:
            return value
        print("Choose one of: " + ", ".join(options))


def ask_yes_no(prompt):

    while True:
        value = input(prompt).strip().lower()
        if value in ("yes", "y"):
            return True
        if value in ("no", "n"):
            return False
        print("Please answer yes or no.")


def ask_date(prompt):

    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%Y-%m-%d").date()
        except ValueError:
            print("Use the format YYYY-MM-DD (example: 2026-10-25).")


# ------------------------------------------------- customer validation
EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+\-]+@(?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,}")


def is_valid_phone(phone):

    return re.fullmatch(r"[0-9]{10}", phone) is not None


def is_valid_email(email):
    return len(email) <= 254 and EMAIL_PATTERN.fullmatch(email) is not None


def clean_licence(licence):

    return re.sub(r"[\s\-]", "", licence).upper()


def is_valid_licence(licence):

    return (
        len(licence) <= 40
        and re.fullmatch(r"[A-Z0-9]+", licence) is not None
        and any(c.isalpha() for c in licence)
        and any(c.isdigit() for c in licence)
    )


def ask_phone(prompt):
    while True:
        phone = ask_text(prompt)
        if is_valid_phone(phone):
            return phone
        print("Phone number must be exactly 10 digits (numbers only).")


def ask_email(prompt):
    while True:
        email = ask_text(prompt)
        if is_valid_email(email):
            return email
        print("Enter a valid email address (example: name@example.com).")


def ask_licence(prompt):
    while True:
        licence = clean_licence(ask_text(prompt))
        if is_valid_licence(licence):
            return licence
        print(
            "Licence number must contain both letters and numbers "
            "(no other symbols)."
        )
