"""Unit tests for SSRF-safe target validator and normalizer."""

from unittest.mock import patch
import pytest
from app.scanner.validator import validate_and_normalize_target


def test_valid_ipv4_target():
    target = "192.168.1.1"
    normalized = validate_and_normalize_target(target)
    assert normalized == "192.168.1.1"


def test_valid_cidr_target():
    target = "10.24.18.0/24"
    normalized = validate_and_normalize_target(target)
    assert normalized == "10.24.18.0/24"


def test_valid_domain_target():
    with patch("socket.getaddrinfo") as mock_dns:
        mock_dns.return_value = [(2, 1, 6, "", ("93.184.216.34", 0))]
        target = "example.com"
        normalized = validate_and_normalize_target(target)
        assert normalized == "example.com"


def test_rejection_empty_target():
    with pytest.raises(ValueError, match="required"):
        validate_and_normalize_target("   ")


def test_rejection_cloud_metadata_ip():
    with pytest.raises(ValueError, match="cloud metadata"):
        validate_and_normalize_target("169.254.169.254")


def test_rejection_multicast_ip():
    with pytest.raises(ValueError, match="Multicast"):
        validate_and_normalize_target("224.0.0.1")


def test_rejection_unspecified_ip():
    with pytest.raises(ValueError, match="Unspecified"):
        validate_and_normalize_target("0.0.0.0")


def test_rejection_cidr_too_large():
    # /16 has 65,536 addresses, maximum allowed is 256
    with pytest.raises(ValueError, match="exceeds maximum"):
        validate_and_normalize_target("10.0.0.0/16")


def test_rejection_command_injection_characters():
    injection_attempts = [
        "127.0.0.1; rm -rf /",
        "192.168.1.1 && whoami",
        "10.0.0.1 | cat /etc/passwd",
        "target`id`",
        "$(whoami).evil.com",
    ]
    for attempt in injection_attempts:
        with pytest.raises(ValueError):
            validate_and_normalize_target(attempt)
