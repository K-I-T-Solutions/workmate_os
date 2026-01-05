"""
SevDesk Token Encryption/Decryption

Sichere Verschlüsselung von API-Tokens mit Fernet (symmetrische Verschlüsselung).

WICHTIG:
- Encryption Key muss in .env gespeichert werden (SEVDESK_ENCRYPTION_KEY)
- Key NIEMALS in Git committen!
- Key generieren mit: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
import os
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class SevDeskTokenEncryption:
    """
    Token Encryption Manager für SevDesk API Tokens.

    Verwendet Fernet (symmetrische Verschlüsselung) für sichere Speicherung
    von API-Tokens in der Datenbank.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize Token Encryption.

        Args:
            encryption_key: Fernet encryption key (base64 encoded).
                           Falls nicht angegeben, wird SEVDESK_ENCRYPTION_KEY aus .env gelesen.

        Raises:
            ValueError: Wenn kein Encryption Key gefunden wurde
        """
        # Get encryption key from parameter or environment
        key = encryption_key or os.getenv("SEVDESK_ENCRYPTION_KEY")

        if not key:
            raise ValueError(
                "No encryption key found. Set SEVDESK_ENCRYPTION_KEY in .env or pass as parameter.\n"
                "Generate key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )

        # Convert to bytes if string
        if isinstance(key, str):
            key = key.encode()

        self.fernet = Fernet(key)

    def encrypt(self, token: str) -> str:
        """
        Encrypt SevDesk API Token.

        Args:
            token: Plain text API token (32 chars hex)

        Returns:
            Encrypted token (base64 encoded)

        Example:
            >>> encryptor = SevDeskTokenEncryption()
            >>> encrypted = encryptor.encrypt("aa4dfe2316d9124d41bcca5baa1dfb0d")
            >>> print(encrypted)
            'gAAAAABh...'  # base64 encoded
        """
        if not token:
            raise ValueError("Token cannot be empty")

        # Encrypt token
        token_bytes = token.encode()
        encrypted_bytes = self.fernet.encrypt(token_bytes)

        # Return as string
        encrypted_str = encrypted_bytes.decode()

        logger.debug(f"🔒 [SevDesk] Token encrypted (length: {len(encrypted_str)})")

        return encrypted_str

    def decrypt(self, encrypted_token: str) -> str:
        """
        Decrypt SevDesk API Token.

        Args:
            encrypted_token: Encrypted token (base64 encoded)

        Returns:
            Plain text API token

        Raises:
            InvalidToken: Wenn Token nicht entschlüsselt werden kann

        Example:
            >>> encryptor = SevDeskTokenEncryption()
            >>> decrypted = encryptor.decrypt("gAAAAABh...")
            >>> print(decrypted)
            'aa4dfe2316d9124d41bcca5baa1dfb0d'
        """
        if not encrypted_token:
            raise ValueError("Encrypted token cannot be empty")

        try:
            # Decrypt token
            encrypted_bytes = encrypted_token.encode()
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)

            # Return as string
            decrypted_str = decrypted_bytes.decode()

            logger.debug("🔓 [SevDesk] Token decrypted successfully")

            return decrypted_str

        except InvalidToken as e:
            logger.error(f"❌ [SevDesk] Failed to decrypt token: {e}")
            raise ValueError("Invalid or corrupted encryption token") from e


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def encrypt_sevdesk_token(token: str) -> str:
    """
    Convenience function to encrypt SevDesk token.

    Args:
        token: Plain text API token

    Returns:
        Encrypted token
    """
    encryptor = SevDeskTokenEncryption()
    return encryptor.encrypt(token)


def decrypt_sevdesk_token(encrypted_token: str) -> str:
    """
    Convenience function to decrypt SevDesk token.

    Args:
        encrypted_token: Encrypted token

    Returns:
        Plain text API token
    """
    encryptor = SevDeskTokenEncryption()
    return encryptor.decrypt(encrypted_token)


# ============================================================================
# KEY GENERATION UTILITY
# ============================================================================

def generate_encryption_key() -> str:
    """
    Generate new Fernet encryption key.

    Returns:
        Base64 encoded encryption key

    Example:
        >>> key = generate_encryption_key()
        >>> print(f"Add to .env: SEVDESK_ENCRYPTION_KEY={key}")
    """
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    # Generate new key when run directly
    key = generate_encryption_key()
    print("=" * 70)
    print("🔑 NEW SEVDESK ENCRYPTION KEY GENERATED")
    print("=" * 70)
    print()
    print("Add this to your .env file:")
    print()
    print(f"SEVDESK_ENCRYPTION_KEY={key}")
    print()
    print("⚠️  IMPORTANT:")
    print("- Never commit this key to Git!")
    print("- Keep this key secure and backed up!")
    print("- If you lose this key, encrypted tokens cannot be recovered!")
    print()
    print("=" * 70)
