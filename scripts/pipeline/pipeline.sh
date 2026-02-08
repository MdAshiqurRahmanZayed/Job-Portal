#!/bin/bash

set -e

echo -e '\e[1m\e[34mCurrent directory...\e[0m\n';
echo $PWD;

echo -e '\e[1m\e[34mEntering into main project directory...\e[0m\n';
cd /Job-Portal;
echo $PWD;

echo -e '\e[1m\e[34mConfiguring git safe directory...\e[0m\n';
git config --global --add safe.directory /Job-Portal;

echo -e '\e[1m\e[34mPulling code from remote...\e[0m\n';
git pull origin main;

# Blue-Green Deployment Logic
echo -e '\e[1m\e[34mStarting Blue-Green Deployment...\e[0m\n';

# Detect current active container
CURRENT_COLOR=""
if sudo docker ps --filter "name=job-portal-blue" --format "{{.Names}}" | grep -q "job-portal-blue"; then
    CURRENT_COLOR="blue"
    NEW_COLOR="green"
elif sudo docker ps --filter "name=job-portal-green" --format "{{.Names}}" | grep -q "job-portal-green"; then
    CURRENT_COLOR="green"
    NEW_COLOR="blue"
else
    # First deployment - default to blue
    NEW_COLOR="blue"
    CURRENT_COLOR="none"
fi

echo -e "\e[1m\e[33mCurrent active: $CURRENT_COLOR | Deploying: $NEW_COLOR\e[0m\n";

# Build new image with color tag
echo -e '\e[1m\e[34mBuilding new image...\e[0m\n';
sudo docker build -t job-portal:$NEW_COLOR .;

# Stop and remove existing container of the new color (if exists)
if sudo docker ps -a --filter "name=job-portal-$NEW_COLOR" --format "{{.Names}}" | grep -q "job-portal-$NEW_COLOR"; then
    echo -e '\e[1m\e[34mRemoving old '$NEW_COLOR' container...\e[0m\n';
    sudo docker stop job-portal-$NEW_COLOR || true
    sudo docker rm job-portal-$NEW_COLOR || true
fi

# Start new container
echo -e '\e[1m\e[34mStarting new '$NEW_COLOR' container...\e[0m\n';
sudo docker run -d \
    --name job-portal-$NEW_COLOR \
    --env-file .env \
    -p 9000:9000 \
    -v $(pwd):/app \
    job-portal:$NEW_COLOR \
    python manage.py runserver 0.0.0.0:9000

# Wait for new container to be healthy
echo -e '\e[1m\e[34mWaiting for new container to be ready...\e[0m\n';
sleep 5

# Check if new container is running
if sudo docker ps --filter "name=job-portal-$NEW_COLOR" --format "{{.Names}}" | grep -q "job-portal-$NEW_COLOR"; then
    echo -e '\e[1m\e[32mNew '$NEW_COLOR' container is running successfully!\e[0m\n';

    # Remove old container if exists
    if [ "$CURRENT_COLOR" != "none" ]; then
        echo -e '\e[1m\e[34mRemoving old '$CURRENT_COLOR' container...\e[0m\n';
        sudo docker stop job-portal-$CURRENT_COLOR || true
        sudo docker rm job-portal-$CURRENT_COLOR || true
        echo -e '\e[1m\e[32mOld '$CURRENT_COLOR' container removed!\e[0m\n';
    fi
else
    echo -e '\e[1m\e[31mNew container failed to start! Rolling back...\e[0m\n';
    sudo docker stop job-portal-$NEW_COLOR || true
    sudo docker rm job-portal-$NEW_COLOR || true
    exit 1
fi

# Cleanup old images (keep last 2)
echo -e '\e[1m\e[34mCleaning up old images...\e[0m\n';
sudo docker images job-portal --format "{{.ID}}" | tail -n +3 | xargs -r sudo docker rmi -f || true

echo -e '\e[1m\e[32mBlue-Green Deployment Done! Active: '$NEW_COLOR'\e[0m\n';
