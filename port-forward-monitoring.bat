@echo off
setlocal

set NAMESPACE=smokestack
set PROMETHEUS_SERVICE=prometheus-service
set GRAFANA_SERVICE=grafana-service

where kubectl >nul 2>&1
if errorlevel 1 (
    echo kubectl was not found on PATH.
    echo Install kubectl or open this from a terminal where kubectl is available.
    pause
    exit /b 1
)

echo Starting SmokeStack monitoring port-forwards...
echo.
echo Prometheus: http://localhost:9090
echo Grafana:    http://localhost:3000
echo.
echo Close the opened windows or press Ctrl+C inside them to stop forwarding.
echo.

start "SmokeStack Prometheus" cmd /k kubectl port-forward service/%PROMETHEUS_SERVICE% 9090:9090 -n %NAMESPACE%
start "SmokeStack Grafana" cmd /k kubectl port-forward service/%GRAFANA_SERVICE% 3000:3000 -n %NAMESPACE%

endlocal
