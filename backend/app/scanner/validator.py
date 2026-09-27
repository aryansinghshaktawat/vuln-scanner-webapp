"""Target validation and SSRF-safe resolution module."""

import ipaddress
import re
import socket
from app.config import settings

DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)([a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
)

# Dangerous cloud metadata and reserved ranges
CLOUD_METADATA_IPS = {"169.254.169.254", "fd00:ec2::254"}


def validate_and_normalize_target(target: str) -> str:
    """Validate target format and apply SSRF / authorization safeguards.

    Returns the normalized target string.
    Raises ValueError with explanatory message on invalid or prohibited targets.
    """
    if not target or not target.strip():
        raise ValueError("Target parameter is required and cannot be empty")

    clean_target = target.strip().rstrip(".")
    if len(clean_target) > 253 or any(c.isspace() for c in clean_target):
        raise ValueError(
            "Target must not exceed 253 characters and cannot contain whitespace"
        )

    # Check for direct cloud metadata address
    if clean_target in CLOUD_METADATA_IPS:
        raise ValueError(
            "Target is a protected cloud metadata address and cannot be scanned"
        )

    # 1. Attempt IP address or CIDR range evaluation
    try:
        network = ipaddress.ip_network(clean_target, strict=False)

        # Enforce maximum address limits
        if network.num_addresses > settings.MAX_TARGETS_PER_SCAN:
            raise ValueError(
                f"CIDR range /{network.prefixlen} exceeds maximum allowed size "
                f"({settings.MAX_TARGETS_PER_SCAN} addresses)"
            )

        # Prohibit multicast, unspecified, and private cloud link-local
        if network.is_multicast:
            raise ValueError("Multicast target addresses are prohibited")
        if network.is_unspecified:
            raise ValueError("Unspecified address (0.0.0.0 / ::) is prohibited")
        if network.is_link_local:
            raise ValueError(
                "Link-local addresses (e.g. 169.254.0.0/16) are prohibited"
            )

        # Check loopback access
        if network.is_loopback and not settings.ALLOW_LOOPBACK_SCAN:
            raise ValueError("Loopback target scanning is disabled by security policy")

        # Return standardized IP or CIDR string
        return str(network) if "/" in clean_target else str(network.network_address)

    except ValueError as err:
        # If the error was one of our explicit restrictions, re-raise it
        if any(
            msg in str(err) for msg in ["exceeds maximum", "prohibited", "disabled"]
        ):
            raise

    # 2. Evaluate as domain name or hostname
    if not DOMAIN_PATTERN.fullmatch(clean_target):
        raise ValueError(
            "Target must be a valid IPv4/IPv6 address, CIDR range, or fully qualified domain name"
        )

    # Ensure hostname resolves via DNS
    try:
        resolved = socket.getaddrinfo(clean_target, None, type=socket.SOCK_STREAM)
        if not resolved:
            raise ValueError(f"Domain '{clean_target}' could not be resolved by DNS")

        # Check resolved IPs for cloud metadata or blocked ranges
        for addr in resolved:
            sockaddr = addr[4]
            ip_str = sockaddr[0]
            if ip_str in CLOUD_METADATA_IPS:
                raise ValueError(
                    f"Target '{clean_target}' resolves to blocked cloud metadata address"
                )
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.is_loopback and not settings.ALLOW_LOOPBACK_SCAN:
                    raise ValueError(
                        f"Target '{clean_target}' resolves to local loopback address"
                    )
                if ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_unspecified:
                    raise ValueError(
                        f"Target '{clean_target}' resolves to restricted network range"
                    )
            except ValueError:
                pass

    except socket.gaierror as e:
        raise ValueError(
            f"Unable to resolve domain '{clean_target}': {e.strerror or 'DNS lookup failed'}"
        ) from e

    return clean_target.lower()
