class Command:
    """Represents a shell command with environment variables and arguments."""
    def __init__(self, array, env=None):
        """
        Initialize a Command instance.

        Args:
            array (list): List of strings representing the command and its arguments.
            env (dict, optional): Dictionary of environment variables. Defaults to None.
        """
        self.array = array
        self.env = env if env is not None else {}

    def __str__(self):
        """Return a string representation of the command with environment variables."""
        parts = []

        for var_name, var_value in self.env.items():
            parts.append(f"{var_name}={var_value}")

        parts.extend(self.array)

        return " ".join(parts)
