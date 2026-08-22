"""
This module is used for Clash-specific text-modifying utility functions.
"""
import datetime
import math

from direct.gui.DirectLabel import DirectLabel

from toontown.toonbase import TTLocalizer


def plural(value):
    return "" if value == 1 else "s"


def makeCommaSeparatedItems(items, useAnd=True, oxfordComma=False):
    """
    Makes a list of comma separated items.
    Does modify the content of the list.
    """
    if not items:
        return ''

    if len(items) == 1:
        return items[0]

    if len(items) >= 2 and useAnd:
        items[-1] = 'and ' + items[-1]

    if not oxfordComma:
        # Skip the oxford comma.
        msg = ', '.join(items[:-1]) + ' ' + items[-1]
    else:
        # Yummm commas
        msg = ', '.join(items)

    return msg


def getTextScaleAfterLength(text, scaleAfterLength, modifier=0.05, baseScale=1.0):
    if len(text) > scaleAfterLength:
        return baseScale - ((len(text) - scaleAfterLength) * modifier)
    else:
        return baseScale


def capTextScaleToWidth(label, maxWidth):
    """Caps a label/frame's text scale to the given width"""
    text0 = label.component('text0')
    bMin, bMax = text0.getTightBounds()
    totalWidth = abs(bMin[0]) + abs(bMax[0])
    if totalWidth > maxWidth:
        xScale = maxWidth / totalWidth
        currTextScale = label['text_scale']
        label['text_scale'] = (currTextScale[0] * xScale, currTextScale[1] * xScale)


def capTextToLineCount(label, lines=2):
    iterations = 0
    while label.component('text0').textNode.getNumRows() > lines:
        currTextScale = label['text_scale']
        label['text_scale'] = (currTextScale[0] * 0.97, currTextScale[1] * 0.97)
        label['text_wordwrap'] = label['text_wordwrap'] / 0.97

        # break early if this operation takes too long
        iterations += 1
        if iterations > 60:
            break


def fitLabelTextToBounds(maxWidth, maxHeight, label, textNodeName, maxLines=None, maxScale=None, minScaleIncreasePerLine=1.1, keepTopOfTextAligned=False):
    """
    NOTE: Do NOT use newlines (\\n) with this function. It will break.
    """

    textNode = label.component(textNodeName).textNode

    # If we have an empty string, return. This avoids divide-by-zero errors.
    if textNode.getText() == '':
        return

    # Save original scale
    originalScale = label['text_scale']

    def getFrameToTextRatio():
        return textNode.getWidth() / label.getWidth()

    def getProperWordwrap():
        return math.ceil(maxWidth * getFrameToTextRatio())

    def fitTextToWidth():
        label['text_scale'] = label['text_scale'][0] * (maxWidth / label.getWidth())
        if maxScale is not None and label['text_scale'][0] > maxScale:
            label['text_scale'] = maxScale
        label.resetFrameSize()

    def fitTextToHeight():
        label['text_scale'] = label['text_scale'][0] * (maxHeight / label.getHeight())
        if maxScale is not None and label['text_scale'][0] > maxScale:
            label['text_scale'] = maxScale
        label.resetFrameSize()

    def fitTextToBounds():
        fitTextToWidth()
        if label.getHeight() > maxHeight:
            fitTextToHeight()

    # Start by putting all the text on one line and scaling that to fit
    label['text_wordwrap'] = None
    label.resetFrameSize()
    fitTextToBounds()

    # Get some starting values
    label['text_wordwrap'] = getProperWordwrap()
    startingWordwrap = label['text_wordwrap']
    previousTextScale = label['text_scale'][0]
    previousWordwrap = label['text_wordwrap']
    numberOfLines = 1

    # Keep adding more lines as long as the text scale is increasing
    while (previousTextScale < label['text_scale'][0] and (label['text_scale'][0] / previousTextScale) >= minScaleIncreasePerLine) or numberOfLines == 1:
        previousTextScale = label['text_scale'][0]
        previousWordwrap = label['text_wordwrap']
        if numberOfLines == maxLines:
            break
        numberOfLines += 1
        label['text_wordwrap'] = startingWordwrap / numberOfLines
        # Increase wordwrap to adjust to the correct number of lines as needed
        while textNode.getNumRows() > numberOfLines:
            label['text_wordwrap'] = label['text_wordwrap'] + 0.5
        label.resetFrameSize()
        fitTextToBounds()

    # Apply changes and adjust label Z
    label['text_scale'] = previousTextScale
    label['text_wordwrap'] = previousWordwrap

    if keepTopOfTextAligned:
        adjustZAfterTextScaleChange(label, originalScale)


