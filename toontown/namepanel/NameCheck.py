"""
Avatar name-checking routines.

Used in Make-a-Toon and Restoration Station for type-a-name inputs.
"""
from __future__ import annotations
import string

from . import NameCheckLocalizer, NameCheckRules as NCR


def miscBadCharacters(name: str) -> str | None:
    for char in name:
        if not NCR.isValidCharacter(char) and char not in string.digits:
            return NameCheckLocalizer.NCBadCharacter % char
    return None


def repeatedChars(name: str) -> str | None:
    count = 1
    lastChar = None
    i = 0
    while i < len(name):
        char = name[i]
        i += 1
        if char == lastChar:
            # character is repeating
            count += 1
        else:
            count = 1
        lastChar = char
        if count > 2:
            return NameCheckLocalizer.NCRepeatedChar % char
    return None


def checkName(name: str) -> str | None:
    """
    runs a set of misc check functions; they are also given unicode strings

    :param name: should be an ASCII string

    :return: None if name is OK, error string if name is not OK
    """

    # Boolean check paired with its fail message
    checks = (
        (NCR.isNotAllCaps, NameCheckLocalizer.NCAllCaps),
        (NCR.noMonoLetters, NameCheckLocalizer.NCSingleLetter),
        (NCR.isOnlyPrintableChars, NameCheckLocalizer.NCPrintableChar),
        (NCR.hasNoDigits, NameCheckLocalizer.NCNoDigits),
        (NCR.noMoreThanOneSpaceBetweenWords, NameCheckLocalizer.NCSpaces),
        (NCR.longEnough, NameCheckLocalizer.NCTooShort),
        (NCR.notTooLong, NameCheckLocalizer.NCTooLong),
        (NCR.nameNotEmpty, NameCheckLocalizer.NCTooShort),
        (NCR.hasLetters, NameCheckLocalizer.NCNeedLetters),
        (NCR.hasVowels, NameCheckLocalizer.NCNeedVowels),
        (NCR.usingDashesProperly, NameCheckLocalizer.NCDashUsage),
        (NCR.usingCommasProperly, NameCheckLocalizer.NCCommaUsage),
        (NCR.usingPeriodsProperly, NameCheckLocalizer.NCPeriodUsage),
        (NCR.usingApostrophesProperly, NameCheckLocalizer.NCApostrophes),
        (NCR.notTooManyWords, NameCheckLocalizer.NCTooManyWords),
        (NCR.isNotMixedCase, NameCheckLocalizer.NCMixedCase),
        (NCR.isNotNpcName, NameCheckLocalizer.NCNpcName)
    )

    # Boolean checks that should be run on the reversed name string
    symmetricChecks = []

    # Checks that return a dynamic error message
    dynamicChecks = (
        miscBadCharacters,
        repeatedChars,
    )

    # run through all boolean checks
    for [check, error_msg] in checks:
        success = check(name[:])
        if success and check in symmetricChecks:
            # check it backwards.
            bName = name[::-1]
            success = check(bName)
        if not success:
            return error_msg

    # run through all dynamic error message checks
    for dynamicCheck in dynamicChecks:
        problem = dynamicCheck(name[:])
        if problem:
            return problem

    return None
