#!/bin/bash

sudo redis-cli FLUSHDB
sudo systemctl restart rq_download@1
sudo systemctl restart rq_download@2
sudo systemctl restart rq_download@3
# sudo systemctl restart discordbot.service
sudo systemctl restart rq_sanitize@1
sudo systemctl restart rq_sanitize@2
sudo systemctl restart rq_sanitize@3
sudo systemctl restart rq_noise_reduce
sudo redis-cli FLUSHDB
sudo systemctl restart rq_download@1
sudo systemctl restart rq_download@2
sudo systemctl restart rq_download@3
# sudo systemctl restart discordbot.service
sudo systemctl restart rq_sanitize@1
sudo systemctl restart rq_sanitize@2
sudo systemctl restart rq_sanitize@3
sudo systemctl restart rq_noise_reduce