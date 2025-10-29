import streamlit as st
import tempfile
import os

import gnupg_utils


st.set_page_config(page_title="PGP Sign & Verify", layout="wide")

st.title("PGP Sign & Verify — Streamlit demo")

st.markdown(
    """
This small demo shows how to generate keys, sign a file (detached signature), and verify a signature.

Requirements: system `gpg` must be installed and available to the environment where this app runs.
"""
)

tabs = st.tabs(["Sign", "Verify"])


with tabs[0]:
    st.header("Sign a file")

    with st.expander("Generate a new keypair"):
        name = st.text_input("Name (Real name)")
        email = st.text_input("Email")
        passphrase = st.text_input("Passphrase (protects the private key)", type="password")
        key_length = st.selectbox("Key length", [2048, 3072, 4096], index=0)

        if st.button("Generate keypair"):
            if not name or not email or not passphrase:
                st.error("Please provide name, email and passphrase to generate a keypair.")
            else:
                with st.spinner("Generating keypair (this can take a few seconds)..."):
                    res = gnupg_utils.generate_key(name=name, email=email, passphrase=passphrase, key_length=int(key_length))
                st.success("Keypair generated")
                st.write("Fingerprint:", res["fingerprint"])
                st.download_button("Download public key", res["public"], file_name=f"{email}_pub.asc")
                st.download_button("Download private key (armored)", res["private"], file_name=f"{email}_priv.asc")

    st.markdown("---")

    st.subheader("Sign using a private key from keyring or import one")
    secret_keys = gnupg_utils.list_keys(secret=True)
    key_options = [f"{k['uids'][0]} | {k['fingerprint']}" for k in secret_keys]
    key_choice = None
    if key_options:
        key_choice = st.selectbox("Select private key from local GPG keyring", ["(none)"] + key_options)

    st.write("Or paste an armored private key and import it (then select from keyring)")
    priv_text = st.text_area("Private key (PEM/ASCII armored)")
    if st.button("Import pasted private key"):
        if not priv_text.strip():
            st.error("Paste a private key before importing")
        else:
            r = gnupg_utils.import_key(priv_text)
            st.success(f"Imported {r['count']} key(s): {r['fingerprints']}")

    uploaded_file = st.file_uploader("File to sign", type=None)
    passphrase_for_sign = st.text_input("Passphrase for private key (if needed)", type="password")

    if st.button("Create detached signature"):
        if not uploaded_file:
            st.error("Upload a file to sign first")
        else:
            # write uploaded to a temp file
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # determine keyid
            keyid = None
            if key_choice and key_choice != "(none)":
                # fingerprint is after '| '
                try:
                    keyid = key_choice.split('|')[-1].strip()
                except Exception:
                    keyid = None

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
    st.write("Upload the original file and the detached signature (.asc or .sig).")
    verify_file = st.file_uploader("Original file to verify", key="verify_file")
    verify_sig = st.file_uploader("Detached signature file", key="verify_sig")

    st.write("Or paste an ASCII-armored public key to import and use for verification")
    pub_text = st.text_area("Public key (PEM/ASCII armored)", key="pub_text")
    if st.button("Import public key for verification"):
        if not pub_text.strip():
            st.error("Paste a public key before importing")
        else:
            r = gnupg_utils.import_key(pub_text)
            st.success(f"Imported {r['count']} key(s): {r['fingerprints']}")

    if st.button("Verify signature"):
        if not verify_file or not verify_sig:
            st.error("Upload both the original file and the detached signature")
        else:
            # save both to temp files
            with tempfile.NamedTemporaryFile(delete=False) as tmp_data:
                tmp_data.write(verify_file.read())
                data_path = tmp_data.name

            with tempfile.NamedTemporaryFile(delete=False) as tmp_sig:
                tmp_sig.write(verify_sig.read())
                sig_path = tmp_sig.name

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
        "This demo relies on the system GnuPG installation. On macOS you can install it with: `brew install gnupg`.\n"
        "You can also create keys using the `gpg` CLI; see README for instructions."
    )
