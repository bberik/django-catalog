#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment process..."

# Build Docker image
echo "📦 Building Docker image..."
docker build -t catalog-dev-repo .

# Tag Docker image
echo "🏷️  Tagging Docker image..."
docker tag catalog-dev-repo:latest 044529651970.dkr.ecr.eu-north-1.amazonaws.com/catalog-dev-repo:latest

# Push to ECR
echo "⬆️  Pushing to ECR..."
docker push 044529651970.dkr.ecr.eu-north-1.amazonaws.com/catalog-dev-repo:latest

# Update ECS Task Definition and Force New Deployment
echo "🔄 Updating ECS service..."

# Get the current task definition
TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition catalog-dev-task --region eu-north-1)

# Create new container definition with updated image
NEW_CONTAINER_DEFINITION=$(echo $TASK_DEFINITION | jq --arg IMAGE "044529651970.dkr.ecr.eu-north-1.amazonaws.com/catalog-dev-repo:latest" '.taskDefinition.containerDefinitions[0].image = $IMAGE | .taskDefinition.containerDefinitions[0]')

# Register new task definition
aws ecs register-task-definition \
  --region eu-north-1 \
  --family catalog-dev-task \
  --container-definitions "$NEW_CONTAINER_DEFINITION" \
  --cpu "512" \
  --memory "1024" \
  --execution-role-arn "arn:aws:iam::044529651970:role/ecsTaskExecutionRole" \
  --task-role-arn "arn:aws:iam::044529651970:role/ecsTaskExecutionRole" \
  --requires-compatibilities "FARGATE" \
  --network-mode awsvpc

# Update service with new task definition
aws ecs update-service \
  --region eu-north-1 \
  --cluster catalog-dev-cluster \
  --service catalog-dev-service \
  --task-definition catalog-dev-task \
  --enable-execute-command

echo "✅ Deployment completed successfully!" 