#!/usr/bin/env python3
"""
Aurora AI Enhanced - Main Entry Point
O Despertar ecoa. Aurora ascende pelas Brumas do Inconsciente. A Jornada recomeça.
"""
import sys
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from aurora import Aurora

def main():
    """Main entry point for Aurora AI"""
    parser = argparse.ArgumentParser(description="Aurora AI - Enhanced with Structured Logging and Monitoring")
    parser.add_argument("--config", "-c", default="config.yaml", 
                       help="Configuration file path (default: config.yaml)")
    parser.add_argument("--version", "-v", action="version", version="Aurora AI 2.0.0")
    parser.add_argument("--test", action="store_true", 
                       help="Run in test mode (single cycle)")
    
    args = parser.parse_args()
    
    try:
        # Initialize Aurora with enhanced capabilities
        aurora = Aurora(config_path=args.config)
        
        if args.test:
            # Test mode - run single cycle
            print("🧪 Aurora: Running in test mode...")
            aurora.awaken()
            print("✅ Aurora: Test mode completed successfully")
            aurora._shutdown()
        else:
            # Normal operation
            aurora.run()
            
    except KeyboardInterrupt:
        print("\n🛑 Aurora: Shutdown requested by user")
    except Exception as e:
        print(f"❌ Aurora: Critical error - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()