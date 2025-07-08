#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import shutil
from typing import Dict, Any, Optional, Callable
import weakref
from functools import lru_cache
import time
import logging

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class AsyncDataManager:
    """Optimized data management class with async operations and caching."""
    
    def __init__(self, data_dir: str = 'data', backup_dir: str = 'backup'):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.current_file: Optional[str] = None
        self.current_data: Dict[str, Any] = {}
        
        # Performance optimizations
        self._cache = {}
        self._last_modified = {}
        self._save_queue = asyncio.Queue()
        self._is_saving = False
        self._callbacks = []
        
        # Threading for async operations
        self._executor = ThreadPoolExecutor(max_workers=2)
        
        # Create necessary directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Try to load data from default file
        self.default_file = os.path.join(data_dir, 'current_data.json')
        if os.path.exists(self.default_file):
            self.load_data_sync(self.default_file)
    
    def add_change_callback(self, callback: Callable):
        """Add callback for data change notifications."""
        self._callbacks.append(weakref.ref(callback))
    
    def _notify_callbacks(self, event_type: str, data: Any = None):
        """Notify all registered callbacks of data changes."""
        for callback_ref in self._callbacks[:]:
            callback = callback_ref()
            if callback is None:
                self._callbacks.remove(callback_ref)
            else:
                try:
                    callback(event_type, data)
                except Exception as e:
                    self.logger.error(f"Error in callback: {e}")
    
    @lru_cache(maxsize=128)
    def get_cached_session_id(self, vuelo_data_str: str) -> str:
        """Get session ID with caching for performance."""
        try:
            vuelo_data = json.loads(vuelo_data_str)
            session_id = vuelo_data.get('numero_entrenamiento', '')
            
            if not session_id:
                vuelo_del_ano = vuelo_data.get('vuelo_del_ano', '')
                if vuelo_del_ano:
                    try:
                        num_vuelo = int(vuelo_del_ano)
                        if 0 <= num_vuelo <= 365:
                            year_suffix = datetime.now().strftime("%y")
                            session_id = f"{num_vuelo}-{year_suffix}"
                    except ValueError:
                        self.logger.warning(f"Invalid vuelo_del_ano value: {vuelo_del_ano}")
            
            return session_id
        except Exception as e:
            self.logger.error(f"Error getting cached session ID: {e}")
            return ''

    def get_current_session_id(self) -> str:
        """Get the current session ID with caching."""
        try:
            vuelo_data = self.current_data.get('vuelo', {})
            vuelo_data_str = json.dumps(vuelo_data, sort_keys=True)
            return self.get_cached_session_id(vuelo_data_str)
        except Exception as e:
            self.logger.error(f"Error getting session ID: {e}")
            return ''

    def get_current_session_data(self) -> Dict[str, Any]:
        """Get data for the current session with caching."""
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                return {}
            
            # Check cache first
            cache_key = f"session_data_{session_id}"
            if cache_key in self._cache:
                cache_time = self._last_modified.get(cache_key, 0)
                if time.time() - cache_time < 60:  # Cache for 60 seconds
                    return self._cache[cache_key]
            
            # Get from data
            sessions_data = self.current_data.get('sessions_data', {})
            session_data = sessions_data.get(session_id, {})
            
            # Update cache
            self._cache[cache_key] = session_data
            self._last_modified[cache_key] = time.time()
            
            return session_data
        except Exception as e:
            self.logger.error(f"Error getting session data: {e}")
            return {}

    async def save_session_data_async(self, session_data: Dict[str, Any]) -> bool:
        """Save data for the current session asynchronously."""
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                return False
            
            # Make sure sessions_data exists
            if 'sessions_data' not in self.current_data:
                self.current_data['sessions_data'] = {}
            
            # Update session data
            self.current_data['sessions_data'][session_id] = session_data
            
            # Invalidate cache
            cache_key = f"session_data_{session_id}"
            if cache_key in self._cache:
                del self._cache[cache_key]
                del self._last_modified[cache_key]
            
            # Queue for async save
            await self._save_queue.put(('session_data', session_data))
            self._notify_callbacks('session_data_changed', session_id)
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving session data: {e}")
            return False
    
    def save_session_data(self, session_data: Dict[str, Any]) -> bool:
        """Synchronous wrapper for save_session_data_async."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.save_session_data_async(session_data))
        finally:
            loop.close()
    
    def load_data_sync(self, file_path: Optional[str] = None) -> bool:
        """Load data from a JSON file synchronously."""
        if file_path is None:
            file_path = self.default_file
        
        try:
            if os.path.exists(file_path):
                # Check file modification time for caching
                file_mtime = os.path.getmtime(file_path)
                cache_key = f"file_{file_path}"
                
                if cache_key in self._cache:
                    cached_mtime = self._last_modified.get(cache_key, 0)
                    if file_mtime <= cached_mtime:
                        self.current_data = self._cache[cache_key].copy()
                        self.current_file = file_path
                        return True
                
                # Load file
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                
                # Update cache
                self._cache[cache_key] = self.current_data.copy()
                self._last_modified[cache_key] = file_mtime
                
                self.current_file = file_path
                
                # Ensure session data structure exists
                if 'sessions_data' not in self.current_data:
                    self.current_data['sessions_data'] = {}
                
                # Auto-generate session ID if missing
                self._ensure_session_id()
                
                self.logger.info(f"Data loaded from: {file_path}")
                self._notify_callbacks('data_loaded', file_path)
                return True
            else:
                self.logger.warning(f"File does not exist: {file_path}")
                self.current_data = {'sessions_data': {}}
                self.current_file = file_path
                return False
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            self.current_data = {'sessions_data': {}}
            return False
    
    async def load_data_async(self, file_path: Optional[str] = None) -> bool:
        """Load data from a JSON file asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.load_data_sync, file_path)
    
    def _ensure_session_id(self):
        """Ensure current session has a proper ID."""
        if 'vuelo' in self.current_data:
            vuelo_data = self.current_data['vuelo']
            if not vuelo_data.get('numero_entrenamiento') and vuelo_data.get('vuelo_del_ano'):
                try:
                    vuelo_number = int(vuelo_data['vuelo_del_ano'])
                    if 0 <= vuelo_number <= 365:
                        year_suffix = datetime.now().strftime("%y")
                        vuelo_data['numero_entrenamiento'] = f"{vuelo_number}-{year_suffix}"
                        self.logger.info(f"Generated session ID: {vuelo_data['numero_entrenamiento']}")
                except ValueError:
                    self.logger.warning(f"Invalid vuelo_del_ano: {vuelo_data['vuelo_del_ano']}")
    
    async def save_data_async(self) -> bool:
        """Save current data to file asynchronously."""
        if self._is_saving:
            # Already saving, queue this request
            await self._save_queue.put(('full_save', None))
            return True
        
        self._is_saving = True
        try:
            if not self.current_file:
                self.current_file = self.default_file
            
            # Create backup before saving
            if os.path.exists(self.current_file):
                await self._create_backup_async()
            
            # Ensure sessions_data structure exists
            if 'sessions_data' not in self.current_data:
                self.current_data['sessions_data'] = {}
            
            # Update session data
            self._update_current_session_data()
            
            # Save to file in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self._save_to_file)
            
            # Update cache
            cache_key = f"file_{self.current_file}"
            self._cache[cache_key] = self.current_data.copy()
            self._last_modified[cache_key] = time.time()
            
            self.logger.info(f"Data saved to: {self.current_file}")
            self._notify_callbacks('data_saved', self.current_file)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}")
            return False
        finally:
            self._is_saving = False
    
    def save_data(self) -> bool:
        """Synchronous wrapper for save_data_async."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.save_data_async())
        finally:
            loop.close()
    
    def _save_to_file(self):
        """Save data to file (runs in executor)."""
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_data, f, indent=4)
    
    def _update_current_session_data(self):
        """Update current session data in sessions_data."""
        session_id = self.get_current_session_id()
        
        if session_id:
            if session_id not in self.current_data['sessions_data']:
                self.current_data['sessions_data'][session_id] = {}
            
            session_data = self.current_data['sessions_data'][session_id]
            
            # Copy relevant tab data to the session data
            for key in ['vuelo', 'participantes', 'event_times', 'student_hypoxia_end_times', 
                       'rd', 'reactions_data', 'student_symptoms', 'displayed_calculated_totals']:
                if key in self.current_data:
                    session_data[key] = self.current_data[key].copy()
    
    async def _create_backup_async(self) -> str:
        """Create a backup of the current data file asynchronously."""
        if not self.current_file or not os.path.exists(self.current_file):
            return ""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._backup_file, self.current_file)
    
    def _backup_file(self, source: str) -> str:
        """Create a backup of a file (runs in executor)."""
        if not os.path.exists(source):
            return ""
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(source)
        backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}.bak"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            shutil.copy2(source, backup_path)
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return ""
    
    def create_backup(self) -> str:
        """Create a backup of the current data file."""
        if not self.current_file or not os.path.exists(self.current_file):
            return ""
        return self._backup_file(self.current_file)
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        self._last_modified.clear()
        self.get_cached_session_id.cache_clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        return {
            'cache_size': len(self._cache),
            'cache_hit_ratio': getattr(self.get_cached_session_id, 'cache_info', lambda: {'hits': 0, 'misses': 0})(),
            'last_save_time': max(self._last_modified.values()) if self._last_modified else 0
        }
    
    async def export_to_excel_async(self, file_path: str) -> bool:
        """Export current data to Excel format asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self._executor, self._export_to_excel, file_path)
            return True
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {e}")
            return False
    
    def _export_to_excel(self, file_path: str):
        """Export to Excel (runs in executor)."""
        if HAS_PANDAS:
            df = pd.DataFrame([self.current_data])
            df.to_excel(file_path, index=False)
        else:
            # Fallback to CSV export if pandas not available
            import csv
            with open(file_path.replace('.xlsx', '.csv'), 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if self.current_data:
                    writer.writerow(self.current_data.keys())
                    writer.writerow(self.current_data.values())
    
    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)