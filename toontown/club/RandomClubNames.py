"""
The file dedicated to club name randomization.
"""
import random

__firstName = (
    'Friendly',
    'Cardboard',
    'Fortunate',
    'Kind',
    'Dream',
    'Toon',
    'Friendship',
    'Flower',
    'Positive',
    'Star',
    'Magical',
    'Lucky',
    'Mighty',
    'Agreeable',
    'Determined',
    'Helpful',
    'Likeable',
    'Funny',
    'Patient',
    'Perfect',
    'Tolerant',
    'Silly',
)

__lastName = (
    'Club',
    'Crew',
    'Legion',
    'Squad',
    'League',
    'Company',
    'Guild',
    'Council',
    'Team',
    'Friends',
    'Bureau',
    'Force',
    'Vibes',
    'Allies',
    'Platinum',
    'Fiesta',
    'Two',
)


def getRandomClubName():
    """Generates a random club name."""
    hasFirstName = True
    hasLastName = True

    fullName = ''

    # Pick a first name.
    if hasFirstName:
        fullName = fullName + random.choice(__firstName)

    # Pick a last name.
    if hasLastName:
        fullName = fullName + ' ' + random.choice(__lastName)

    # Return the name.
    return fullName
