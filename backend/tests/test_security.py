import hashlib
import secrets

from app.core.security import ALGORITHM, verify_password, hash_password


def test_deux_hachages_du_meme_mot_de_passe_sont_differents() -> None:
    assert hash_password("mot-de-passe") != hash_password("mot-de-passe")


def test_le_bon_mot_de_passe_est_accepte_et_le_mauvais_refuse() -> None:
    stored = hash_password("mot-de-passe")

    assert verify_password("mot-de-passe", stored)
    assert not verify_password("autre-mot-de-passe", stored)


def test_un_condensat_malforme_est_refuse_sans_erreur() -> None:
    assert not verify_password("mot-de-passe", "x")


def test_un_condensat_avec_un_autre_nombre_d_iterations_reste_verifiable() -> None:
    iterations = 1234
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", b"mot-de-passe", salt, iterations
    )
    stored = f"{ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"

    assert verify_password("mot-de-passe", stored)
