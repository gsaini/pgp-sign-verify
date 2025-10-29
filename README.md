# PGP Sign & Verify (Streamlit demo)

This repository contains a small Streamlit app that demonstrates creating PGP keypairs, signing files (detached ASCII-armored signatures), and verifying signatures.

Files added:

- `app.py` — Streamlit app with two tabs: Sign and Verify.
- `gnupg_utils.py` — small wrapper around `python-gnupg` for key generation, import, signing and verification.
- `requirements.txt` — Python dependencies.

Prerequisites
-------------

- Python 3.8+
- GnuPG installed on your machine (the `gpg` binary). On macOS you can run:

```bash
brew install gnupg
```

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

Notes & example CLI commands
---------------------------

1) Generate a keypair with gpg CLI (example):

```bash
gpg --full-generate-key
# follow the prompts (choose an RSA key, size 2048 or 4096, enter name/email and a passphrase)
```

2) Export public key:

```bash
gpg --armor --export "Your Name <you@example.com>" > public.asc
```

3) Export private key (armored) — be careful with private keys and keep them secret:

```bash
gpg --armor --export-secret-keys "Your Name <you@example.com>" > private.asc
```

4) Use the Streamlit app to import keys, sign files and verify signatures.

Security
--------

This demo writes uploaded files and signatures to temporary files to interact with the local `gpg` installation. Do not run it on untrusted networks if you are using real private keys without additional safeguards.

Limitations
-----------

- The app uses the system GnuPG (so GPG must be installed).
- The `python-gnupg` library wraps gpg and interacts with a local keyring; behavior may vary depending on gpg version and configuration.

If you want, I can:

- Add an option to run a private GPG home inside the app (isolated keyring).
- Add unit tests for the helper functions.
- Provide a Dockerfile that contains GnuPG and runs the Streamlit app.
# pgp-sign-verify
A Utility library providing functions to sign and verify data using OpenPGP standards — private key + passphrase for signing, public key for verification.
