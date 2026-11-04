import argparse
import getpass

from app.core.platform_database import open_platform_session
from app.exceptions.domain_exceptions import EmailAlreadyRegisteredError
from app.services.platform_admin_auth_service import PlatformAdminAuthService

MINIMUM_PASSWORD_LENGTH = 8


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cria um administrador da plataforma Busca Bula.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password")
    return parser.parse_args()


def read_password(arguments: argparse.Namespace) -> str:
    password = arguments.password or getpass.getpass("Senha: ")
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise SystemExit(f"A senha precisa ter pelo menos {MINIMUM_PASSWORD_LENGTH} caracteres.")
    return password


def create_platform_admin() -> None:
    arguments = parse_arguments()
    password = read_password(arguments)
    with open_platform_session() as platform_session:
        try:
            platform_admin = PlatformAdminAuthService(platform_session).create_platform_admin(
                arguments.name, arguments.email, password
            )
        except EmailAlreadyRegisteredError as error:
            raise SystemExit(error.message) from error
    print(f"Administrador da plataforma criado: {platform_admin.email}")


if __name__ == "__main__":
    create_platform_admin()
