class DomainError(Exception):
    status_code = 400
    message = "Não foi possível concluir a operação."

    def __init__(self) -> None:
        super().__init__(self.message)


class MissingOrganizationError(DomainError):
    status_code = 400
    message = "Acesse pelo endereço da sua organização."


class OrganizationNotFoundError(DomainError):
    status_code = 404
    message = "Organização não encontrada."


class SlugAlreadyInUseError(DomainError):
    status_code = 409
    message = "Este subdomínio já está em uso."


class TenantDatabaseConflictError(DomainError):
    status_code = 409
    message = "Já existe um banco de dados para este subdomínio."


class OrganizationStillProvisioningError(DomainError):
    status_code = 409
    message = "A organização ainda está sendo criada."


class EmailAlreadyRegisteredError(DomainError):
    status_code = 409
    message = "E-mail já cadastrado."


class InvalidCredentialsError(DomainError):
    status_code = 401
    message = "E-mail ou senha inválidos."


class InvalidAccessTokenError(DomainError):
    status_code = 401
    message = "Sessão inválida ou expirada. Entre novamente."


class IncorrectPasswordError(DomainError):
    status_code = 400
    message = "Senha incorreta."


class OrganizationAdminRequiredError(DomainError):
    status_code = 403
    message = "Acesso restrito ao administrador da organização."


class OrganizationAdminAccountDeletionError(DomainError):
    status_code = 403
    message = "O administrador da organização não pode excluir a própria conta."


class MemberNotFoundError(DomainError):
    status_code = 404
    message = "Membro não encontrado."


class OrganizationAdminRemovalError(DomainError):
    status_code = 403
    message = "Não é possível remover um administrador da organização."


class ActiveOrganizationDeletionError(DomainError):
    status_code = 409
    message = "Desative a organização antes de excluí-la."
