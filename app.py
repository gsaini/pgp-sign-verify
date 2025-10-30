import streamlit as st
import tempfile
import os

import gnupg_utils


st.set_page_config(page_title="PGP Sign & Verify", layout="wide")

st.title("PGP Sign & Verify — Streamlit demo")


st.markdown(
    """
This app lets you sign a file with a private key from your GPG keyring, and verify signatures using public keys in your keyring.

**Prerequisite:** You must generate/import your PGP keys using the terminal (`gpg` CLI) before using this app. See README for instructions.
"""
)

tabs = st.tabs(["Sign", "Verify"])



with tabs[0]:
    st.header("Sign a file")
    st.write("Select a private key from your GPG keyring and sign a file.")

    secret_keys = gnupg_utils.list_keys(secret=True)
    key_options = [f"{k['uids'][0]} | {k['fingerprint']}" for k in secret_keys]
    key_choice = None
    if key_options:
        key_choice = st.selectbox("Select private key from local GPG keyring", key_options)
    else:
        st.warning("No private keys found in your GPG keyring. Please generate/import keys using the terminal first.")

    uploaded_file = st.file_uploader("File to sign", type=None)
    passphrase_for_sign = st.text_input("Passphrase for private key", type="password")

    if st.button("Create detached signature"):
        if not uploaded_file:
            st.error("Upload a file to sign first")
        elif not key_choice:
            st.error("Select a private key from your keyring.")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            keyid = key_choice.split('|')[-1].strip()
            sig_bytes = gnupg_utils.sign_file(tmp_path, keyid=keyid, passphrase=passphrase_for_sign)

            if sig_bytes:
                st.success("Signature created")
                sig_name = uploaded_file.name + ".asc"
                st.download_button("Download signature (detached, ASCII-armored)", sig_bytes, file_name=sig_name)
                st.text_area("Signature (ASCII-armored)", sig_bytes.decode("utf-8"), height=200)
            else:
                st.error("Failed to create signature — ensure the private key exists in the keyring and passphrase is correct.")



with tabs[1]:
    st.header("Verify signature")
    st.write("Upload the original file and the detached signature (.asc or .sig). The public key must already be in your GPG keyring.")
    verify_file = st.file_uploader("Original file to verify", key="verify_file")
    verify_sig = st.file_uploader("Detached signature file", key="verify_sig")

    pub_keys = gnupg_utils.list_keys(secret=False)
    pub_options = [f"{k['uids'][0]} | {k['fingerprint']}" for k in pub_keys]
    pub_choice = None
    if pub_options:
        pub_choice = st.selectbox("Select public key from local GPG keyring (for verification)", pub_options)
    else:
        st.warning("No public keys found in your GPG keyring. Please import public keys using the terminal first.")

    if st.button("Verify signature"):
        if not verify_file or not verify_sig:
            st.error("Upload both the original file and the detached signature")
        elif not pub_choice:
            st.error("Select a public key from your keyring.")
        else:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_data:
                tmp_data.write(verify_file.read())
                data_path = tmp_data.name

            with tempfile.NamedTemporaryFile(delete=False) as tmp_sig:
                tmp_sig.write(verify_sig.read())
                sig_path = tmp_sig.name

            # Optionally, could restrict verification to a specific key, but gpg will use keyring
            res = gnupg_utils.verify_signature(sig_path, data_path)
            if res.get("valid"):
                st.success("Signature is VALID")
            else:
                st.error("Signature is NOT valid")

            st.write("status:", res.get("status"))
            st.write("signer fingerprint:", res.get("fingerprint"))
            st.write("signer username:", res.get("username"))

    st.markdown("---")
    st.subheader("Notes")
    st.write(
        "This app relies on the system GnuPG installation. On macOS you can install it with: `brew install gnupg`.\n"
        "You must generate/import keys using the `gpg` CLI before using this app. See README for instructions."
    )
