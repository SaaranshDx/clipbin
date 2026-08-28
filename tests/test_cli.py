import base64
import io
import json
import sys
import unittest
from unittest.mock import Mock, patch

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cli import main as cli


class CliTests(unittest.TestCase):
    def encrypted_payload(self, plaintext="secret text", key="correct horse"):
        salt = bytes(range(16))
        iv = bytes(range(12))
        derived = cli.hashlib.pbkdf2_hmac(
            "sha256", key.encode(), salt, 250000, dklen=32
        )
        ciphertext = AESGCM(derived).encrypt(iv, plaintext.encode(), None)
        return json.dumps({
            "version": 1,
            "algorithm": "AES-GCM",
            "kdf": "PBKDF2-SHA-256",
            "iterations": 250000,
            "salt": base64.b64encode(salt).decode(),
            "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        })

    @patch.object(cli.requests, "post")
    @patch.object(cli, "getpass", return_value="upload key")
    @patch.object(cli.sys, "stdin", new_callable=io.StringIO, initial_value="hello")
    @patch.object(cli.sys, "argv", ["clipbin", "--encrypt", "--duration", "24"])
    def test_encrypted_upload(self, _stdin, _getpass, post):
        post.return_value = Mock(ok=True, json=lambda: {"id": "ABC123"})

        result = cli.main()

        self.assertEqual(result, 0)
        payload = post.call_args.kwargs["json"]
        envelope = json.loads(payload["data"])
        self.assertEqual(payload["duration"], 24)
        self.assertEqual(cli.decrypt_paste(payload["data"], "upload key"), "hello")
        self.assertEqual(envelope["iterations"], 250000)

    def test_decrypt_round_trip_and_wrong_key(self):
        payload = self.encrypted_payload()

        self.assertEqual(cli.decrypt_paste(payload, "correct horse"), "secret text")
        with self.assertRaises(cli.InvalidTag):
            cli.decrypt_paste(payload, "wrong key")

    @patch.object(cli.requests, "get")
    @patch.object(cli.sys, "stdout", new_callable=io.StringIO)
    def test_get_id_writes_plaintext(self, stdout, get):
        get.return_value = Mock(ok=True, text="restored\n")

        with patch.object(cli.sys, "argv", ["clipbin", "get", "8WVDY"]):
            result = cli.main()

        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue(), "restored\n")
        get.assert_called_once_with(
            "https://api.ghostdrop.qzz.io/pastes/8WVDY",
            timeout=15,
            allow_redirects=True,
        )

    @patch.object(cli.requests, "get")
    @patch.object(cli, "getpass", return_value="correct horse")
    @patch.object(cli.sys, "stdout", new_callable=io.StringIO)
    def test_get_url_decrypts(self, stdout, _getpass, get):
        get.return_value = Mock(ok=True, text=self.encrypted_payload("restored"))

        with patch.object(
            cli.sys, "argv", ["clipbin", "get", "https://clipbin.github.io/8WVDY", "--decrypt"]
        ):
            result = cli.main()

        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue(), "restored")
        self.assertTrue(get.call_args.kwargs["allow_redirects"])

    @patch.object(cli.requests, "get", side_effect=cli.requests.exceptions.Timeout("offline"))
    def test_get_network_error(self, _get):
        with patch.object(cli.sys, "argv", ["clipbin", "get", "8WVDY"]):
            result = cli.main()
        self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
