@echo off
Start "docker" /B "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout 50
start docker container start %1
exit