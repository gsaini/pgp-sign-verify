import tempfile
import os
from typing import Optional, Dict, Any

import gnupg


def get_gpg(gnupghome: Optional[str] = None) -> gnupg.GPG:
    """Return a GPG instance. If gnupghome is provided it will be used.
    Otherwise the default GPG home will be used (system gpg).
    """
    if gnupghome:
        os.makedirs(gnupghome, exist_ok=True)
    return gnupg.GPG(gnupghome=gnupghome)


def generate_key(name: str, email: str, passphrase: str, key_type: str = "RSA", key_length: int = 2048, gnupghome: Optional[str] = None) -> Dict[str, Any]:
    gpg = get_gpg(gnupghome)
    input_data = gpg.gen_key_input(
        name_real=name,
        name_email=email,
        passphrase=passphrase,
        key_type=key_type,
        key_length=key_length,
    )
    key = gpg.gen_key(input_data)
    fingerprint = key.fingerprint
    public = gpg.export_keys(fingerprint)
    private = gpg.export_keys(fingerprint, True, passphrase=passphrase)
    return {
        "fingerprint": fingerprint,
        "public": public,
        "private": private,
    }


def import_key(key_text: str, gnupghome: Optional[str] = None) -> Dict[str, Any]:
    gpg = get_gpg(gnupghome)
    result = gpg.import_keys(key_text)
    return {
        "count": result.count,
        "fingerprints": result.fingerprints,
        "result": result.results,
    }


def list_keys(secret: bool = False, gnupghome: Optional[str] = None):
    gpg = get_gpg(gnupghome)
    return gpg.list_keys(secret=secret)


def sign_file(path: str, keyid: Optional[str] = None, passphrase: Optional[str] = None, gnupghome: Optional[str] = None) -> bytes:
    """Create a detached ASCII-armored signature for the file at path.
    Returns the signature bytes (ASCII armored).
    """
    gpg = get_gpg(gnupghome)
    with open(path, "rb") as f:
        signed = gpg.sign_file(f, keyid=keyid, passphrase=passphrase, detach=True)
    # signed.data may be bytes. If not present, str(signed) contains the signature
    data = None
    if hasattr(signed, "data") and signed.data:
        data = signed.data
    else:
        data = str(signed).encode("utf-8")
    return data


def verify_signature(sig_path: str, data_path: str, gnupghome: Optional[str] = None) -> Dict[str, Any]:
    """Verify a detached signature file against data file.
    Returns a dict with keys: valid (bool), status (str), fingerprint (str or None), trust_text.
    """
    gpg = get_gpg(gnupghome)
    with open(sig_path, "rb") as sig_file:
        verify = gpg.verify_file(sig_file, data_path)

    return {
        "valid": bool(verify.valid),
        "status": verify.status,
        "fingerprint": verify.fingerprint,
        "trust_text": verify.trust_text,
        "username": verify.username,
    }
