#!/bin/bash

set -e

echo -e '\e[1m\e[34mCurrent directory...\e[0m\n';
echo $PWD;

echo -e '\e[1m\e[34mEntering into main project directory...\e[0m\n';
cd /Job-Portal;
echo $PWD;

echo -e '\e[1m\e[34mConfiguring git safe directory...\e[0m\n';
sudo git config --global --add safe.directory /Job-Portal;

echo -e '\e[1m\e[34mPulling code from remote...\e[0m\n';
sudo git pull origin main;

# Blue-Green Deployment Logic
echo -e '\e[1m\e[34mStarting Blue-Green Deployment...\e[0m\n';

# Detect current active container
CURRENT_COLOR=""
NEW_COLOR=""
CURRENT_PORT=""
NEW_PORT=""

if sudo docker ps --filter "name=job-portal-blue" --filter "status=running" --format "{{.Names}}" | grep -q "job-portal-blue"; then
    CURRENT_COLOR="blue"
    NEW_COLOR="green"
    CURRENT_PORT="9000"
    NEW_PORT="9001"
    echo -e "\e[1m\e[33mDetected blue running on port 9000\e[0m\n";
elif sudo docker ps --filter "name=job-portal-green" --filter "status=running" --format "{{.Names}}" | grep -q "job-portal-green"; then
    CURRENT_COLOR="green"
    NEW_COLOR="blue"
    CURRENT_PORT="9001"
    NEW_PORT="9000"
    echo -e "\e[1m\e[33mDetected green running on port 9001\e[0m\n";
else
    # First deployment - default to blue on 9000
    NEW_COLOR="blue"
    CURRENT_COLOR="none"
    NEW_PORT="9000"
    CURRENT_PORT=""
    echo -e "\e[1m\e[33mFirst deployment - starting blue on port 9000\e[0m\n";
fi

echo -e "\e[1m\e[33mCurrent active: $CURRENT_COLOR:$CURRENT_PORT | Deploying: $NEW_COLOR:$NEW_PORT\e[0m\n";

# Build new image with timestamp tag
TIMESTAMP=$(date +%s)
echo -e '\e[1m\e[34mBuilding new image...\e[0m\n';
sudo docker build -t job-portal:$NEW_COLOR-$TIMESTAMP .;
sudo docker tag job-portal:$NEW_COLOR-$TIMESTAMP job-portal:$NEW_COLOR;

# Stop and remove existing container of the new color (if exists from previous failed deployment)
if sudo docker ps -a --filter "name=job-portal-$NEW_COLOR" --format "{{.Names}}" | grep -q "job-portal-$NEW_COLOR"; then
    echo -e '\e[1m\e[34mCleaning up existing '$NEW_COLOR' container...\e[0m\n';
    sudo docker stop job-portal-$NEW_COLOR 2>/dev/null || true
    sudo docker rm job-portal-$NEW_COLOR 2>/dev/null || true
    sleep 2
fi

# Start new container on alternate port
echo -e '\e[1m\e[34mStarting new '$NEW_COLOR' container on port '$NEW_PORT'...\e[0m\n';
sudo docker run -d \
    --name job-portal-$NEW_COLOR \
    --env-file .env \
    -p $NEW_PORT:9000 \
    -v $(pwd):/app \
    --restart unless-stopped \
    job-portal:$NEW_COLOR \
    python manage.py runserver 0.0.0.0:9000

# Wait for new container to be ready
echo -e '\e[1m\e[34mWaiting for new container to be ready...\e[0m\n';
sleep 10

# Health check with retries
MAX_RETRIES=15
RETRY_COUNT=0
HEALTH_CHECK_PASSED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s http://localhost:$NEW_PORT/ > /dev/null 2>&1; then
        echo -e '\e[1m\e[32mHealth check passed!\e[0m\n';
        HEALTH_CHECK_PASSED=true
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "\e[1m\e[33mHealth check attempt $RETRY_COUNT/$MAX_RETRIES...\e[0m";
    sleep 2
done

# Check if new container is running and healthy
if [ "$HEALTH_CHECK_PASSED" = true ] && sudo docker ps --filter "name=job-portal-$NEW_COLOR" --format "{{.Names}}" | grep -q "job-portal-$NEW_COLOR"; then
    echo -e '\e[1m\e[32mNew '$NEW_COLOR' container is running successfully!\e[0m\n';

    # Nginx automatically handles both ports via upstream config
    # No need to update Nginx configuration on each deployment!

    # Wait for traffic to stabilize on new container
    echo -e '\e[1m\e[34mWaiting for traffic to stabilize...\e[0m\n';
    sleep 5

    # Remove old container if exists
    if [ "$CURRENT_COLOR" != "none" ]; then
        echo -e '\e[1m\e[34mStopping old '$CURRENT_COLOR' container...\e[0m\n';
        sudo docker stop job-portal-$CURRENT_COLOR 2>/dev/null || true
        sleep 2
        sudo docker rm job-portal-$CURRENT_COLOR 2>/dev/null || true
        echo -e '\e[1m\e[32mOld '$CURRENT_COLOR' container removed!\e[0m\n';
    fi
else
    echo -e '\e[1m\e[31mNew container failed health checks! Rolling back...\e[0m\n';
    echo -e '\e[1m\e[31mContainer logs:\e[0m\n';
    sudo docker logs job-portal-$NEW_COLOR || true
    sudo docker stop job-portal-$NEW_COLOR 2>/dev/null || true
    sudo docker rm job-portal-$NEW_COLOR 2>/dev/null || true
    exit 1
fi

# Cleanup old images (keep last 3 tagged versions)
echo -e '\e[1m\e[34mCleaning up old images...\e[0m\n';
sudo docker images job-portal --format "{{.ID}} {{.Tag}}" | grep -v "blue\|green" | awk '{print $1}' | tail -n +4 | xargs -r sudo docker rmi -f 2>/dev/null || true

echo -e '\e[1m\e[32m========================================\e[0m';
echo -e '\e[1m\e[32mBlue-Green Deployment Done!\e[0m';
echo -e '\e[1m\e[32mActive: '$NEW_COLOR' on port '$NEW_PORT'\e[0m';
echo -e '\e[1m\e[32m========================================\e[0m\n';
