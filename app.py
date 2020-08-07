#!/usr/bin/env python3

from aws_cdk import core

from aws_cdk_python.aws_cdk_python_stack import AwsCdkPythonStack


app = core.App()
AwsCdkPythonStack(app, "aws-cdk-python")

app.synth()
