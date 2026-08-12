# Test architecture

Each Molecule scenario uses the standard lifecycle: dependency, create, prepare,
converge, idempotence where applicable, side effect, verify, cleanup, and destroy.

- `system` validates package installation and a full stable role converge on every
  supported distribution. It uses nested Docker with the `vfs` storage driver.
- `api` exercises Remnawave v3 and Cloudflare create, unchanged, update, duplicate,
  rotation, and malformed-response paths against `fixtures/mock-api`.
- `firewall` owns a disposable network namespace, confirms `flush ruleset`, tests
  whitelist precedence, and protects the last-known-good configuration.
- `tags` invokes the actual role entrypoint with public tags and checks restart and
  fake-site regeneration contracts.
- `warp` uses deterministic command stubs; no real WARP account or license is used.
- `ssh` opens two disposable sshd targets and tests password/master-key bootstrap,
  service-key login, idempotence, host-key behavior, and serial failure handling.

Production HTTP calls are redirected only by scenario inventory variables. The mock
API request journal stores method, path, and JSON body but never Authorization
headers. CI captures verbose output and rejects all known sentinel secrets.

`requirements-test.txt` and `requirements-lint.txt` declare isolated toolchains;
their exact versions are pinned in the adjacent constraints files.
