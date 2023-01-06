#!/usr/bin/env python3

import aws_cdk as cdk
from backup_stack import BackupStack


app = cdk.App()

props = {
    "namespace": app.node.try_get_context("namespace")
}

BackupStack(app, "BackupStack", props=props, description=f"Backup of {props['namespace']}-stack")

app.synth()
