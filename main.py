import requests
import time

start_height = 1867020  # Initial block height
end_height = 1867075  # Final block height (inclusive)
batch_size = 10  # Number of blocks to process in each batch
pause_duration = 0.2  # Pause duration between batches in seconds


def get_block_time(block_height):
    """Gets the block time in UNIX format."""
    try:
        response = requests.get(f'https://explorer-blockbook.syscoin.org//api/v2/block/{block_height}')
        response.raise_for_status()
        data = response.json()
        return data['time']
    except requests.exceptions.RequestException as e:
        print(f'Error in request for block {block_height}: {e}')
        return None


def calculate_block_time_differences(start_height, end_height):
    """Calculates the time difference between consecutive blocks in a range, processing in batches."""
    previous_time = None
    differences = []

    current_height = start_height
    while current_height < end_height:
        # Process blocks in batches of batch_size
        batch_end = min(current_height + batch_size, end_height + 1)

        batch_differences = []
        batch_previous_time = None

        for height in range(current_height, batch_end):
            current_time = get_block_time(height)
            if batch_previous_time is not None:
                # Calculate the difference in seconds
                time_diff = current_time - batch_previous_time
                batch_differences.append(time_diff)
            batch_previous_time = current_time

        differences.extend(batch_differences)

        # Move to the next batch
        current_height = batch_end

        # Pause between batches
        print(f'Pausing for {pause_duration} seconds...')
        time.sleep(pause_duration)

    return differences


def analyze_differences(differences):
    """Analyzes the differences to obtain specific statistics."""
    if not differences:
        return {
            'average': None,
            'count_above_2_5_minutes': 0,
            'count_below_2_5_minutes': 0,
            'count_above_2_5_minutes_individual': 0
        }

    average_diff = sum(differences) / len(differences)
    count_above_2_5_minutes = sum(1 for diff in differences if diff > 150)
    count_below_2_5_minutes = sum(1 for diff in differences if diff < 150)

    return {
        'average': average_diff,
        'count_above_2_5_minutes': count_above_2_5_minutes,
        'count_below_2_5_minutes': count_below_2_5_minutes,
    }


def main():
    # Get time differences between blocks
    differences = calculate_block_time_differences(start_height, end_height)

    # Analyze differences
    analysis = analyze_differences(differences)

    # Print results
    for i, diff in enumerate(differences):
        print(
            f'Time difference between block {start_height + i} and block {start_height + i + 1}: {diff} seconds')

    if analysis['average'] is not None:
        print(f'\nAverage duration between blocks: {analysis["average"]:.2f} seconds')
    print(f'Number of time intervals between blocks longer than 2.5 minutes: {analysis["count_above_2_5_minutes"]}')
    print(f'Number of time intervals between blocks shorter than 2.5 minutes: {analysis["count_below_2_5_minutes"]}')


if __name__ == "__main__":
    main()