def wordwrapWithVerticalCentering(label, wordwrapValue, text=None):
    if text is None:
        text = label['text']
    originalText = text
    noBreakText = text.replace('\n', '')
    label.setText(noBreakText)
    label['text_wordwrap'] = None
    label.resetFrameSize()
    originalHeight = label.getHeight()
    label.setText(originalText)
    label['text_wordwrap'] = wordwrapValue
    label.resetFrameSize()
    newHeight = label.getHeight()
    label.setZ(label.getZ() + (newHeight - originalHeight) / 2.0)


def adjustZAfterTextScaleChange(label, originalScale, text=None):
    if text is None:
        text = label['text']
    originalText = text
    originalWordWrap = label['text_wordwrap']
    newScale = label['text_scale']

    noBreakText = text.replace('\n', '')
    label.setText(noBreakText)
    label['text_wordwrap'] = None
    label['text_scale'] = originalScale
    label.resetFrameSize()
    originalHeight = label.getHeight()
    label['text_scale'] = newScale
    label.resetFrameSize()
    newHeight = label.getHeight()
    label.setText(originalText)
    label['text_wordwrap'] = originalWordWrap
    label.resetFrameSize()
    label.setZ(label.getZ() + (originalHeight - newHeight) / 2.0)


def splitTextByWordwrap(text, wordwrapValue):
    """
    Given a string of text, returns a list of strings with the proper
    linebreaks implied per index.
    :param text: The text to try to split.
    :param wordwrapValue: The value of wordwrap to attempt splitting by.
    :return: A list of strings, split at where the wordwrap would split.
    """
    retList = []
    label = DirectLabel(parent=base.aspect2d, text=text, text_wordwrap=wordwrapValue)
    textNode = label.component("text0").textNode

    # Begin the terrible, terrible space splitting algorithm.
    label.setText('')
    current_string = ''
    last_space_index = None
    last_space_offset = 0
    activeTextProperties = []
    fillingTextProperty = ''
    for character in text:
        # So here's the plan:
        # We operate over the entire line of string in the text,
        # appending each character. We keep up with spaces being added
        # by referencing their index.
        # We check the label's height every single character until it goes past line 1.
        # When it does:
        # - If we have a last_space_index defined, we cut the string off up to that spacebar,
        #   and resume the rest of our string from that space index, setting it back to None.
        # - If we do not have a last_space_index defined, then we force a new line at
        #   the character we are looking at, without thinking whatsoever.

        if character == '\2':
            # Our text property has ended.
            activeTextProperties.pop()

        if character == '\1' or fillingTextProperty:
            # We are processing a text property at this moment.
            fillingTextProperty += character
            if character == '\1' and len(fillingTextProperty) > 1:
                # Flip our fillingTextProperty flag.
                activeTextProperties.append(fillingTextProperty)
                current_string += fillingTextProperty
                fillingTextProperty = ''
            continue

        current_string = current_string + character
        label.setText(current_string)
        if character == ' ':
            last_space_index = len(current_string) - 1

        # See if our label height has increased.
        if textNode.getHeight() > 1:
            # Action depending on if we have a last_space_index defined.

            # If we have a text property active, append a delimiter to our string.
            if activeTextProperties:
                # Add delimiter.
                current_string = current_string + '\2'

            if last_space_index is not None:
                # Update our retlist and current string accordingly.
                retList.append(current_string[0:last_space_index])
                current_string = current_string[last_space_index + 1:]
            else:
                # Just force a newline here.
                retList.append(current_string[:-1])
                current_string = current_string[-1]

            if activeTextProperties:
                # Put a starter textProperty at the start of this string.
                current_string = ''.join(activeTextProperties) + current_string[:-1]  # get rid of tha \2 from the end i hate you

            # Reset our last space index.
            last_space_index = None

    # Add the rest of the string to our return list as well.
    if current_string:
        retList.append(current_string)

    # Cleanup and return.
    label.destroy()
    return retList


