"""Isolated subprocess executor for Nmap."""

import asyncio
import logging
import subprocess
from typing import Tuple, Optional
from app.config import settings
from app.scanner.profiles import get_profile, BaseScanProfile

logger = logging.getLogger("northstar.scanner.engine")


def is_nmap_available() -> bool:
    """Check if the nmap binary is installed and executable."""
    try:
        proc = subprocess.run(
            [settings.NMAP_BINARY, "--version"],
            capture_output=True,
            timeout=5,
            check=False,
        )
        return proc.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


class NmapEngine:
    """Secure Nmap execution engine enforcing timeouts and subprocess isolation."""

    @staticmethod
    async def run_scan(
        target: str,
        profile_name: str = "quick",
        cancel_event: Optional[asyncio.Event] = None,
    ) -> Tuple[int, str, str]:
        """Execute an Nmap scan asynchronously without blocking the event loop.

        Returns:
            (exit_code: int, stdout: str, stderr: str)
        """
        profile: BaseScanProfile = get_profile(profile_name)
        args = profile.build_args(target)

        logger.info(
            "Executing isolated Nmap scan: target=%s, profile=%s", target, profile.name
        )

        # Create async subprocess
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as err:
            logger.error("Nmap binary not found: %s", settings.NMAP_BINARY)
            raise RuntimeError(
                f"Nmap scanner binary '{settings.NMAP_BINARY}' is not installed on this system"
            ) from err

        try:
            # Wait for process to complete with timeout
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(),
                timeout=float(profile.timeout_seconds),
            )
            stdout = stdout_data.decode("utf-8", errors="replace")
            stderr = stderr_data.decode("utf-8", errors="replace")
            return process.returncode or 0, stdout, stderr

        except asyncio.TimeoutError:
            logger.warning(
                "Scan on %s exceeded timeout of %ds", target, profile.timeout_seconds
            )
            try:
                process.kill()
                await process.wait()
            except ProcessLookupError:
                pass
            raise TimeoutError(
                f"Scan timed out after {profile.timeout_seconds} seconds"
            )

        except asyncio.CancelledError:
            logger.info("Scan on %s was cancelled by user request", target)
            try:
                process.terminate()
                await asyncio.sleep(0.5)
                if process.returncode is None:
                    process.kill()
                await process.wait()
            except ProcessLookupError:
                pass
            raise
