@echo off
REM Replace the following with your actual name and email
set NAME=Your Name
set EMAIL=your@email.com

REM Export public key
gpg --armor --export "%NAME% <%EMAIL%>" > public.asc

REM Export private key (keep this file safe!)
gpg --armor --export-secret-keys "%NAME% <%EMAIL%>" > private.asc

echo Public and private keys exported to public.asc and private.asc
pause