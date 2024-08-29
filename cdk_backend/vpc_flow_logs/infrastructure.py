# External imports
from aws_cdk import aws_ec2, aws_logs, aws_iam
from constructs import Construct

# Own imports
from cdk_backend.vpc.infrastructure import VPC


class VPCFlowLogs(Construct):
    """
    Class to create the VPC Flow Logs resources for a given VPC.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc_construct: VPC,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc_construct (VPC): The VPC construct to be used in this stack.
        """
        super().__init__(scope, construct_id)

        # CW Log Group for VPC Flow Logs
        log_group = aws_logs.LogGroup(
            self,
            "CWLogGroup",
            log_group_name=f"vpc-flow-logs/{vpc_construct.vpc.vpc_id}",
            retention=aws_logs.RetentionDays.ONE_WEEK,
        )
        role = aws_iam.Role(
            self,
            "CWLogRole",
            assumed_by=aws_iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        )

        # Enable VPC Flow Logs
        vpc_construct.vpc.add_flow_log(
            "VPCFlowLog",
            traffic_type=aws_ec2.FlowLogTrafficType.ALL,
            destination=aws_ec2.FlowLogDestination.to_cloud_watch_logs(log_group, role),
        )
