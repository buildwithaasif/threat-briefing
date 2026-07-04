"""Lightweight batch processor to avoid sequential LLM bottleneck"""
import concurrent.futures
from typing import Callable, List

def process_in_parallel(items: List, func: Callable, max_workers: int = 4, desc: str = "Processing"):
    """Process items in parallel with progress indication"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(func, item): item for item in items}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                print(f"  ✓ {desc}")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
    
    return results
