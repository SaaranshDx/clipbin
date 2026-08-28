# Clipbin

Share text like never befour

Clipbin is a small, lightweight text-sharing utility.

It's built around privacy, speed, and portability.

## CLI

The Clipbin CLI is a small command-line tool which can be used to interact with Clipbin via your terminal.

### Installation

Just download the binary from the [Releases page](https://github.com/SaaranshDx/clipbin/releases) and put it somewhere in your `PATH`.

On Unix systems, you can place it in:

```text
/usr/local/bin/
```

On Windows, you can place it in a directory included in your `PATH`, such as:

```text
C:\Windows\System32\
```

### Usage

#### Create a paste

The CLI reads text from `stdin`.

```bash
echo "hello world" | clipbin
```

This will create a paste and output its URL:

```text
https://clipbin.github.io/GBLV5C
```

You can also pipe files directly:

```bash
cat file.txt | clipbin
```

#### Set paste duration

The default paste duration is 7 days.

You can specify the duration in hours with `--duration`:

```bash
echo "hello world" | clipbin --duration 24
```

#### Encrypt a paste

Clipbin supports optional client-side encryption using AES-256-GCM.

```bash
echo "secret message" | clipbin --encrypt
```

The CLI will prompt you for an encryption key:

```text
Key:
```

The encryption key is never sent to or stored by the API.

**Keep your key safe. If you lose it, the encrypted paste cannot be decrypted.**

#### Retrieve a paste

Pastes can be retrieved using either their ID or their full URL:

```bash
clipbin get GBLV5C
```

```bash
clipbin get https://clipbin.github.io/GBLV5C
```

The paste contents are written directly to `stdout`, making them easy to pipe into other commands:

```bash
clipbin get GBLV5C > output.txt
```

#### Decrypt an encrypted paste

Encrypted pastes can be decrypted using `--decrypt`:

```bash
clipbin get 9F27KL --decrypt
```

The CLI will prompt for the encryption key and decrypt the paste locally.

Without `--decrypt`, an encrypted paste is returned as its raw JSON encryption envelope.

## Encryption

Encryption is optional and happens entirely on the client.

Clipbin uses:

- **AES-256-GCM** for encryption
- **PBKDF2-SHA-256** for key derivation
- **250,000 PBKDF2 iterations**
- A random **16-byte salt** for every encrypted paste
- A random **12-byte initialization vector** for every encrypted paste

The API only receives the encrypted data and encryption metadata.

The encryption key itself is never sent to or stored by the server.

An encrypted paste is stored as a JSON envelope:

```json
{
  "version": 1,
  "algorithm": "AES-GCM",
  "kdf": "PBKDF2-SHA-256",
  "iterations": 250000,
  "salt": "...",
  "iv": "...",
  "ciphertext": "..."
}
```

The encryption format is shared between the web client and CLI so encrypted pastes can be created and opened from either client.

## API

> [!WARNING]
> For detailed and regularly updated api documentation visit [Clipbin's API documentation](https://clipbin.github.io/api)

The CLI communicates with the Clipbin API.

### Create a paste

```http
POST /pastes
```

Example request:

```json
{
  "data": "hello world",
  "duration": 168
}
```

The API returns the generated paste ID.

### Paste URLs

Created pastes are available at:

```text
https://clipbin.github.io/<paste-id>
```

## Privacy

Clipbin is designed to keep the service simple and minimize what the server needs to know.

For encrypted pastes:

- Encryption happens on the client.
- The encryption key never reaches the API.
- The server stores only the encrypted payload and its associated metadata.
- Decryption happens on the client.

Losing the encryption key means losing access to the encrypted contents.

## Web Client

Clipbin also provides a web client for creating and viewing pastes.

The web client supports:

- Plain text pastes
- Optional encryption
- Paste expiration
- Client-side encryption
- Encrypted paste decryption
- API access

## License

Clipbin is licensed under the MIT License.