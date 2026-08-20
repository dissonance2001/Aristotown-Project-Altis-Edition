#!/usr/bin/env python2
"""
Checks that the version of the projects bundled in ensurepip are the latest
versions available.
"""
from __future__ import absolute_import
from __future__ import print_function
import ensurepip
import json
import six.moves.urllib.request, six.moves.urllib.error, six.moves.urllib.parse
import sys


def main():
    outofdate = False

    for project, version in ensurepip._PROJECTS:
        data = json.loads(six.moves.urllib.request.urlopen(
            "https://pypi.python.org/pypi/{}/json".format(project),
        ).read().decode("utf8"))
        upstream_version = data["info"]["version"]

        if version != upstream_version:
            outofdate = True
            print(("The latest version of {} on PyPI is {}, but ensurepip "
                  "has {}".format(project, upstream_version, version)))

    if outofdate:
        sys.exit(1)


if __name__ == "__main__":
    main()
