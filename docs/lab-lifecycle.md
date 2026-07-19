# Lab Lifecycle and Teardown

## Current state

The environment used for the original exercise was dismantled after completion. Repository screenshots and configuration are historical evidence, not proof of live infrastructure.

## Before a future run

1. Use a disposable AWS account or tightly scoped sandbox.
2. Set an AWS Budget and alert before creating EKS or NAT Gateway resources.
3. Choose a currently supported EKS version explicitly; the Terraform module intentionally has no version default.
4. Review the Terraform plan and Kubernetes manifests independently.
5. Keep the vulnerable target private. Prefer local Docker networking or `kubectl port-forward` for demonstrations.
6. Create Splunk configuration out of band. Do not commit HEC tokens, endpoint tunnels, account IDs, or generated kubeconfig files.
7. Record an owner and teardown time before applying infrastructure.

## Teardown checklist

1. Delete any Kubernetes `LoadBalancer` resources first and wait for cloud load balancers to disappear.
2. Remove test images and confirm no unrelated images depend on the ECR repository.
3. Run `terraform destroy` against the same reviewed state and variables used for creation.
4. Confirm EKS clusters, node groups, NAT gateways, elastic IPs, load balancers, log groups, and ECR repositories are gone.
5. Revoke temporary credentials and Splunk HEC tokens.
6. Remove temporary DNS or tunnel endpoints.
7. Preserve only sanitized evidence and note the completion date.

Never run teardown commands against an unreviewed account, workspace, or state file.
