import csv
import os
import signal
import sys

# Mapping of single-letter inputs to poker hands
hand_mapping = {
    '2': 'Two pairs',
    '3': 'Triple',
    's': 'Straight',
    'f': 'Flush (Color)',
    'fh': 'Full House',
    '4': 'Four pairs',
    'sf': 'Straight Flush',
    '5': '5 pairs',
    'r': 'Royal Flush',
    'rj': 'Royal Jelly',
    '0': 'First hand lost',
}

hand_bet_multipliers = {
    '2': 1,   # Two pairs
    '3': 1,   # Triple
    's': 3,   # Straight
    'f': 4,   # Flush (Color)
    'fh': 5,  # Full House
    '4': 10,  # Four pairs
    'sf': 20, # Straight Flush
    '5': 50,  # 5 pairs
    'r': 100, # Royal Flush
    'rj': 500 # Royal Jelly
}
initial_bet_scalar = 1  # Replace with user input if needed


# Data storage structure
data_storage = []

def summarize_data(num_rounds):
    """Function to summarize data and write to a single CSV file."""
    filename = f'frequencies_{num_rounds}.csv'
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Observation', 'Hand', 'Last Double or Nothing', 'Success/Failure', 'Cumulative Winnings (b)'])
        writer.writeheader()
        for i, entry in enumerate(data_storage, 1):
            writer.writerow({
                'Observation': i,
                'Hand': entry['Hand'],
                'Last Double or Nothing': entry['Last Double or Nothing'],
                'Success/Failure': entry['Success/Failure'],
                'Cumulative Winnings (b)': entry['Cumulative Winnings (b)'] if 'Cumulative Winnings (b)' in entry else 0  # This line is changed to provide a default of 0
            })
    print(f"Data summarized and saved to {filename} in the current directory.")


def signal_handler(sig, frame, num_rounds):
    print('Exiting the program...')
    summarize_data(num_rounds)
    sys.exit(0)

def main():
    global num_rounds  # Declare global variable for number of rounds to evaluate
    try:
        num_rounds = int(input("Enter the number of double or nothing rounds to evaluate: "))
        signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, num_rounds))
        
        while True:
            hand_input = input("Enter the hand (single letter or 0 if first hand was lost): ").lower()
            if hand_input in ["exit", "stop", "quit", "end", "e", "s", "q"]:
                raise EOFError
            if hand_input not in hand_mapping and hand_input != "0":
                print("Invalid hand. Please try again.")
                continue
            if hand_input == "0":
                data_storage.append({
                    'Hand': 'First hand lost',
                    'Last Double or Nothing': '0',
                    'Success/Failure': '0',
                    'Cumulative Winnings (b)': -1 * initial_bet_scalar  # Assuming the player loses their initial bet when they lose the first hand
                })
                print("First hand lost, no further data required for this round.")
                continue  # Skip the rest of the loop and wait for next input


            last_double_or_nothing = None
            while last_double_or_nothing is None:
                try:
                    last_double_or_nothing = int(input(f"Enter the last double or nothing round number (0-{num_rounds}): "))
                    if last_double_or_nothing < 0 or last_double_or_nothing > num_rounds:
                        raise ValueError
                except ValueError:
                    print(f"Invalid input. Please enter a number between 0 and {num_rounds}.")
            
            success = 1 if last_double_or_nothing == num_rounds else 0
            hand_bet_value = hand_bet_multipliers[hand_input]
            cumulative_winnings = (last_double_or_nothing * hand_bet_value * success) - (1 - success)
            cumulative_winnings *= initial_bet_scalar

            data_storage.append({
                'Hand': hand_mapping[hand_input],
                'Last Double or Nothing': last_double_or_nothing,
                'Success/Failure': success,
                'Cumulative Winnings (b)': cumulative_winnings,
            })
            print(f"Data added: {hand_mapping[hand_input]}, {last_double_or_nothing}, {success}")
        
    except EOFError:
        end(None, None, num_rounds)

def end(sig, frame, num_rounds):
    """Handler for ending the program and summarizing data."""
    print('Exiting the program...')
    summarize_data(num_rounds)
    sys.exit(0)

if __name__ == '__main__':
    main()