magnitudeCutoffs = {
    1E3:  (' thousand', 'k'),
    1E6:  (' million', 'm'),
    1E9:  (' billion', 'b'),
    1E12: (' trillion', 't'),
    1E15: (' quadrillion', 'qd'),
    1E18: (' quintillion', 'qt'),

    # Define an extrordinarily large value for use in the below algorithm
    1E300: (' big', ' big'),
}


def reduceNumberIntoString(num, short=False,
                           ignoreRedundant=False,
                           decimalPlaces=2):
    """
    Reduces a number into a suffix string.

    :param num: The number to compress.
    :param short: million vs. -m
    :param ignoreRedundant: 1.0k vs. 1k
    :param decimalPlaces: 1.57k vs. 1.6k
    """
    # Return early if the number is too small.
    if num < min(magnitudeCutoffs.keys()):
        return str(num)

    # Find the greatest cutoff.
    cutoffValues = tuple(magnitudeCutoffs.keys())

    for lowValue, highValue in zip(cutoffValues, cutoffValues[1:]):
        # Check if this number is in bounds.
        if lowValue <= num < highValue:
            # The number is in bounds, render it properly.
            # First, reduce the value.
            num = round(num / float(lowValue), decimalPlaces)

            # If we're ignoring redundant, drop the hanging .0.
            if ignoreRedundant:
                # Drop any and all hanging .0s if necessary.
                for i in range(decimalPlaces, 0, -1):
                    places = (i - 1) if i != 1 else 0
                    if num == round(num, places):
                        # The numbers are still the same when we drop the place, so we can drop safely.
                        num = round(num, places)
                    else:
                        # The numbers differ when we drop a place, so we cannot drop safely.
                        break

            # Figure out the suffix to use.
            suffixTuple = magnitudeCutoffs.get(lowValue)
            suffix = suffixTuple[0 if not short else 1]

            # Return our formatted string.
            return "%s%s" % (num, suffix)

    # This number is out of bounds -- just return normally.
    return str(num)


def formatNumberWithCommas(num):
    """Formats a number with commas."""
    return "{:,}".format(num)


def formatTimeRemainingIntoString(seconds, timesToShow=4, useAnd=False):
    # Formats a time remaining into a string.
    days = math.floor(seconds / 86400)
    hours = math.floor((seconds / 3600) % 24)
    minutes = math.floor((seconds / 60) % 60)
    seconds = math.floor(seconds % 60)
    retString = ''
    if days and timesToShow:
        retString += '%s day%s, ' % (days, "s" if days != 1 else "")
        timesToShow -= 1
    if hours and timesToShow:
        retString += '%s hour%s, ' % (hours, "s" if hours != 1 else "")
        timesToShow -= 1
    if minutes and timesToShow:
        retString += '%s minute%s, ' % (minutes, "s" if minutes != 1 else "")
        timesToShow -= 1
    if timesToShow:
        retString += '%s second%s, ' % (seconds, "s" if seconds != 1 else "")
        timesToShow -= 1
    if not useAnd:
        # Return just the string.
        return retString[:-2]
    else:
        # Change the last comma into an 'and'.
        retString = retString[:-2]
        if retString.find(','):
            # Lots of reversals to just change the last comma
            # Lol
            retString = ((retString[::-1]).replace(',', ' and'[::-1]))[::-1]
        return retString


def formatTimestampToAbsoluteTime(seconds, withTime=False):
    dt = datetime.datetime.fromtimestamp(seconds)
    month = TTLocalizer.Months.get(dt.month)
    day = dt.day
    ordinalSuffix = {
        1: 'st',
        2: 'nd',
        3: 'rd',
    }.get(day % 10, 'th')
    if day in (11, 12, 13):
        ordinalSuffix = 'th'
    year = dt.year
    if not withTime:
        return '%s %s%s, %s' % (month, day, ordinalSuffix, year)
    else:
        hour = dt.hour
        minute = str(dt.minute)
        if len(minute) == 1:
            minute = '0' + minute
        is24hour = True  # TODO: make setting for this
        if not is24hour:
            return '%s %s%s, %s, %s:%s' % (month, day, ordinalSuffix, year, hour, minute)
        else:
            if hour < 12:
                timeSuffix = 'AM'
            else:
                timeSuffix = 'PM'
            hour = ((hour - 1) % 12) + 1
            return '%s %s%s, %s, %s:%s %s' % (month, day, ordinalSuffix, year, hour, minute, timeSuffix)