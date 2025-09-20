from logger import log_publish

def getjournalctl_logs(service):
    import subprocess
    try:
        logs = subprocess.check_output(['journalctl', '-n', '50', '--no-pager', '-u', service]).decode('utf-8')
        logs = logs.strip()
        #limit logs to last 1995 characters
        if len(logs) > 1995:
            logs = logs[-1995:]
        log_publish(f"[journalctl] Retrieved logs for service {service}")
        log_publish(logs)
    except Exception as e:
        return f"Error retrieving logs: {str(e)}"
    
def restart_system():
    #execute restart.sh
    import subprocess
    try:
        subprocess.run(['/home/azureuser/podcat-processor/restart.sh'], check=True)
        log_publish("[restart] System services restarted successfully.")
    except Exception as e:
        log_publish(f"[restart] Error restarting services: {str(e)}")
    return "Restart command executed."
