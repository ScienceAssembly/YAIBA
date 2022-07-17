from __future__ import annotations

import base64
import hashlib
import secrets

from yaiba.log.types import PseudoUserName, UserName


class Pseudonymizer:
    """
    Pseudonymize the input (ex. username).
    
    `salt` can be any byte strings ( https://en.wikipedia.org/wiki/Salt_(cryptography) ), but should be different 
    across stakeholders (See guideline from Japan Gov; 
    https://www.ppc.go.jp/files/pdf/280930_siryou1-5.pdf#page=13). If salt is not applied, salt is generated    
    randomly.
    """

    def __init__(self, salt: bytes):
        self.salt = salt

    @classmethod
    def new_random(cls) -> Pseudonymizer:
        return cls(secrets.token_bytes(32))

    def pseudonymize_user_name(self, user_name: UserName) -> PseudoUserName:
        hasher = hashlib.sha256()
        hasher.update(user_name.encode('utf-8'))

        # salt
        hasher.update(b'\0')
        hasher.update(self.salt)

        pseudonymized = base64.b64encode(hasher.digest()).decode('utf-8')
        return PseudoUserName(pseudonymized)
