# Vulnerable-to-Remediated Findings

| Finding | Vulnerable evidence target | Remediation | Regression evidence |
|---|---|---|---|
| OS command injection | Builds a command string from `target` and invokes a shell. | Accepts only a JSON string that parses as a literal IP address; no command is executed. | `test_rejects_command_injection` and `test_accepts_literal_ip_addresses` |
| Obsolete application packages | Retains deliberately old Flask, Werkzeug, Requests, and urllib3 versions. | Uses a fully pinned, current runtime dependency set. | Blocking Trivy scan of the remediated image |
| Obsolete container base | Retains Python 3.8 on Debian Buster for historical scanner findings. | Uses Python 3.13 on Alpine and runs Gunicorn. | Blocking remediated image build and scan |
| Root container | No runtime user is declared. | Dedicated UID/GID 10001 in the image and Kubernetes security context. | Repository validator asserts both Dockerfile and manifest controls. |
| Debug server | Starts Flask with debug enabled on all interfaces. | Gunicorn entry point; Flask debug mode is not enabled. | Repository validator asserts target separation. |
| Embedded credential-shaped values | Earlier versions stored synthetic cloud/PAT patterns and a HEC token-shaped value. | Credential-shaped fixtures and operational values are removed; runtime settings come from environment references. | Repository identifier scan |
| Disabled TLS verification | Earlier runtime logging explicitly disabled certificate verification. | Both targets now use Requests' normal certificate verification; the remediated target also requires an HTTPS HEC base URL. | `test_hec_request_uses_default_tls_verification` |
| Public-by-default service | Historical evidence used a public cloud load balancer. | The checked-in Kubernetes service is `ClusterIP`. | Repository validator asserts service type. |
| Ambiguous scanner policy | The only target was intentionally vulnerable, so a green build did not represent a clean release candidate. | Vulnerable findings remain visible in an advisory job; the remediated target has blocking quality and image gates. | GitHub Actions job behavior |

The vulnerable target remains intentionally unsafe so reviewers can inspect the original failure mode. It must not receive real credentials or be exposed outside an isolated, disposable lab.
