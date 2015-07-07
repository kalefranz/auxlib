# -*- coding: utf-8 -*-
import json
import logging
from enum import Enum
import testtools

from auxlib.entity import Entity, StringField, ComposableField, EnumField

log = logging.getLogger(__name__)



json_string_1 = """
{
  "actor": "User",
  "repository": "Repository",
  "push": {
    "changes": [
      {
        "new": {
          "type": "branch",
          "name": "name-of-branch",
          "target": {
            "type": "commit",
            "hash": "709d658dc5b6d6afcd46049c2f332ee3f515a67d",
            "author": User,
            "message": "new commit message",
            "date": "2015-06-09T03:34:49+00:00",
            "parents": [
              {
              "hash": "1e65c05c1d5171631d92438a13901ca7dae9618c",
              "type": "commit"
              }
            ]
          }
        },
        "old": {
          "type": "branch",
          "name": "name-of-branch",
          "target": {
            "type": "commit",
            "hash": "1e65c05c1d5171631d92438a13901ca7dae9618c",
            "author": User,
            "message": "old commit message",
            "date": "2015-06-08T21:34:56+00:00",
            "parents": [
              {
              "hash": "e0d0c2041e09746be5ce4b55067d5a8e3098c843",
              "type": "commit"
              }
            ]
          }
        },
        "created": false,
        "forced": false,
        "closed": false
      }
    ]
  }
}
"""

json_string_simple = """
{
  "actor": "User",
  "repository": "Repository",
  "parent": {
    "hash": "e0d0c2041e09746be5ce4b55067d5a8e3098c843",
    "type": "commit"
  }
}
"""

class CommitType(Enum):
    COMMIT = "commit"


class Commit(Entity):

    hash = StringField()
    type = EnumField(CommitType)


class Simple(Entity):
    actor = StringField()
    repository = StringField()
    parent = ComposableField(Commit)


class ClassFieldTests(testtools.TestCase):

    def test_most_simplest(self):
        obj_dict = json.loads(json_string_simple)
        simple = Simple(**obj_dict)
        assert simple.actor == "User"
        assert isinstance(simple.parent, Commit)
        assert simple.parent.hash == "e0d0c2041e09746be5ce4b55067d5a8e3098c843"
        assert simple.parent.type == CommitType.COMMIT.value

    def test_simple_list(self):
        pass