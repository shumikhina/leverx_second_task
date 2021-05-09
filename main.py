import functools
import itertools
import re


@functools.total_ordering
class Version:
    def __init__(self, version):
        self.version = version

    def __eq__(self, other):
        current_version_list = self._get_parsed_and_repaired_version(self.version)
        other_version_list = self._get_parsed_and_repaired_version(other.version)
        return [self._enhance_periods_word(current) for current in current_version_list] == \
               [self._enhance_periods_word(other) for other in other_version_list]

    def __lt__(self, other):
        current_version_list = self._get_parsed_and_repaired_version(self.version)
        other_version_list = self._get_parsed_and_repaired_version(other.version)
        for v1_period, v2_period in itertools.zip_longest(current_version_list, other_version_list):
            if v1_period is None:
                return v2_period.isdigit()
            if v2_period is None:
                return v1_period.isalpha()
            if v1_period.isdigit() and v1_period.isdigit():
                if v1_period != v2_period:
                    return v1_period < v2_period
            if v2_period.isdigit() and v1_period.isalpha():
                return True
            if v1_period.isdigit() and v2_period.isalpha():
                return False
            if v1_period.isalpha() and v2_period.isalpha():
                if not self._words_eq(v1_period, v2_period):
                    return self._word_lt(v1_period, v2_period)

    def _get_parsed_and_repaired_version(self, version):
        return self._restore_punctuation_in_number_and_letter_union(version).replace('-', '.').split(sep='.')

    @staticmethod
    def _enhance_periods_word(word):
        words_enhancement_map = {'a': 'alpha', 'b': 'beta'}
        return words_enhancement_map.get(word, word)

    def _words_eq(self, word_1, word_2):
        word_1 = self._enhance_periods_word(word_1)
        word_2 = self._enhance_periods_word(word_2)
        return word_1 == word_2

    def _word_lt(self, word_1, word_2):
        word_1 = self._enhance_periods_word(word_1)
        word_2 = self._enhance_periods_word(word_2)
        return word_1 < word_2

    @staticmethod
    def _restore_punctuation_in_number_and_letter_union(version):
        match = re.search(r'\d[a-z]', version)
        while match is not None:
            insert_position = match.regs[0][0]
            version = f'{version[:insert_position+1]}-{version[insert_position+1:]}'
            match = re.search(r'\d[a-z]', version)
        return version


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for version_1, version_2 in to_test:
        assert Version(version_1) < Version(version_2), "le failed"
        assert Version(version_2) > Version(version_1), f"ge failed {version_1}"
        assert Version(version_2) != Version(version_1), "neq failed"


if __name__ == "__main__":
    main()
