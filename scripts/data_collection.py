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
initial_bet_scalar = 1  # 1 by default, can be changed if needed


# Data storage structure
data_storage = []

# Function to check the last observation number in the CSV
def get_last_observation(filename):
    """Function to get the last observation number in the CSV file."""
    last_observation = 0
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            reader = csv.DictReader(file)
            last_observation = sum(1 for row in reader) - 1 # Exclude header
    return last_observation

def summarize_data(num_rounds, start_observation):
    """Function to summarize data and write to a single CSV file."""
    filename = f'frequencies_{num_rounds}.csv'
    header_written = os.path.exists(filename)
    with open(filename, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Observation', 'Hand', 'Last Won Round', 'Success/Failure', 'Win in b'])
        if not header_written:
            writer.writeheader()
        #loop to begin writing data
        for i, entry in enumerate(data_storage, start_observation):
            writer.writerow({
                'Observation': i,
                'Hand': entry['Hand'],
                'Last Won Round': entry['Last Won Round'],
                'Success/Failure': entry['Success/Failure'],
                'Win in b': entry['Win in b'] if 'Win in b' in entry else 0  # Ensure this line matches the fieldname
            })
    print(f"Data summarized and saved to {filename} in the current directory.")


def signal_handler(sig, frame, num_rounds, start_observation):
    print('Exiting the program...')
    summarize_data(num_rounds, start_observation)
    sys.exit(0)

def main():
    global num_rounds  # Declare global variable for number of rounds to evaluate
    num_rounds = int(input("Enter the number of double or nothing rounds to evaluate: "))
    filename = f'frequencies_{num_rounds}.csv'
    start_observation = get_last_observation(filename) + 1
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, num_rounds, start_observation))
    try:
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
                    'Last Won Round': '0',
                    'Success/Failure': '0',
                    'Win in b': -1 * initial_bet_scalar  # Assuming the player loses their initial bet when they lose the first hand
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
            win_in_b = (last_double_or_nothing * hand_bet_value * success) - (1 - success)
            win_in_b *= initial_bet_scalar

            data_storage.append({
                'Hand': hand_mapping[hand_input],
                'Last Won Round': last_double_or_nothing,
                'Success/Failure': success,
                'win in b': win_in_b,
            })
            print(f"Data added: {hand_mapping[hand_input]}, {last_double_or_nothing}, {success}")
    except EOFError:
        summarize_data(num_rounds, start_observation)

if __name__ == '__main__':
    main()