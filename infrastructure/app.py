#!/usr/bin/env python3
import os

import aws_cdk as cdk

from catalog_server.stack import InfrastructureStack


env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

app = cdk.App()
InfrastructureStack(app, "InfrastructureStack", env=env)

app.synth()
