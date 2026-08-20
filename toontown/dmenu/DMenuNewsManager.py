'''
Created on Apr 14, 2017

@author: Drew
'''
from __future__ import absolute_import
from direct.showbase.DirectObject import DirectObject
import six.moves.http_client

RELEASE_NOTES_URL = '/OSToontown/Project-Altis/master/resources/phase_3/etc/changelog.md'

class DMenuNewsManager(DirectObject):

    def __init__(self):
        DirectObject.__init__(self)

    def fetchReleaseNotes(self):
        req = six.moves.http_client.HTTPSConnection('raw.githubusercontent.com')
        req.request('GET', RELEASE_NOTES_URL)
        self.releaseNotes = req.getresponse().read()
        return self.releaseNotes
