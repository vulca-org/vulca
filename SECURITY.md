# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest master | :white_check_mark: |
| older commits | :x:                |

Only the latest version on the `master` branch receives security updates.

## Reporting a Vulnerability

If you discover a security vulnerability in VULCA, please report it responsibly:

1. **Email**: [yuhaorui48@gmail.com](mailto:yuhaorui48@gmail.com)
2. **Subject line**: `[VULCA Security] <brief description>`
3. **Include**: Steps to reproduce, affected component, potential impact

### Response Timeline

| Stage | Timeframe |
|-------|-----------|
| Acknowledgement | Within **72 hours** |
| Initial assessment | Within **7 days** |
| Fix or mitigation | Within **30 days** |
| Public disclosure | After fix is deployed |

We will coordinate disclosure timing with the reporter.

## Out of Scope

The following are **not** considered vulnerabilities:

- Demo account credentials (`demo/demo123`, `admin/admin123`) — these are intentional test accounts
- Mock data in the repository (sample YAML traditions, seed data)
- Rate limiting on the demo instance (intentionally relaxed for evaluation)
- Self-signed certificates in local development
- Dependencies with CVEs that do not affect VULCA's usage of that dependency

## Security Best Practices for Contributors

- **Never** commit `.env` files, API keys, or credentials
- Use `.env.example` files with placeholder values
- Store secrets in GitHub Secrets or your cloud provider's secret manager
- Rotate API keys regularly — see the deployment guide for key rotation procedures
- Use `constraints.txt` to pin Python dependency versions

## Acknowledgements

We appreciate responsible disclosure and will credit reporters (with permission) in release notes.

## License

This security policy applies to the VULCA project licensed under Apache 2.0.
