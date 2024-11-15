import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);
''')
conn.commit()


def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0


def generate_card_number():
    while True:
        partial_card_number = "400000" + str(random.randint(0, 999999999)).zfill(9)
        for checksum in range(10):
            card_number = partial_card_number + str(checksum)
            if luhn_checksum(card_number):
                return card_number


def generate_pin():
    return str(random.randint(0, 9999)).zfill(4)


def create_account():
    card_number = generate_card_number()
    pin = generate_pin()

    cur.execute('INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)', (card_number, pin, 0))
    conn.commit()

    print("\nYour card has been created")
    print("Your card number:")
    print(card_number)
    print("Your card PIN:")
    print(pin)


def add_income(card_number):
    amount = int(input("Enter income:\n"))
    cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, card_number))
    conn.commit()
    print("Income was added!")


def do_transfer(card_number):
    print("Transfer")
    receiver_card = input("Enter card number:\n")

    # Validate card number with Luhn algorithm
    if not luhn_checksum(receiver_card):
        print("Probably you made a mistake in the card number. Please try again!")
        return

    # Check if receiver exists
    cur.execute('SELECT * FROM card WHERE number = ?', (receiver_card,))
    receiver_account = cur.fetchone()

    if receiver_account is None:
        print("Such a card does not exist.")
        return

    # Prevent transferring to the same account
    if receiver_card == card_number:
        print("You can't transfer money to the same account!")
        return

    # Get the transfer amount and check if the balance is sufficient
    amount = int(input("Enter how much money you want to transfer:\n"))
    cur.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
    sender_balance = cur.fetchone()[0]

    if amount > sender_balance:
        print("Not enough money!")
    else:
        # Perform the transfer
        cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?', (amount, card_number))
        cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', (amount, receiver_card))
        conn.commit()
        print("Success!")


def close_account(card_number):
    cur.execute('DELETE FROM card WHERE number = ?', (card_number,))
    conn.commit()
    print("The account has been closed!")


def log_into_account():
    card_number = input("\nEnter your card number:\n")
    pin = input("Enter your PIN:\n")

    cur.execute('SELECT * FROM card WHERE number = ? AND pin = ?', (card_number, pin))
    account = cur.fetchone()

    if account:
        print("\nYou have successfully logged in!")
        while True:
            print("\n1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice = input()
            if choice == "1":
                cur.execute('SELECT balance FROM card WHERE number = ?', (card_number,))
                balance = cur.fetchone()[0]
                print(f"\nBalance: {balance}")
            elif choice == "2":
                add_income(card_number)
            elif choice == "3":
                do_transfer(card_number)
            elif choice == "4":
                close_account(card_number)
                break
            elif choice == "5":
                print("\nYou have successfully logged out!")
                break
            elif choice == "0":
                print("\nBye!")
                conn.close()
                exit()
            else:
                print("\nInvalid option. Try again.")
    else:
        print("\nWrong card number or PIN!")


def main():
    while True:
        print("\n1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = input()
        if choice == "1":
            create_account()
        elif choice == "2":
            log_into_account()
        elif choice == "0":
            print("\nBye!")
            conn.close()
            break
        else:
            print("\nInvalid option. Try again.")


# Start the program
main()
