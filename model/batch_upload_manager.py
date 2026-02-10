"""
WordPress Batch Upload Manager - HIGH VOLUME MODE
Optimized for 200+ posts with batch processing and smart rate limiting
"""

import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple, Callable, Optional
import json
import os


class BatchUploadManager:
    """
    Quản lý upload hàng loạt với batch processing
    Tối ưu cho 200+ bài viết
    """
    
    def __init__(
        self,
        batch_size: int = 20,
        max_parallel_batches: int = 3,
        max_workers_per_batch: int = 5,
        checkpoint_file: str = "upload_checkpoint.json"
    ):
        """
        Args:
            batch_size: Số bài/batch (default: 20)
            max_parallel_batches: Số batches chạy song song (default: 3)
            max_workers_per_batch: Số uploads song song/batch (default: 5)
            checkpoint_file: File lưu progress
        """
        self.batch_size = batch_size
        self.max_parallel_batches = max_parallel_batches
        self.max_workers_per_batch = max_workers_per_batch
        self.checkpoint_file = checkpoint_file
        
        # Statistics
        self.total_posts = 0
        self.completed_posts = 0
        self.failed_posts = []
        self.start_time = None
        
        # Queues
        self.retry_queue = queue.Queue()
        
        # Locks
        self.stats_lock = threading.Lock()
        
        print(f"[BATCH_MGR] 🚀 Initialized HIGH VOLUME mode")
        print(f"[BATCH_MGR] Config: batch_size={batch_size}, parallel_batches={max_parallel_batches}")
    
    def process_posts_batch(
        self,
        posts: List[Dict],
        upload_func: Callable,
        progress_callback: Optional[Callable] = None
    ) -> Tuple[int, int, List[Dict]]:
        """
        Xử lý hàng loạt posts với batch processing
        
        Args:
            posts: List of post data dicts
            upload_func: Function to upload a single post (post_data) -> (success, result)
            progress_callback: Optional callback(completed, total, eta)
            
        Returns:
            (success_count, failed_count, failed_posts)
        """
        self.total_posts = len(posts)
        self.completed_posts = 0
        self.failed_posts = []
        self.start_time = time.time()
        
        print(f"[BATCH_MGR] 📦 Processing {self.total_posts} posts...")
        print(f"[BATCH_MGR] 🔧 Batch size: {self.batch_size}")
        print(f"[BATCH_MGR] ⚡ Parallel batches: {self.max_parallel_batches}")
        
        # Chia thành batches
        batches = self._split_into_batches(posts)
        total_batches = len(batches)
        
        print(f"[BATCH_MGR] 📊 Split into {total_batches} batches")
        
        # Process batches in parallel
        completed_batches = 0
        
        with ThreadPoolExecutor(max_workers=self.max_parallel_batches) as executor:
            # Submit all batches
            future_to_batch = {
                executor.submit(
                    self._process_single_batch,
                    batch_idx,
                    batch,
                    upload_func,
                    total_batches
                ): batch_idx
                for batch_idx, batch in enumerate(batches, 1)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    batch_success, batch_failed = future.result()
                    completed_batches += 1
                    
                    # Update progress
                    if progress_callback:
                        eta = self._calculate_eta()
                        progress_callback(self.completed_posts, self.total_posts, eta)
                    
                    # Save checkpoint
                    self._save_checkpoint()
                    
                except Exception as e:
                    print(f"[BATCH_MGR] ❌ Batch {batch_idx} error: {e}")
        
        # Process retry queue
        if not self.retry_queue.empty():
            print(f"[BATCH_MGR] 🔄 Retrying {self.retry_queue.qsize()} failed posts...")
            self._process_retry_queue(upload_func)
        
        # Final stats
        elapsed = time.time() - self.start_time
        success_count = self.completed_posts - len(self.failed_posts)
        
        print(f"\n[BATCH_MGR] ✅ COMPLETED!")
        print(f"[BATCH_MGR] 📊 Success: {success_count}/{self.total_posts}")
        print(f"[BATCH_MGR] ❌ Failed: {len(self.failed_posts)}")
        print(f"[BATCH_MGR] ⏱️ Time: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
        print(f"[BATCH_MGR] 🚀 Speed: {self.total_posts/elapsed*60:.1f} posts/minute")
        
        return success_count, len(self.failed_posts), self.failed_posts
    
    def _split_into_batches(self, posts: List[Dict]) -> List[List[Dict]]:
        """Chia posts thành batches"""
        batches = []
        for i in range(0, len(posts), self.batch_size):
            batch = posts[i:i + self.batch_size]
            batches.append(batch)
        return batches
    
    def _process_single_batch(
        self,
        batch_idx: int,
        batch: List[Dict],
        upload_func: Callable,
        total_batches: int
    ) -> Tuple[int, int]:
        """
        Xử lý 1 batch
        
        Returns:
            (success_count, failed_count)
        """
        batch_size = len(batch)
        print(f"[BATCH {batch_idx}/{total_batches}] 🚀 Processing {batch_size} posts...")
        
        batch_start = time.time()
        batch_success = 0
        batch_failed = 0
        
        # Process posts in this batch (parallel within batch)
        with ThreadPoolExecutor(max_workers=self.max_workers_per_batch) as executor:
            future_to_post = {
                executor.submit(upload_func, post): post
                for post in batch
            }
            
            for future in as_completed(future_to_post):
                post = future_to_post[future]
                try:
                    success, result = future.result()
                    
                    with self.stats_lock:
                        self.completed_posts += 1
                        
                        if success:
                            batch_success += 1
                        else:
                            batch_failed += 1
                            self.failed_posts.append({
                                'post': post,
                                'error': result
                            })
                            # Add to retry queue
                            self.retry_queue.put(post)
                    
                    # Progress
                    progress = (self.completed_posts / self.total_posts) * 100
                    print(f"[BATCH {batch_idx}] Progress: {self.completed_posts}/{self.total_posts} ({progress:.1f}%)")
                    
                except Exception as e:
                    print(f"[BATCH {batch_idx}] ❌ Post error: {e}")
                    batch_failed += 1
                    with self.stats_lock:
                        self.completed_posts += 1
                        self.failed_posts.append({
                            'post': post,
                            'error': str(e)
                        })
        
        batch_elapsed = time.time() - batch_start
        print(f"[BATCH {batch_idx}] ✅ Done: {batch_success} success, {batch_failed} failed ({batch_elapsed:.1f}s)")
        
        return batch_success, batch_failed
    
    def _process_retry_queue(self, upload_func: Callable):
        """Retry failed posts"""
        retry_count = 0
        max_retries = min(self.retry_queue.qsize(), 10)  # Max 10 retries
        
        while not self.retry_queue.empty() and retry_count < max_retries:
            try:
                post = self.retry_queue.get_nowait()
                print(f"[RETRY] Retrying post: {post.get('title', 'Unknown')[:30]}...")
                
                success, result = upload_func(post)
                if success:
                    print(f"[RETRY] ✅ Success!")
                    # Remove from failed list
                    self.failed_posts = [f for f in self.failed_posts if f['post'] != post]
                else:
                    print(f"[RETRY] ❌ Still failed: {result}")
                
                retry_count += 1
                time.sleep(1)  # Wait between retries
                
            except queue.Empty:
                break
    
    def _calculate_eta(self) -> float:
        """Tính ETA (giây)"""
        if self.completed_posts == 0:
            return 0
        
        elapsed = time.time() - self.start_time
        avg_time_per_post = elapsed / self.completed_posts
        remaining_posts = self.total_posts - self.completed_posts
        eta = avg_time_per_post * remaining_posts
        
        return eta
    
    def _save_checkpoint(self):
        """Lưu progress vào file"""
        try:
            checkpoint = {
                'total': self.total_posts,
                'completed': self.completed_posts,
                'failed': len(self.failed_posts),
                'timestamp': time.time()
            }
            
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, indent=2)
                
        except Exception as e:
            print(f"[CHECKPOINT] ⚠️ Save error: {e}")
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Load checkpoint từ file"""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                    print(f"[CHECKPOINT] 📂 Loaded: {checkpoint['completed']}/{checkpoint['total']} completed")
                    return checkpoint
        except Exception as e:
            print(f"[CHECKPOINT] ⚠️ Load error: {e}")
        
        return None


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 BATCH UPLOAD MANAGER - HIGH VOLUME MODE")
    print("=" * 60)
    print()
    
    # Example: 200 posts
    test_posts = [
        {'title': f'Post {i}', 'content': f'Content {i}'}
        for i in range(1, 201)
    ]
    
    # Mock upload function
    def mock_upload(post):
        """Simulate upload"""
        time.sleep(0.1)  # Simulate network delay
        # 95% success rate
        import random
        success = random.random() > 0.05
        return success, "OK" if success else "Error"
    
    # Create manager
    manager = BatchUploadManager(
        batch_size=20,           # 20 posts/batch
        max_parallel_batches=3,  # 3 batches song song
        max_workers_per_batch=5  # 5 uploads/batch
    )
    
    # Process
    def progress_callback(completed, total, eta):
        print(f"[PROGRESS] {completed}/{total} ({completed/total*100:.1f}%) - ETA: {eta:.0f}s")
    
    success, failed, failed_posts = manager.process_posts_batch(
        test_posts,
        mock_upload,
        progress_callback
    )
    
    print()
    print("=" * 60)
    print("✅ TEST COMPLETE")
    print(f"Success: {success}, Failed: {failed}")
    print("=" * 60)
