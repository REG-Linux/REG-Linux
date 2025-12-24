from collections.abc import Mapping


class Command:
    """Represents a shell command with environment variables and arguments."""

    def __init__(
        self, array: list[str], env: Mapping[str, str] | None = None
    ) -> None:
        """
        Initialize a Command instance.

        Args:
            array: List of strings representing the command and its arguments.
            env: Dictionary of environment variables. Defaults to None.
        """
        self.array: list[str] = array
        self.env: dict[str, str] = dict(env) if env is not None else {}

    def __str__(self) -> str:
        """Return a string representation of the command with environment variables."""
        # Using list comprehension to build parts
        env_parts = [
            f"{var_name}={var_value}" for var_name, var_value in self.env.items()
        ]
        return " ".join(env_parts + self.array)
