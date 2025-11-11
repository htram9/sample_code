import torch
import time
import statistics
from typing import Callable, Dict, Any, List, Optional
from contextlib import contextmanager

import logging
from SimpleLogger import SimpleLogger


class PyTorchPerformanceTester:
    m_logger : SimpleLogger

    """Test and benchmark PyTorch function performance."""
    
    def __init__(self, logger : SimpleLogger, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        Initialize the performance tester.
        
        Args:
            device: Device to run tests on ('cuda' or 'cpu')
        """
        self.m_logger = logger

        self.device = torch.device(device)
        print(f"Using device: {self.device}")
        if self.device.type == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    @contextmanager
    def timer(self):
        """Context manager for timing code blocks."""
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()
        yield
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        end = time.perf_counter()
        self.elapsed_time = end - start
    
    def benchmark_function(
        self,
        func: Callable,
        *args,
        warmup_runs: int = 10,
        test_runs: int = 100,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Benchmark a PyTorch function.
        
        Args:
            func: Function to benchmark
            *args: Positional arguments for the function
            warmup_runs: Number of warmup iterations
            test_runs: Number of test iterations
            **kwargs: Keyword arguments for the function
            
        Returns:
            Dictionary with timing statistics
        """
        # Warmup runs
        for _ in range(warmup_runs):
            _ = func(*args, **kwargs)
        
        if self.device.type == "cuda":
            torch.cuda.synchronize()
        
        # Benchmark runs
        times = []
        for _ in range(test_runs):
            with self.timer():
                _ = func(*args, **kwargs)
            times.append(self.elapsed_time)
        
        return {
            "mean_ms": statistics.mean(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
            "std_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "total_runs": test_runs,
        }
    
    def compare_functions(
        self,
        functions: Dict[str, Callable],
        *args,
        warmup_runs: int = 10,
        test_runs: int = 100,
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare performance of multiple functions.
        
        Args:
            functions: Dictionary of {name: function} to compare
            *args: Positional arguments for the functions
            warmup_runs: Number of warmup iterations
            test_runs: Number of test iterations
            **kwargs: Keyword arguments for the functions
            
        Returns:
            Dictionary with results for each function
        """
        results = {}
        for name, func in functions.items():
            print(f"\nBenchmarking: {name}")
            results[name] = self.benchmark_function(
                func, *args, warmup_runs=warmup_runs, test_runs=test_runs, **kwargs
            )
            print(f"  Mean: {results[name]['mean_ms']:.4f} ms")
            print(f"  Std:  {results[name]['std_ms']:.4f} ms")
        
        return results
    
    def profile_memory(self, func: Callable, *args, **kwargs) -> Dict[str, float]:
        """
        Profile memory usage of a function (CUDA only).
        
        Args:
            func: Function to profile
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Dictionary with memory statistics in MB
        """
        if self.device.type != "cuda":
            return {"error": "Memory profiling only available for CUDA"}
        
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        
        mem_before = torch.cuda.memory_allocated() / 1024**2
        _ = func(*args, **kwargs)
        torch.cuda.synchronize()
        
        mem_after = torch.cuda.memory_allocated() / 1024**2
        peak_mem = torch.cuda.max_memory_allocated() / 1024**2
        
        return {
            "allocated_mb": mem_after - mem_before,
            "peak_mb": peak_mem,
        }
    
    def print_results(self, results: Dict[str, Dict[str, Any]]):
        """Pretty print benchmark results."""
        print("\n" + "="*70)
        print("PERFORMANCE COMPARISON")
        print("="*70)
        
        for name, stats in results.items():
            self.m_logger.info(f"\n{name}:")
            self.m_logger.info(f"  Mean:   {stats['mean_ms']:>10.4f} ms")
            self.m_logger.info(f"  Median: {stats['median_ms']:>10.4f} ms")
            self.m_logger.info(f"  Std:    {stats['std_ms']:>10.4f} ms")
            self.m_logger.info(f"  Min:    {stats['min_ms']:>10.4f} ms")
            self.m_logger.info(f"  Max:    {stats['max_ms']:>10.4f} ms")
        
        # Find fastest
        fastest = min(results.items(), key=lambda x: x[1]['mean_ms'])
        self.m_logger.info(f"\nFastest: {fastest[0]} ({fastest[1]['mean_ms']:.4f} ms)")


# Example usage
if __name__ == "__main__":
    logger = SimpleLogger(
        name="PYTorchPerformanceTester",
        log_file="logs/PYTorchPerformanceTester.log",
        level=logging.DEBUG
    )

    # Initialize tester
    tester = PyTorchPerformanceTester(logger)
    
    # Create test data
    batch_size, seq_len, hidden_dim = 32, 128, 512
    x = torch.randn(batch_size, seq_len, hidden_dim).to(tester.device)
    
    # Define functions to test
    def method_matmul(x):
        return torch.matmul(x, x.transpose(-2, -1))
    
    def method_bmm(x):
        return torch.bmm(x, x.transpose(-2, -1))
    
    def method_einsum(x):
        return torch.einsum('bik,bjk->bij', x, x)
    
    # Benchmark single function
    logger.info("\n--- Single Function Benchmark ---")
    result = tester.benchmark_function(method_matmul, x, warmup_runs=10, test_runs=100)
    logger.info(f"Mean time: {result['mean_ms']:.4f} ms")
    logger.info(f"Std dev: {result['std_ms']:.4f} ms")
    
    # Compare multiple functions
    print("\n--- Function Comparison ---")
    functions = {
        "torch.matmul": method_matmul,
        "torch.bmm": method_bmm,
        "torch.einsum": method_einsum,
    }
    results = tester.compare_functions(functions, x, warmup_runs=10, test_runs=100)
    tester.print_results(results)
    
    # Memory profiling (if CUDA available)
    if tester.device.type == "cuda":
        logger.info("\n--- Memory Profiling ---")
        mem_stats = tester.profile_memory(method_matmul, x)
        logger.info(f"Memory allocated: {mem_stats['allocated_mb']:.2f} MB")
        logger.info(f"Peak memory: {mem_stats['peak_mb']:.2f} MB")
        