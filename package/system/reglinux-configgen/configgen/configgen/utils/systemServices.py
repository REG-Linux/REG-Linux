from subprocess import PIPE, Popen

from .logger import get_logger

eslog = get_logger(__name__)


def is_service_enabled(name: str) -> bool:
    try:
        proc = Popen(["system-services", "list"], stdout=PIPE)
        out, _ = proc.communicate()
        for valmod in out.decode().splitlines():
            vals = valmod.split(";")
            if len(vals) > 1 and name == vals[0] and vals[1] == "*":
                eslog.debug(f"service {name} is enabled")
                return True
        eslog.debug(f"service {name} is disabled")
    except Exception as e:
        eslog.error(f"Failed to check if service {name} is enabled: {e}")
    return False


def get_service_status(name: str) -> str:
    try:
        proc = Popen(["system-services", "status", name], stdout=PIPE)
        out, _ = proc.communicate()
        val = out.decode().strip()
        eslog.debug(f'service {name} status: "{val}"')
        return val
    except Exception as e:
        eslog.error(f"Failed to get status for service {name}: {e}")
        return "unknown"
