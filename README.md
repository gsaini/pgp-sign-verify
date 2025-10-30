# PGP Sign & Verify (Streamlit demo)


This repository contains a small Streamlit app that demonstrates signing files (detached ASCII-armored signatures) and verifying signatures using PGP keys already present in your GPG keyring.

Files added:

- `app.py` — Streamlit app with two tabs: Sign and Verify.
- `gnupg_utils.py` — small wrapper around `python-gnupg` for listing keys, signing and verification.
- `requirements.txt` — Python dependencies.


Prerequisites
-------------

- Python 3.14 (see below for setup)
- GnuPG installed on your machine (the `gpg` binary). On macOS you can run:
	```bash
	brew install gnupg
	```
- **PGP keys must be generated or imported using the terminal (`gpg` CLI) before using this app.**

Install Python dependencies:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```


Key management (must be done in terminal)
-----------------------------------------

**Generate a keypair with gpg CLI:**

```bash
gpg --full-generate-key
# follow the prompts (choose an RSA key, size 2048 or 4096, enter name/email and a passphrase)
```

**Import an existing private key:**

```bash
gpg --import private.asc
```

**Import a public key:**

```bash
gpg --import public.asc
```

**List keys in your keyring:**

```bash
gpg --list-secret-keys
gpg --list-keys
```

**Export public key (for sharing):**

```bash
gpg --armor --export "Your Name <you@example.com>" > public.asc
```

**Export private key (for backup, keep safe!):**

```bash
gpg --armor --export-secret-keys "Your Name <you@example.com>" > private.asc
```


Security
--------

This app writes uploaded files and signatures to temporary files to interact with the local `gpg` installation. Do not run it on untrusted networks if you are using real private keys without additional safeguards.


Limitations
-----------

- The app uses the system GnuPG (so GPG must be installed).
- The `python-gnupg` library wraps gpg and interacts with a local keyring; behavior may vary depending on gpg version and configuration.


If you want, I can:
- Add an option to run a private GPG home inside the app (isolated keyring).
- Add unit tests for the helper functions.
- Provide a Dockerfile that contains GnuPG and runs the Streamlit app.

## Ensuring Python 3.14 for this project

This project is intended to run on Python 3.14. To help ensure that environment:

- `pyproject.toml` includes `requires-python = ">=3.14,<3.15"`.
- A `.python-version` file is included with `3.14.0` for `pyenv` users.

Installation suggestions (macOS):

1) Install `pyenv` (if not installed):

```bash
brew install pyenv
```

2) Install Python 3.14 using pyenv and set it for the project:

```bash
pyenv install 3.14.0
pyenv local 3.14.0
```

Alternatively, if you prefer Homebrew and a bottle is available:

```bash
brew install python@3.14
# then use the full path or update PATH to point to the installed python3.14
```

3) Recreate the virtualenv with Python 3.14 and install deps:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you want, I can add a Dockerfile that installs Python 3.14 and GnuPG so the environment is reproducible.
