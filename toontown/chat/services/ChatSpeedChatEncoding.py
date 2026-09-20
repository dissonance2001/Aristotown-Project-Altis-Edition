from typing import Optional, Tuple

from direct.directnotify.DirectNotifyGlobal import directNotify
from direct.directnotify.Notifier import Notifier

from toontown.chat.enums.ChatSpeedChatType import ChatSpeedChatType
from toontown.chat.models.ChatMessageContent import ChatSpeedChatContent

"""
A rule of the chat system is enforcing content is sent as a string.
For text and sticker messages, this is trivial to do.

However, for SpeedChat it's a little more tricky.
There are many different types of SpeedChat and each have multiple values.
To cover this case, we use custom encoding/decoding.

The encoded format looks like this (Spaces added for readability):
    Type || Primary ID || Secondary ID || Text
"""

_delimiter = "||"
_ignoreValue = "##"


def encode(speedChatType: ChatSpeedChatType, primaryId: Optional[int], secondaryId: Optional[int], text: Optional[str]):
    """
    Encodes a SpeedChat message into a string which can be sent through the chat system.

    :param speedChatType: The type of message being sent.
    :param primaryId: The primary id for the SpeedChat type.
    :param secondaryId: The secondary id for the SpeedChat type.
    :param text: The phrase converted into text form.
    :return: The encoded SpeedChat string.
    """
    primaryId = _ignoreValue if primaryId is None else primaryId
    secondaryId = _ignoreValue if secondaryId is None else secondaryId
    text = _ignoreValue if text is None else text
    return f"{speedChatType.value}{_delimiter}{primaryId}{_delimiter}{secondaryId}{_delimiter}{text}"


def decode(content: str) -> Optional[ChatSpeedChatContent]:
    """
    Decodes a SpeedChat message from its encoded format.
    Warning: This only validates the encoded format was followed. You'll need to validate the input etc.

    :param content: The encoded string to decode.
    :return: The decoded SpeedChat message if decoding is successful, otherwise None.
    """
    # First, check that we have enough values to match the encoded format.
    contentSplit = content.split(_delimiter)
    if len(contentSplit) != 4:
        return None

    # Get the SpeedChat type of the message.
    speedChatType = ChatSpeedChatType(contentSplit[0])
    if speedChatType is None:
        return None

    # Convert the ignored values to None. Each message should at least have a primary or secondary id.
    primaryId = None if contentSplit[1] == _ignoreValue else contentSplit[1]
    secondaryId = None if contentSplit[2] == _ignoreValue else contentSplit[2]
    text = None if contentSplit[3] == _ignoreValue else contentSplit[3]
    if primaryId is None and secondaryId is None:
        return None

    # Attempt to parse the primary id to an int.
    success, primaryId = __parseInt(primaryId)
    if not success:
        return None

    # Attempt to parse the secondary id to an int.
    success, secondaryId = __parseInt(secondaryId)
    if not success:
        return None

    # Create and return the content.
    return ChatSpeedChatContent(speedChatType, primaryId, secondaryId, text)


"""
Utility Methods
"""


def __parseInt(toParse: str) -> Tuple[bool, Optional[int]]:
    """
    A utility method to parse a string to an int without throwing an exception.

    :param toParse: The string to parse to an int.
    :return: A tuple containing if the conversion was successful and the parsed int.
    """
    if toParse is None:
        return True, None

    try:
        return True, int(toParse)
    except TypeError:
        return False, None
    except ValueError:
        return False, None
