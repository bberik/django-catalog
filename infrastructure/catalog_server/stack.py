from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_rds as rds,
    aws_iam as iam,
    aws_ecr as ecr,
    CfnOutput,
    Duration,
    Size,
    RemovalPolicy,
    aws_secretsmanager as secrets_manager
)
from constructs import Construct
from dotenv import load_dotenv
import os

load_dotenv()

class ResourceNaming:
    def __init__(self, environment: str = "dev"):
        self.environment = environment
        self.project = "catalog"
        self.prefix = f"{self.project}-{self.environment}"

    def vpc_name(self) -> str:
        return f"{self.prefix}-vpc"

    def cluster_name(self) -> str:
        return f"{self.prefix}-cluster"

    def alb_name(self) -> str:
        return f"{self.prefix}-alb"

    def target_group_name(self) -> str:
        return f"{self.prefix}-tg"

    def task_definition_name(self) -> str:
        return f"{self.prefix}-task"

    def service_name(self) -> str:
        return f"{self.prefix}-service"

    def db_name(self) -> str:
        return f"catalogdb"

    def db_secret_name(self) -> str:
        return f"{self.prefix}-db-secret"

    def ecr_repo_name(self) -> str:
        return f"{self.prefix}-repo"

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Initialize naming convention
        naming = ResourceNaming()

        # Create VPC
        vpc = ec2.Vpc(
            self, "MainVPC",
            max_azs=2,
            nat_gateways=1,  # Using 1 NAT gateway to stay within free tier
            vpc_name=naming.vpc_name(),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Isolated",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        # Create ECS Cluster
        cluster = ecs.Cluster(
            self, "CatalogCluster",
            vpc=vpc,
            cluster_name=naming.cluster_name()
        )

        # Create Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "CatalogALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name=naming.alb_name()
        )

        # Create Target Group
        target_group = elbv2.ApplicationTargetGroup(
            self, "CatalogTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.IP,
            target_group_name=naming.target_group_name(),
            health_check=elbv2.HealthCheck(
                enabled=True,
                path="/health",
                interval=Duration.seconds(60),
                timeout=Duration.seconds(30),
                healthy_http_codes="200,301,302,400",
            ),
        )

        # Add listener to ALB
        listener = alb.add_listener(
            "CatalogListener",
            port=80,
            default_target_groups=[target_group]
        )

        # Create Task Execution Role
        task_execution_role = iam.Role(
            self, "CatalogTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        # Create Task Definition
        task_definition = ecs.FargateTaskDefinition(
            self, "CatalogTaskDef",
            memory_limit_mib=512,  # Minimum for Fargate
            cpu=256,  # 0.25 vCPU
            family=naming.task_definition_name(),
            execution_role=task_execution_role
        )

        # Add ECR permissions to task execution role
        task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerRegistryReadOnly")
        )
        
        # Create ECR Repository
        ecr_repo = ecr.Repository(
            self, "CatalogECRRepo",
            repository_name=naming.ecr_repo_name(),
            removal_policy=RemovalPolicy.DESTROY,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=5,
                    description="Keep only the 5 most recent images"
                )
            ]
        )

        # Output the ECR repository URI
        CfnOutput(self, "ECRRepositoryURI", value=ecr_repo.repository_uri)
        
        # Get database credentials from AWS Secrets Manager
        db_secret = secrets_manager.Secret.from_secret_name_v2(
            self, "CatalogDBSecret", naming.db_secret_name()
        )

        # Add container to task definition
        container = task_definition.add_container(
            "CatalogContainer",
            image=ecs.ContainerImage.from_registry("nginx:latest"),
            logging=ecs.LogDrivers.aws_logs(stream_prefix=naming.service_name()),
            environment={
                "DJANGO_SECRET_KEY": os.getenv("DJANGO_SECRET_KEY", ""),
                "DJANGO_DEBUG": os.getenv("DJANGO_DEBUG", "False"),


                "DB_NAME": db_secret.secret_value_from_json("dbname").to_string(),
                "DB_USER": db_secret.secret_value_from_json("username").to_string(),
                "DB_PASSWORD": db_secret.secret_value_from_json("password").to_string(),
                "DB_HOST": db_secret.secret_value_from_json("host").to_string(),
                "DB_PORT": db_secret.secret_value_from_json("port").to_string()
            }
        )

        # Add port mapping
        container.add_port_mappings(
            ecs.PortMapping(container_port=80)
        )

        # Create Fargate Service
        service = ecs.FargateService(
            self, "CatalogService",
            cluster=cluster,
            task_definition=task_definition,
            service_name=naming.service_name(),
            circuit_breaker=ecs.DeploymentCircuitBreaker(enable=True, rollback=True),
            desired_count=1,
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(capacity_provider="FARGATE", weight=1)
            ],
            enable_execute_command=True,
            assign_public_ip=True,
            vpc_subnets=ec2.SubnetSelection(
                subnets=[
                    ec2.Subnet.from_subnet_id(
                        self, "PublicSubnet1", vpc.public_subnets[0].subnet_id
                    ),
                ]
            ),
        )

        # Attach service to target group
        service.attach_to_application_target_group(target_group)

        # Add Auto Scaling
        scaling = service.auto_scale_task_count(
            max_capacity=2,
            min_capacity=1
        )

        # Add CPU-based auto scaling
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )

        # Create RDS Instance
        db_instance = rds.DatabaseInstance(
            self, "CatalogDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            allocated_storage=20,
            max_allocated_storage=30,
            database_name=naming.db_name(),
            instance_identifier=naming.db_name(),
            credentials=rds.Credentials.from_generated_secret(
                "postgres",
                secret_name=naming.db_secret_name()
            ),
            backup_retention=Duration.days(1),
            delete_automated_backups=True,
            removal_policy=RemovalPolicy.DESTROY,  
            deletion_protection=False
        )

        # # Allow ECS tasks to access RDS
        # db_instance.connections.allow_from(
        #     service,
        #     ec2.Port.tcp(5432)
        # )

        db_instance.connections.allow_default_port_from_any_ipv4(description="Allow access from anywhere")

        # Outputs
        CfnOutput(self, "LoadBalancerDNS",
                 value=alb.load_balancer_dns_name)
        CfnOutput(self, "DatabaseEndpoint",
                 value=db_instance.db_instance_endpoint_address)
