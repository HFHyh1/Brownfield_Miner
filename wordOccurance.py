def count_word_occurrences_with_locations(input_file_path, output_file_path):
    # Open the input text file
    with open(input_file_path, 'r') as file:
        # Read the content of the file
        content = file.read()

        # Split the content by space and new line
        words = content.split()

        # Create a dictionary to store word occurrences and their locations
        word_data = {}
        for index, word in enumerate(words):
            word = word.lower()  # Convert to lowercase to treat words case-insensitively
            if word in word_data:
                word_data[word]['count'] += 1
                word_data[word]['locations'].append(index)
            else:
                word_data[word] = {'count': 1, 'locations': [index]}

    # Convert the word_data dictionary to the desired output format
    result_data = [{"word": word, "count": data['count'], "locations": data['locations']} for word, data in word_data.items()]

    # Write the results to the output text file
    with open(output_file_path, 'w') as output_file:
        for result in result_data:
            output_file.write(f"{result['word']}: {result['count']}, {result['locations']}\n")

# Example usage:
# input_file_path = 'input.txt'  # Replace with your actual input file path
# output_file_path = 'output.txt'  # Replace with your desired output file path
# count_word_occurrences_with_locations(input_file_path, output_file_path)
