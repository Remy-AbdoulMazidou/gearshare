class DomainError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class RessourceIntrouvable(DomainError):
    pass


class ConflitMetier(DomainError):
    pass


class AccesRefuse(DomainError):
    pass


ConflitReservation = ConflitMetier
