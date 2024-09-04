# External imports
from aws_cdk import (
    aws_certificatemanager,
    aws_ec2,
    aws_elasticloadbalancingv2 as aws_elbv2,
    aws_route53,
    aws_route53_targets,
    Duration,
    CfnOutput,
)
from constructs import Construct

# Own imports
from cdk_backend.common.constants import (
    APP_PORT,
    ALB_PORT,
    INDEXER_PORT,
    MANAGER_PORT_1,
    MANAGER_PORT_2,
    MANAGER_PORT_3,
    DNS_SUBDOMAIN,
)


class NLB(Construct):
    """
    Class to create the Network Load Balancer resources for the servers.
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: aws_ec2.Vpc,
        short_name: str,
        security_group: aws_ec2.SecurityGroup,
        nlb_target: aws_ec2.IInstance,
        hosted_zone_name: str,
    ) -> None:
        """
        :param scope (Construct): Parent of this stack, usually an 'App' or a 'Stage', but could be any construct.
        :param construct_id (str): The construct ID of this stack (same as aws-cdk Stack 'construct_id').
        :param vpc (aws_ec2.Vpc): The VPC where the Security Group will be created.
        :param short_name (str): The short name for the NLB resources.
        :param security_group (aws_ec2.SecurityGroup): The Security Group for the NLB.
        :param nlb_target (aws_ec2.IInstance): The target for the NLB.
        :param hosted_zone_name (str): The hosted zone name for the NLB (e.g. example.com).
        """
        super().__init__(scope, construct_id)

        self.vpc = vpc
        self.short_name = short_name
        self.security_group = security_group
        self.nlb_target = nlb_target
        self.hosted_zone_name = hosted_zone_name

        # Main methods to create and configure the ALB
        self.create_nlb()
        self.import_route_53_hosted_zone()
        self.configure_acm_certificate()
        self.configure_nlb_listeners()
        self.configure_target_groups()
        self.configure_route_53_records()

    def create_nlb(self):
        """
        Method to create the Network Load Balancer for the UI.
        """
        self.nlb = aws_elbv2.NetworkLoadBalancer(
            self,
            "LoadBalancer",
            vpc=self.vpc,
            internet_facing=True,
            load_balancer_name=self.short_name,
            security_group=self.security_group,
        )

    def import_route_53_hosted_zone(self):
        """
        Method to import the Route 53 hosted zone for the application.
        """
        # IMPORTANT: The hosted zone must be already created in Route 53!
        self.hosted_zone_name = self.hosted_zone_name
        self.domain_name = f"{DNS_SUBDOMAIN}.{self.hosted_zone_name}"
        self.hosted_zone = aws_route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=self.hosted_zone_name,
        )

    def configure_acm_certificate(self):
        """
        Method to configure the SSL certificate for the ALB.
        """
        self.certificate = aws_certificatemanager.Certificate(
            self,
            "Certificate",
            domain_name=self.domain_name,
            validation=aws_certificatemanager.CertificateValidation.from_dns(
                hosted_zone=self.hosted_zone,
            ),
        )

    def configure_nlb_listeners(self):
        """
        Method to configure the NLB listeners for the Dashboard, Indexer and Manager.
        """
        # Main HTTPS Listener for the NLB
        self.https_listener = self.nlb.add_listener(
            "NLB-Dashboard-Listener",
            port=APP_PORT,
            protocol=aws_elbv2.Protocol.HTTP,
            certificates=[self.certificate],
        )

        # Listener for the Indexer
        self.indexer_listener = self.nlb.add_listener(
            "NLB-Indexer-Listener",
            port=INDEXER_PORT,
            protocol=aws_elbv2.Protocol.TCP,
            certificates=[self.certificate],
        )

        # Listeners for the Manager
        self.manager_1_listener = self.nlb.add_listener(
            "NLB-Manager-Listener-1",
            port=MANAGER_PORT_1,
            protocol=aws_elbv2.Protocol.TCP_UDP,
            certificates=[self.certificate],
        )
        self.manager_2_listener = self.nlb.add_listener(
            "NLB-Manager-Listener-2",
            port=MANAGER_PORT_2,
            protocol=aws_elbv2.Protocol.TCP_UDP,
            certificates=[self.certificate],
        )
        self.manager_3_listener = self.nlb.add_listener(
            "NLB-Manager-Listener-3",
            port=MANAGER_PORT_3,
            protocol=aws_elbv2.Protocol.TCP_UDP,
            certificates=[self.certificate],
        )

    def configure_target_groups(self):
        """
        Method to configure the target groups for the NLB.
        """
        # Dashboard Target Group
        self.https_listener_target_group = self.https_listener.add_targets(
            "NLB-Dashboard-TargetGroup",
            port=APP_PORT,  # Intentionally set to Application Port for the ASG
            protocol=aws_elbv2.Protocol.HTTPS,
            targets=[self.nlb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.HTTPS,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )

        # Indexer Target Group
        self.indexer_listener_target_group = self.indexer_listener.add_targets(
            "NLB-Indexer-TargetGroup",
            port=INDEXER_PORT,
            protocol=aws_elbv2.Protocol.TCP,
            targets=[self.nlb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.TCP,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )

        # Manager Target Groups
        self.manager_1_listener_target_group = self.manager_1_listener.add_targets(
            "NLB-Manager-TargetGroup-1",
            port=MANAGER_PORT_1,
            protocol=aws_elbv2.Protocol.TCP_UDP,
            targets=[self.nlb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.TCP_UDP,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )
        self.manager_2_listener_target_group = self.manager_2_listener.add_targets(
            "NLB-Manager-TargetGroup-2",
            port=MANAGER_PORT_2,
            protocol=aws_elbv2.Protocol.TCP,
            targets=[self.nlb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.TCP,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )
        self.manager_3_listener_target_group = self.manager_3_listener.add_targets(
            "NLB-Manager-TargetGroup-3",
            port=MANAGER_PORT_3,
            protocol=aws_elbv2.Protocol.TCP,
            targets=[self.nlb_target],
            health_check=aws_elbv2.HealthCheck(
                path="/",
                protocol=aws_elbv2.Protocol.TCP,
                timeout=Duration.seconds(15),
                interval=Duration.minutes(5),
            ),
        )

    def configure_route_53_records(self):
        """
        Method to configure the Route 53 records for the ALB.
        """
        aws_route53.ARecord(
            self,
            "NLB-Record",
            zone=self.hosted_zone,
            target=aws_route53.RecordTarget.from_alias(
                aws_route53_targets.LoadBalancerTarget(self.nlb)
            ),
            record_name=self.domain_name,
            comment=f"NLB DNS for {self.domain_name} for {self.short_name} application",
        )

        # Outputs for the custom domain and NLB DNS
        CfnOutput(
            self,
            "APP-DNS",
            value=f"https://{self.domain_name}",
            description="Application custom DNS",
        )
        CfnOutput(
            self,
            "NLB-DNS",
            value=f"https://{self.nlb.load_balancer_dns_name}",
            description="NLB DNS",
        )
