# envault

> A CLI tool for securely managing and syncing `.env` files across dev environments using encrypted local storage.

---

## Installation

```bash
pip install envault
```

Or with [pipx](https://pypa.github.io/pipx/) (recommended):

```bash
pipx install envault
```

---

## Usage

**Initialize a vault in your project:**

```bash
envault init
```

**Store your `.env` file:**

```bash
envault push --env .env --name myproject
```

**Pull and restore a stored environment:**

```bash
envault pull --name myproject
```

**List all stored environments:**

```bash
envault list
```

Secrets are encrypted locally using AES-256 before being stored. A master password is required on first use and cached securely in your system keyring.

---

## How It Works

1. `envault` encrypts your `.env` file using a master password derived key.
2. Encrypted vaults are stored in `~/.envault/` on your local machine.
3. Optionally sync vaults across machines via a shared backend (S3, Git, etc.).

---

## Requirements

- Python 3.8+
- Works on macOS, Linux, and Windows

---

## License

This project is licensed under the [MIT License](LICENSE).

---

> ⚠️ **Never commit your `.env` files to version control.** envault is a safer alternative.