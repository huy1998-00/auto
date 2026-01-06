"""
Resource monitoring utilities for CPU and memory usage.

Provides monitoring for auto-throttling based on CPU usage.
"""

import psutil
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class ResourceUsage:
    """Current resource usage snapshot."""

    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float


class ResourceMonitor:
    """
    Monitor system resources for auto-throttling.

    Tracks CPU and memory usage to enable automatic
    screenshot frequency reduction when CPU > 80%.
    """

    def __init__(
        self,
        cpu_throttle_threshold: float = 80.0,
        sample_interval: float = 0.1,
    ):
        """
        Initialize resource monitor.

        Args:
            cpu_throttle_threshold: CPU percentage threshold for throttling
            sample_interval: Interval for CPU measurement in seconds
        """
        self.cpu_throttle_threshold = cpu_throttle_threshold
        self.sample_interval = sample_interval
        self._last_cpu_percent = 0.0

    def get_cpu_percent(self) -> float:
        """
        Get current CPU usage percentage.

        Returns:
            CPU usage percentage (0-100)
        """
        # Use interval=None for non-blocking call
        # This returns the CPU percent since last call
        cpu_percent = psutil.cpu_percent(interval=None)
        self._last_cpu_percent = cpu_percent
        return cpu_percent

    def get_memory_info(self) -> Dict[str, float]:
        """
        Get current memory usage information.

        Returns:
            Dictionary with memory usage stats
        """
        memory = psutil.virtual_memory()
        return {
            "percent": memory.percent,
            "used_mb": memory.used / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "total_mb": memory.total / (1024 * 1024),
        }

    def get_resource_usage(self) -> ResourceUsage:
        """
        Get current resource usage snapshot.

        Returns:
            ResourceUsage dataclass with CPU and memory info
        """
        cpu_percent = self.get_cpu_percent()
        memory = psutil.virtual_memory()

        return ResourceUsage(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024),
        )

    def should_throttle(self) -> bool:
        """
        Check if screenshot frequency should be reduced.

        Returns:
            True if CPU usage exceeds threshold (80%)
        """
        cpu_percent = self.get_cpu_percent()
        return cpu_percent > self.cpu_throttle_threshold

    def get_throttle_factor(self) -> float:
        """
        Get throttle factor based on CPU usage.

        Returns a multiplier for screenshot interval:
        - 1.0 = normal frequency
        - 1.5 = 50% slower when CPU 80-90%
        - 2.0 = 100% slower when CPU > 90%

        Returns:
            Throttle factor multiplier
        """
        cpu_percent = self._last_cpu_percent

        if cpu_percent <= self.cpu_throttle_threshold:
            return 1.0
        elif cpu_percent <= 90:
            return 1.5
        else:
            return 2.0

    def get_adjusted_interval(self, base_interval_ms: int) -> int:
        """
        Get adjusted screenshot interval based on CPU usage.

        Args:
            base_interval_ms: Base interval in milliseconds

        Returns:
            Adjusted interval in milliseconds
        """
        factor = self.get_throttle_factor()
        return int(base_interval_ms * factor)

    def get_status_string(self) -> str:
        """
        Get human-readable status string for UI display.

        Returns:
            Status string like "CPU: 45% | Memory: 62%"
        """
        usage = self.get_resource_usage()
        throttle_status = " [THROTTLED]" if self.should_throttle() else ""
        return (
            f"CPU: {usage.cpu_percent:.1f}%{throttle_status} | "
            f"Memory: {usage.memory_percent:.1f}%"
        )

    def get_status_dict(self) -> Dict[str, any]:
        """
        Get status as dictionary for UI updates.

        Returns:
            Dictionary with resource status
        """
        usage = self.get_resource_usage()
        return {
            "cpu_percent": usage.cpu_percent,
            "memory_percent": usage.memory_percent,
            "memory_used_mb": usage.memory_used_mb,
            "memory_available_mb": usage.memory_available_mb,
            "is_throttled": self.should_throttle(),
            "throttle_factor": self.get_throttle_factor(),
        }
