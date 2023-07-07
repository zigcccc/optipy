import jwt
from fastapi import HTTPException, status

from optipy.api.exceptions import BadRequestFromRaisedException
from optipy.config import settings


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

        except jwt.exceptions.PyJWKClientError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error while trying to initialize JWK client."
            )

        except jwt.exceptions.DecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error decoding JWT token"
            )

        try:
            decoded_token = jwt.decode(
                token,
                jwk.key,
                algorithms=settings.AUTH0_ALGORITHMS,
                audience=settings.AUTH0_API_AUDIENCE,
                issuer=settings.AUTH0_ISSUER
            )

        except Exception as e:
            raise BadRequestFromRaisedException(exception=e)

        return decoded_token
