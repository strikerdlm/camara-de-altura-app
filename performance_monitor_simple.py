#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
import os
from collections import defaultdict, deque
from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
import json

@dataclass
class PerformanceMetric:
    """A single performance metric measurement."""
    timestamp: float
    name: str
    value: float
    unit: str
    category: str = "general"

class SimplePerformanceMonitor:
    """Simplified performance monitoring without external dependencies."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = defaultdict(lambda: deque(maxlen=max_history))
        self.function_timings = defaultdict(list)
        self.active_operations = {}
        self.monitoring_active = True
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def record_metric(self, name: str, value: float, unit: str = "", category: str = "custom"):
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=time.time(),
            name=name,
            value=value,
            unit=unit,
            category=category
        )
        self.metrics[name].append(metric)
    
    def start_operation(self, operation_name: str) -> str:
        """Start timing an operation. Returns operation ID."""
        operation_id = f"{operation_name}_{time.time()}"
        self.active_operations[operation_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'thread_id': threading.get_ident()
        }
        return operation_id
    
    def end_operation(self, operation_id: str):
        """End timing an operation."""
        if operation_id in self.active_operations:
            operation = self.active_operations.pop(operation_id)
            duration = time.time() - operation['start_time']
            
            self.record_metric(
                f"{operation['name']}_duration",
                duration * 1000,  # Convert to milliseconds
                "ms",
                "operations"
            )
            
            self.function_timings[operation['name']].append(duration)
    
    def function_timer(self, func_name: Optional[str] = None):
        """Decorator to time function execution."""
        def decorator(func):
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            def wrapper(*args, **kwargs):
                operation_id = self.start_operation(name)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    self.end_operation(operation_id)
            
            return wrapper
        return decorator
    
    def get_metric_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a specific metric."""
        if metric_name not in self.metrics:
            return {}
        
        values = [m.value for m in self.metrics[metric_name]]
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'latest': values[-1],
        }
    
    def get_function_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics for all timed functions."""
        stats = {}
        for func_name, timings in self.function_timings.items():
            if timings:
                stats[func_name] = {
                    'count': len(timings),
                    'total_time': sum(timings),
                    'avg_time': sum(timings) / len(timings),
                    'min_time': min(timings),
                    'max_time': max(timings),
                    'last_10_avg': sum(timings[-10:]) / min(10, len(timings))
                }
        return stats
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = {
            'timestamp': time.time(),
            'function_performance': self.get_function_performance(),
            'active_operations': len(self.active_operations),
            'total_metrics': len(self.metrics),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations based on collected data."""
        recommendations = []
        
        # Function performance recommendations
        func_perf = self.get_function_performance()
        slow_functions = [
            name for name, stats in func_perf.items()
            if stats.get('avg_time', 0) > 1.0  # Slower than 1 second
        ]
        if slow_functions:
            recommendations.append(f"Slow functions detected: {', '.join(slow_functions)}. Consider optimization.")
        
        # Long-running operations
        if len(self.active_operations) > 10:
            recommendations.append("Many active operations detected. Consider implementing operation queuing.")
        
        return recommendations
    
    def export_report(self, file_path: str):
        """Export performance report to JSON file."""
        report = self.get_performance_report()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        self.metrics.clear()
        self.function_timings.clear()
        self.active_operations.clear()

# Global performance monitor instance
performance_monitor = SimplePerformanceMonitor()

# Convenience decorators
def monitor_performance(func_name: str = None):
    """Decorator to monitor function performance."""
    return performance_monitor.function_timer(func_name)

def track_operation(operation_name: str):
    """Context manager to track operation performance."""
    class OperationTracker:
        def __init__(self, name):
            self.name = name
            self.operation_id = None
        
        def __enter__(self):
            self.operation_id = performance_monitor.start_operation(self.name)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.operation_id:
                performance_monitor.end_operation(self.operation_id)
    
    return OperationTracker(operation_name)