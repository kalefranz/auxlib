# -*- coding: utf-8 -*-
import os

from testtools import TestCase

from auxlib import crypt
from auxlib.crypt import AuthenticationError, encrypt, decrypt



class TestBase64Encoding(TestCase):

    def test_encode(self):
        test_str = "Mickey Mouse"
        result_str = "TWlja2V5IE1vdXNl".encode('UTF-8')
        self.assertEqual(crypt.as_base64(test_str),
                         result_str)

    def test_encode_unicode(self):
        test_str = u"Mickey Mouseп"
        result_str = "TWlja2V5IE1vdXNl0L8=".encode('UTF-8')
        self.assertEqual(crypt.as_base64(test_str),
                         result_str)

    def test_decode(self):
        test_str = "TWlubmllIE1vdXNl"
        result_str= "Minnie Mouse".encode('UTF-8')
        self.assertEqual(crypt.from_base64(test_str),
                         result_str)

    def test_decode_unicode(self):
        test_str = "Tc65bm7OuWUgTW_PhXNl"
        result_str= u"Mιnnιe Moυse".encode('UTF-8')
        self.assertEqual(crypt.from_base64(test_str),
                         result_str)

    def test_decode_unicode_unicode(self):
        test_str = u"Tc65bm7OuWUgTW_PhXNl"
        result_str= u"Mιnnιe Moυse".encode('UTF-8')
        self.assertEqual(crypt.from_base64(test_str),
                         result_str)

    def test_encode_and_decode_unicode(self):
        test_str = u"Mickey & Miννie Μouse".encode('UTF-8')
        self.assertEqual(crypt.from_base64(crypt.as_base64(test_str)),
                         test_str)


class TestKeyCreation(TestCase):

    def test_create_keys(self):
        key = crypt.generate_encryption_key()
        self.assertEquals(len(crypt.from_base64(key)),
                          crypt.AES_KEY_SIZE + crypt.HMAC_SIG_SIZE)

        # generate new key, and make sure it's different than the last
        self.assertNotEqual(crypt.generate_encryption_key(), key)

    def test_hashing_secret(self):
        secret = 'test secret'
        key_hash = crypt.generate_hash_from_secret(secret)
        self.assertEquals(len(crypt.from_base64(key_hash)),
                          crypt.AES_KEY_SIZE + crypt.HMAC_SIG_SIZE)

        # hash should always be the same
        self.assertEqual(key_hash, crypt.generate_hash_from_secret(secret))


class TestAESEncryption(TestCase):

    def test_encrypt_and_decrypt_end_to_end(self):
        test_data = u"Mickey & Miννie Μouse"
        encryption_key = crypt.generate_encryption_key()
        encrypted_data = crypt.aes_encrypt(encryption_key, test_data)
        decrypted_data = crypt.aes_decrypt(encryption_key, encrypted_data)
        self.assertEquals(decrypted_data, test_data.encode('UTF-8'))

    def test_invalid_hmac_throws_error(self):
        test_data = u"Mickey & Miννie Μouse"
        encryption_key = crypt.generate_encryption_key()
        encrypted_data = crypt.from_base64(crypt.aes_encrypt(encryption_key, test_data))
        enc_data_only = encrypted_data[:-crypt.HMAC_SIG_SIZE]
        real_hmac_signature = encrypted_data[-crypt.HMAC_SIG_SIZE:]
        fake_hmac_signature = os.urandom(crypt.HMAC_SIG_SIZE)
        self.assertEqual(encrypted_data, enc_data_only + real_hmac_signature)
        self.assertRaises(AuthenticationError, crypt.aes_decrypt, encryption_key,
                          crypt.as_base64(enc_data_only + fake_hmac_signature))
        decrypted_data = crypt.aes_decrypt(encryption_key,
                                           crypt.as_base64(enc_data_only + real_hmac_signature))
        self.assertEquals(decrypted_data, test_data.encode('UTF-8'))

    def test_encrypt_decrypt(self):
        data = ('abcdefg\n' * 5000).encode('UTF-8')
        secret_key = "test_scoobydoobydoo".encode('UTF-8')
        encryption_key_encrypted, encrypted_data = encrypt(secret_key, data)
        round_trip = decrypt(secret_key, encryption_key_encrypted, encrypted_data)
        self.assertEqual(data, round_trip)


