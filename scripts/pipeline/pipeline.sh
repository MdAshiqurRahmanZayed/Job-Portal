#!/bin/bash

echo -e '\e[1m\e[34mCurrent directory...\e[0m\n';
echo $PWD;

echo -e '\e[1m\e[34mEntering into main project directory...\e[0m\n';
cd /home/ubuntu/Job-Portal;
echo $PWD;

echo -e '\e[1m\e[34mPulling code from remote...\e[0m\n';
git pull origin main;

echo -e '\e[1m\e[34mBuilding image...\e[0m\n';
docker build .;

echo -e '\e[1m\e[34mPushing image to internal hub...\e[0m\n';
docker-compose -f docker-compose.yml up --build;

echo -e '\e[1m\e[34mDeployment Done!\e[0m\n';
