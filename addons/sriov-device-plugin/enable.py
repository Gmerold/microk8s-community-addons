import json
import os
import subprocess
import tempfile

import click

KUBECTL = os.path.expandvars("$SNAP/microk8s-kubectl.wrapper")


@click.command()
@click.option(
    "--resources",
    required=True,
    type=dict,
    help="{\"${RESOURCE_NAME\": \"${PCI_ADDRESS}\"}"
)
def main(resources):
    resources_list = [
        {"resrouceName": resource_name, "selectors": {"pciAddress": [pci_address]}}
        for resource_name, pci_address in resources.items()
    ]

    sriovdp_config_manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "sriovdp-config",
            "namespace": "kube-config"
        },
        "data": {
            "config.json": {
                "resourceList": json.dumps(resources_list)
            }
        }
    }

    click.echo("Enabling SRIOV device plugin...")

    with tempfile.NamedTemporaryFile(mode="w+") as sriovdp_config:
        json.dump(sriovdp_config_manifest, sriovdp_config)
        sriovdp_config.flush()

        subprocess.check_call([KUBECTL, "apply", "-f", sriovdp_config.name])
    subprocess.check_call([KUBECTL, "apply", "-f", "sriovdp.yaml"])

    click.echo("Enabled SRIOV device plugin.")


if __name__ == "__main__":
    main()
