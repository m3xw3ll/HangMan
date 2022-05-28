from collections import Counter
import os

HANGMEN = ['''
  +---+
  |   |
      |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', '''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========''']


def read_vocabuary_file(path):
    """
    Function to read the vocabulary file
    :param path: Path to file
    :return: List with words
    """
    words = []
    with open(path) as file:
        for line in file:
            words.append(line.rstrip().lower())
    return words


def get_char_frequency(words):
    """
    Function to get the frequency of each character in the word list
    :param words: Word list
    :return: Frequency dict
    """
    return Counter(letter for w in words for letter in w)


def filter_by_word_size(words, size):
    """
    Function to get possible words with same length
    :param word_length: The length of the user word
    :param words: List of words
    :return: Possible words with equal length
    """
    return [w for w in words if len(w) == size]


def filter_by_excluded_letter(words, letter):
    """
    Function to update the word list and remove words where asked character is not in
    :param character: The character for that the program asked
    :param words: Current word list
    :return: Updated word list
    """
    return [w for w in words if letter not in w]


def filter_by_known_letter(words, letter, indices):
    """
    Function to update the word list with potential words
    :param character: The character for that the program asked
    :param indices: The indicies where the characters are
    :param words: Current word list
    :return: Updated word list
    """
    return [
        w
        for w in words
        if all(w[i] == letter for i in indices)
    ]


def print_screen(masked_word, wrong_guesses, message=None):
    """
    Helper function to print the current game state
    :param masked_word: The masked user word
    :param wrong_guesses: The wrong guesses count
    :param message: Game Over message if masked word was not found
    :return: None
    """
    clear_screen()
    print(HANGMEN[wrong_guesses])
    print(' '.join(masked_word))
    print(' '.join(map(str, range(len(masked_word)))))
    if message:
        print(message)


def clear_screen():
    """
    Helper function to clear terminal
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def most_common_letter(words, masked_word):
    """
    Function to find the most common character
    :param words: The word list
    :param masked_word: The masked Word
    :return: Most common letter
    """
    counts = get_char_frequency(words)
    for c in masked_word:
        counts.pop(c, None)
    return counts.most_common()[0][0]


def get_input(prompt, convert = None, validate = None, choices = None):
    """
    Function to get valid user input
    :param prompt: Prompt text
    :param convert: Control parameter if input has to be converted
    :param validate: Control parameter to validate user input
    :param choices: Possible choices a user can make, e.g. masked_word in word list
    :return: None
    """
    # Prepare the conversion and validation functions.
    convert = convert or (lambda x: x)
    if choices:
        validate = lambda x: x in choices
    elif validate is None:
        validate = lambda x: True

    # Get user reply: convert and return if valid.
    while True:
        reply = input(prompt + ': ')
        try:
            value = convert(reply)
            if validate(value):
                return value
        except Exception:
            pass
        prompt = 'Invalid input. Try again'


def parse_ints(reply):
    """
    Helper function to get the user input for character indices
    :param reply: User input
    :return: Map with character indices
    """
    return sorted(map(int, reply.split()))


def play_hangman():
    # Select word from vocabulary.
    words = read_vocabuary_file('vocabulary.txt')
    word = get_input(
        'Please enter a word which is in the vocabulary',
        choices = words,
    )

    # Filter down to words of that size.
    size = len(word)
    words = filter_by_word_size(words, size)
    masked_word = ['_'] * size

    # Play until solved or failed.
    game_over = None
    wrong_guesses = 0
    print_screen(masked_word, wrong_guesses)
    while not game_over:
        # Guess the most common letter.
        letter = most_common_letter(words, masked_word)

        # Force the poor human to enter the letter locations, if any.
        expected_indices = [i for i, c in enumerate(word) if c == letter]
        indices = get_input(
            f'If the word contains [{letter}], enter its indices. Else hit ENTER',
            convert = parse_ints,
            choices = [expected_indices],
        )

        # Filter words based on reply.
        if indices:
            words = filter_by_known_letter(words, letter, indices)
            for i in indices:
                masked_word[i] = letter
        else:
            words = filter_by_excluded_letter(words, letter)
            wrong_guesses += 1

        # Check for game over.
        if wrong_guesses >= len(HANGMEN) - 1:
            game_over = 'GAME OVER!'
        elif len(words) == 1:
            game_over = 'I found your word!'
            masked_word = words[0]

        # Display.
        print_screen(masked_word, wrong_guesses, message = game_over)


if __name__ == '__main__':
    play_hangman()
