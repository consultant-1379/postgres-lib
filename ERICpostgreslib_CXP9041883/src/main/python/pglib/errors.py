class FollowerNotRunning(Exception):
    pass


class InvalidDeploymentType(Exception):
    pass


class LeaderNotRunning(Exception):
    pass


class NoAvailablePostgresPod(Exception):
    pass


class NoFollowerInCluster(Exception):
    pass


class NoLeaderInCluster(Exception):
    pass


class NonReplicatingCluster(Exception):
    pass


class PsqlSessionException(Exception):
    pass


class PsqlAuthenticationFailure(PsqlSessionException):
    pass


class PsqlClientNotAvailable(PsqlSessionException):
    pass


class PsqlColumnDoesNotExist(PsqlSessionException):
    pass


class PostgresCredentialsException(PsqlSessionException):
    pass


class PostgresHostError(PsqlSessionException):
    pass


class PsqlObjectIsUndefined(PsqlSessionException):
    pass


class PsqlSyntaxError(PsqlSessionException):
    pass


class PsqlTableDoesNotExist(PsqlSessionException):
    pass
