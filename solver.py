from dataclasses import dataclass, field
from typing import List
import exrex
import itertools

NUM_OF_GUESSES = 6
NUM_OF_LETTERS = 5


class ColorEnum:
    gray = "gray"
    orange = "orange"
    green = "green"


@dataclass
class LetterData:
    letter: str
    color: str


@dataclass
class PositionData:
    letters: [LetterData] = field(default_factory=list)

    def get_orange_letters(self) -> List[str]:
        return [l.letter for l in self.letters if l.color == ColorEnum.orange]

    def get_green_letter(self) -> str:
        greens = [l.letter for l in self.letters if l.color == ColorEnum.green]
        if len(greens) == 0:
            return ""
        return greens[0]


class BaseSolver:
    def __init__(self):
        self.positions = [PositionData() for a in range(NUM_OF_LETTERS)]
        self.gray_letters = []
        self.green_letters = []
        self.orange_letters = []
        self.num_of_guesses = 0

    def is_word_in_language(self, word: str) -> bool:
        raise NotImplementedError()

    def get_best_guesses(self):
        raise NotImplementedError()

    def get_all_letters_in_language(self) -> List[str]:
        raise NotImplementedError()

    def solve(self):
        for i in range(NUM_OF_GUESSES):
            found_at_least_one_word = False
            possible_words = self.get_possible_words()
            print(f"all possible words: {possible_words}")
            for word in possible_words:
                print("Please enter the word '{}'".format(word))
                colors = input(f"Please type in the colors for the word '{word}': (g for green, o for orange, r for gray) ")
                if colors:
                    self.add_guess(word, parse_color_codes(colors))
                    found_at_least_one_word = True
                    break
            if not found_at_least_one_word:
                print("No words found")
                break

    def initial_guess(self):
        best_guesses = self.get_best_guesses()
        if self.num_of_guesses == 0:
            return best_guesses[0]
        if self.num_of_guesses == 1:
            return best_guesses[1]
        return None

    def is_word_in_constraints(self, word: str) -> bool:
        for letter in self.orange_letters:
            if letter not in word:
                return False
        for letter in self.green_letters:
            if letter not in word:
                return False
        return True

    def get_possible_words(self) -> List[str]:
        initial_guess = self.initial_guess()
        if initial_guess:
            return [initial_guess]
        possible_letters = set(self.get_all_letters_in_language())
        possible_letters -= set(self.gray_letters)
        regex_phrase = ""
        for i in range(NUM_OF_LETTERS):
            position_data = self.positions[i]
            green_letter = position_data.get_green_letter()
            if green_letter:
                regex_phrase += f"({green_letter})"
            else:
                possible_for_position = possible_letters - set(position_data.get_orange_letters())
                all_options = "|".join(possible_for_position)
                regex_phrase += f"({all_options})"
        res = []
        for word in exrex.generate(regex_phrase):
            if self.is_word_in_constraints(word) and self.is_word_in_language(word):
                res.append(word)

        return self.rank_words(res)

    def rank_words(self, words):
        # rank by number of unique letters
        words = sorted(words, key=lambda w: len(set(w)), reverse=True)
        return words

    def add_guess(self, guess: str, colors: List[str]):
        for ind, position in enumerate(self.positions):
            position.letters.append(LetterData(guess[ind], colors[ind]))
        self.recalc_letters_agg()
        self.num_of_guesses += 1

    def recalc_letters_agg(self):
        self.gray_letters = []
        self.green_letters = []
        self.orange_letters = []
        for position in self.positions:
            for letter in position.letters:
                if letter.color == ColorEnum.gray:
                    self.gray_letters.append(letter.letter)
                elif letter.color == ColorEnum.green:
                    self.green_letters.append(letter.letter)
                elif letter.color == ColorEnum.orange:
                    self.orange_letters.append(letter.letter)
        self.green_letters = set(self.green_letters)
        self.orange_letters = set(self.orange_letters) - self.green_letters
        self.gray_letters = set(self.gray_letters) - self.green_letters - self.orange_letters


class EnglishSolver(BaseSolver):

    def __init__(self):
        self.all_words = set(open("english.txt").read().splitlines())
        super().__init__()

    def get_best_guesses(self):
        return ["those", "drain", ]

    def get_all_letters_in_language(self) -> List[str]:
        return ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

    def is_word_in_language(self, word: str) -> bool:
        return word in self.all_words

    def find_optimal_initial_guesses(self):
        freq_letters = [
            "e", "t", "a", "o", "i", "n", "s", "h", "r", "d"
        ]
        prem = [''.join(p) for p in itertools.permutations("".join(freq_letters))]
        for a in prem:
            word1 = a[:5]
            word2 = a[5:]
            if self.is_word_in_language(word1) and self.is_word_in_language(word2):
                print(f"{word1} {word2}")


class HebrewSolver(BaseSolver):
    def __init__(self):
        self.all_words = set(open("hebrew.txt").read().splitlines())
        super().__init__()

    def get_all_letters_in_language(self) -> List[str]:
        return ["א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ", "ק", "ר", "ש", "ת"]

    def is_word_in_language(self, word: str) -> bool:
        return word in self.all_words

    def get_best_guesses(self):
        return [
            "יובהר",
            "אשתלם"
        ]

    def find_optimal_initial_guesses(self):
        freq_letters = [
            "י",
            "ו",
            "ה",
            "ל",
            "א",
            "ת",
            "ר",
            "ב",
            "ש",
            "מ",
        ]
        prem = [''.join(p) for p in itertools.permutations("".join(freq_letters))]
        for a in prem:
            word1 = a[:5]
            word2 = a[5:]
            if self.is_word_in_language(word1) and self.is_word_in_language(word2):
                print(f"{word1} {word2}")


def parse_color_codes(color_codes: str) -> List[str]:
    res = []
    for color in color_codes:
        if color == "g":
            res.append(ColorEnum.green)
        elif color == "o":
            res.append(ColorEnum.orange)
        elif color == "r":
            res.append(ColorEnum.gray)
    return res


if __name__ == "__main__":
    solver = EnglishSolver()
    solver.solve()
