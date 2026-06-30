import psutil

class ResourceMonitor:
    def snapshot(self) -> dict:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_mb": psutil.virtual_memory().used / (1024 * 1024),
            "disk_percent": psutil.disk_usage("/").percent,
        }
