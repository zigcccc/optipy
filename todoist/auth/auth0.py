import jwt

from todoist.config import settings


class VerifyToken():
    jwks_client = jwt.PyJWKClient(
        f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json",
        cache_keys=True,
        cache_jwk_set=True,
        lifespan=36000
    )

    def verify(self, token: str) -> dict[str, str]:
        try:
            jwk = self.jwks_client.get_signing_key_from_jwt(token)

        except jwt.exceptions.PyJWKClientError as error:
            raise error

        except jwt.exceptions.DecodeError as error:
            raise error

        try:
            decoded_token = jwt.decode(
                token,
                jwk.key,
                algorithms=settings.AUTH0_ALGORITHMS,
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=settings.AUTH0_ISSUER
            )

        except Exception as e:
            raise e

        return decoded_token
