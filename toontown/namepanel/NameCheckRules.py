"""
Pure avatar name-checking routines and utility that strictly return
booleans or static strings respectively.

Used by NameChecks.checkName in this module.
"""

import string
from typing import List

# Altis's NPC toon system doesn't have Clash's NPCToonRegistry, so there's no
# equivalent name list to pull from here. Names are simply never excluded for
# colliding with an NPC's name.
NPCToonNames = {}

validAsciiChars = set(".,'- " + string.ascii_letters)


def filterString(str_: str, filter_: str) -> str:
    """
    :returns: a version of str_ that only contains characters in filter_
    """
    result = ''
    for char in str_:
        if char in filter_:
            result = result + char

    return result


def justLetters(str_: str) -> str:
    letters = ''
    for c in str_:
        if c.isalpha():
            letters = letters + c

    return letters


def justUpper(str_: str) -> str:
    upperCaseLetters = ''
    for c in str_:
        if c.upper() != c.lower():
            if c == c.upper():
                upperCaseLetters = upperCaseLetters + c

    return upperCaseLetters


def wordList(str_: str) -> List[str]:
    """ just like split, but treats dashes as whitespace """
    words = str_.split()
    result = []
    for word in words:
        subWords = word.split('-')
        for sw in subWords:
            if sw:
                result.append(sw)
    return result


#
# Rules
#

def isNotNpcName(name: str) -> bool:
    for npcToonName in NPCToonNames.values():
        if name.lower() == npcToonName.lower() and (' ' in name):
            return False
    return True


def longEnough(name: str) -> bool:
    return len(name) >= 2


def notTooLong(name: str) -> bool:
    return len(name) <= 64


def nameNotEmpty(name: str) -> bool:
    return name.strip() != ''


def isOnlyPrintableChars(name: str) -> bool:
    for char in name:
        # If it is an extended character, we cannot test it for printability here
        # (but presumably it is some printable character.)
        if ord(char) < 128 and char not in string.printable:
            return False
    return True


def noMoreThanOneSpaceBetweenWords(name: str) -> bool:
    return '  ' not in name


def isValidCharacter(c: str) -> bool:
    return c in validAsciiChars


def hasNoDigits(name: str) -> bool:
    for char in name:
        if not isValidCharacter(char):
            if char in string.digits:
                return False
    return True


def hasLetters(name: str) -> bool:
    # ,...,
    words = wordList(name)
    for word in words:
        letters = justLetters(word)
        if len(letters) == 0:
            return False
    return True


def hasVowels(name: str) -> bool:
    # ndssmvwls
    def hasVowelsPerWord(word: str) -> bool:
        if '.' in word:
            # if there's a period, assume it's an abbreviation
            return True

        # Check if there's an extended character; if so, it might be a vowel.
        for char in word:
            if ord(char) >= 128:
                return True

        letters = filterString(word, string.ascii_letters)
        # things like 'MD' are ok without periods
        if len(letters) > 2:
            vowels = filterString(letters, 'aeiouyAEIOUY')
            if len(vowels) == 0:
                return False
        return True

    for word in wordList(name):
        if hasVowelsPerWord(word) is False:
            return False
    return True


def usingDashesProperly(name: str) -> bool:
    """Checks for proper dash usage."""
    def validDash(index: int, name: str = name) -> bool:
        # if the dash is at the beginning or the end, fail
        if index == 0 or i == len(name) - 1:
            return False
        if not name[i - 1].isalpha():
            return False
        if not name[i + 1].isalpha():
            return False
        return True

    # validate dashes
    for i in range(len(name)):
        char = name[i]
        if char == '-':
            if not validDash(i):
                return False
    return True


def usingCommasProperly(name: str) -> bool:
    """Checks for proper comma usage."""
    def validComma(index: int, name: str = name):
        # if the comma is at the beginning or the end, fail
        if index == 0 or i == len(name) - 1:
            return False
        # comma must follow a word and be followed by a space
        if name[i - 1].isspace():
            return False
        if not name[i + 1].isspace():
            return False
        return True

    # validate commas
    for i in range(len(name)):
        char = name[i]
        if char == ',':
            if not validComma(i):
                return False
    return True


def usingPeriodsProperly(name: str) -> bool:
    """
    periods are allowed at the end of words, or in two-letter words, like 'J.T.'
    """
    words = wordList(name)
    for word in words:
        # strip off any trailing commas
        if word[-1] == ',':
            word = word[:-1]

        # no periods skip
        numPeriods = word.count('.')
        if not numPeriods:
            continue

        # word must end in '.'
        if word[-1] != '.':
            return False

        # max periods is 2
        if numPeriods > 2:
            return False

        if numPeriods == 2:
            # 2nd and 4th characters should be periods
            if not (word[1] == '.' and word[3] == '.'):
                return False

    return True


def usingApostrophesProperly(name: str) -> bool:
    words = wordList(name)
    for word in words:
        numApos = word.count("'")
        if numApos > 2:
            return False
    numApos = name.count("'")
    if numApos > 3:
        return False
    return True


def notTooManyWords(name: str) -> bool:
    return len(wordList(name)) <= 4


def isNotMixedCase(name: str) -> bool:
    # MiCkeY MoUsE
    words = wordList(name)
    for word in words:
        if len(word) > 2:
            capitals = justUpper(word)
            if len(capitals) > 2:
                return False
    return True


def isNotAllCaps(name: str) -> bool:
    # MICKEY MOUSE
    letters = justLetters(name)
    # J.T. -> OK
    return len(letters) <= 2 or letters != letters.upper()


def noMonoLetters(name: str) -> bool:
    # eeeeeeeee
    def noMonoLettersPerWord(word: str) -> bool:
        word = word
        letters = justLetters(word)
        if len(letters) > 2:
            # make case-insensitive
            letters = letters.lower()
            filtered = filterString(letters, letters[0])
            if filtered == letters:
                return False

    for word in wordList(name):
        if noMonoLettersPerWord(word) is False:
            return False
    return True
