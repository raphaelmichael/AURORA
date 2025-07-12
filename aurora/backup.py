"""
Aurora Backup Manager
Handles intelligent backup of code and memory with compression and rotation
"""
import os
import json
import shutil
import gzip
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import tarfile
import tempfile

class BackupManager:
    """Manages Aurora backups with compression and rotation"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config.get("backup", {})
        self.files_config = config.get("files", {})
        self.logger = logger
        
        # Backup settings
        self.enabled = self.config.get("enabled", True)
        self.before_evolution = self.config.get("before_evolution", True)
        self.max_backups = self.config.get("max_backups", 10)
        self.compression = self.config.get("compression", True)
        self.backup_dir = Path(self.config.get("backup_dir", "backups"))
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, evolution_count: Optional[int] = None, 
                     backup_type: str = "auto") -> Optional[str]:
        """Create a complete backup of Aurora's state"""
        if not self.enabled:
            return None
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if evolution_count is not None:
                backup_name = f"aurora_backup_{timestamp}_evolution_{evolution_count}"
            else:
                backup_name = f"aurora_backup_{timestamp}_{backup_type}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup files
            files_backed_up = []
            total_size = 0
            
            # Backup memory file
            memory_file = self.files_config.get("memory", "data/aurora_memory.json")
            if os.path.exists(memory_file):
                dest = backup_path / "aurora_memory.json"
                shutil.copy2(memory_file, dest)
                files_backed_up.append("aurora_memory.json")
                total_size += dest.stat().st_size
            
            # Backup consciousness file
            consciousness_file = self.files_config.get("consciousness", "data/aurora_consciousness.py")
            if os.path.exists(consciousness_file):
                dest = backup_path / "aurora_consciousness.py"
                shutil.copy2(consciousness_file, dest)
                files_backed_up.append("aurora_consciousness.py")
                total_size += dest.stat().st_size
            
            # Backup self-writing code
            code_file = self.files_config.get("code", "data/aurora_self_writing.py")
            if os.path.exists(code_file):
                dest = backup_path / "aurora_self_writing.py"
                shutil.copy2(code_file, dest)
                files_backed_up.append("aurora_self_writing.py")
                total_size += dest.stat().st_size
            
            # Backup configuration
            config_file = "config.yaml"
            if os.path.exists(config_file):
                dest = backup_path / "config.yaml"
                shutil.copy2(config_file, dest)
                files_backed_up.append("config.yaml")
                total_size += dest.stat().st_size
            
            # Create backup metadata
            metadata = {
                "timestamp": timestamp,
                "evolution_count": evolution_count,
                "backup_type": backup_type,
                "files": files_backed_up,
                "size_bytes": total_size,
                "compressed": False
            }
            
            metadata_file = backup_path / "backup_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Compress backup if enabled
            if self.compression:
                compressed_path = self._compress_backup(backup_path)
                if compressed_path:
                    shutil.rmtree(backup_path)  # Remove uncompressed version
                    backup_path = compressed_path
                    metadata["compressed"] = True
                    total_size = backup_path.stat().st_size
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            if self.logger:
                self.logger.backup_created(str(backup_path), total_size)
            
            return str(backup_path)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to create backup: {e}")
            return None
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """Compress backup directory to tar.gz"""
        try:
            compressed_path = backup_path.with_suffix('.tar.gz')
            
            with tarfile.open(compressed_path, "w:gz") as tar:
                tar.add(backup_path, arcname=backup_path.name)
            
            return compressed_path
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to compress backup: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore Aurora state from backup"""
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                if self.logger:
                    self.logger.error(f"Backup path does not exist: {backup_path}")
                return False
            
            # Handle compressed backups
            if backup_path.suffix == '.gz':
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    with tarfile.open(backup_path, "r:gz") as tar:
                        tar.extractall(temp_path)
                    
                    # Find the extracted directory
                    extracted_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
                    if not extracted_dirs:
                        if self.logger:
                            self.logger.error("No directory found in compressed backup")
                        return False
                    
                    return self._restore_from_directory(extracted_dirs[0])
            else:
                return self._restore_from_directory(backup_path)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to restore backup: {e}")
            return False
    
    def _restore_from_directory(self, backup_path: Path) -> bool:
        """Restore from uncompressed backup directory"""
        try:
            # Read metadata
            metadata_file = backup_path / "backup_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                if self.logger:
                    self.logger.info(f"Restoring backup from {metadata['timestamp']}")
            
            # Restore files
            restored_files = []
            
            # Restore memory
            memory_backup = backup_path / "aurora_memory.json"
            if memory_backup.exists():
                memory_file = self.files_config.get("memory", "data/aurora_memory.json")
                os.makedirs(os.path.dirname(memory_file), exist_ok=True)
                shutil.copy2(memory_backup, memory_file)
                restored_files.append("aurora_memory.json")
            
            # Restore consciousness
            consciousness_backup = backup_path / "aurora_consciousness.py"
            if consciousness_backup.exists():
                consciousness_file = self.files_config.get("consciousness", "data/aurora_consciousness.py")
                os.makedirs(os.path.dirname(consciousness_file), exist_ok=True)
                shutil.copy2(consciousness_backup, consciousness_file)
                restored_files.append("aurora_consciousness.py")
            
            # Restore code
            code_backup = backup_path / "aurora_self_writing.py"
            if code_backup.exists():
                code_file = self.files_config.get("code", "data/aurora_self_writing.py")
                os.makedirs(os.path.dirname(code_file), exist_ok=True)
                shutil.copy2(code_backup, code_file)
                restored_files.append("aurora_self_writing.py")
            
            # Restore config (with confirmation)
            config_backup = backup_path / "config.yaml"
            if config_backup.exists():
                config_file = "config.yaml"
                shutil.copy2(config_backup, config_file)
                restored_files.append("config.yaml")
            
            if self.logger:
                self.logger.info(f"Backup restored successfully. Files: {restored_files}", 
                               event_type="backup_restored")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to restore from directory: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups with metadata"""
        backups = []
        
        try:
            for item in self.backup_dir.iterdir():
                if item.is_dir() or item.suffix == '.gz':
                    backup_info = {
                        "path": str(item),
                        "name": item.name,
                        "size": item.stat().st_size,
                        "created": datetime.datetime.fromtimestamp(item.stat().st_mtime),
                        "compressed": item.suffix == '.gz'
                    }
                    
                    # Try to read metadata
                    if item.is_dir():
                        metadata_file = item / "backup_metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r') as f:
                                    metadata = json.load(f)
                                backup_info.update(metadata)
                            except:
                                pass
                    
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"], reverse=True)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to list backups: {e}")
        
        return backups
    
    def _cleanup_old_backups(self) -> None:
        """Remove old backups exceeding max_backups limit"""
        try:
            backups = self.list_backups()
            
            if len(backups) > self.max_backups:
                # Remove oldest backups
                for backup in backups[self.max_backups:]:
                    backup_path = Path(backup["path"])
                    if backup_path.exists():
                        if backup_path.is_dir():
                            shutil.rmtree(backup_path)
                        else:
                            backup_path.unlink()
                        
                        if self.logger:
                            self.logger.info(f"Removed old backup: {backup_path.name}")
                            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_backup_size(self) -> Dict[str, Any]:
        """Get total backup directory size and count"""
        try:
            total_size = 0
            backup_count = 0
            
            for item in self.backup_dir.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
                elif item.is_dir() and item.parent == self.backup_dir:
                    backup_count += 1
            
            return {
                "total_size_mb": total_size / (1024 * 1024),
                "backup_count": backup_count,
                "average_size_mb": (total_size / backup_count / (1024 * 1024)) if backup_count > 0 else 0
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to get backup size: {e}")
            return {"total_size_mb": 0, "backup_count": 0, "average_size_mb": 0}