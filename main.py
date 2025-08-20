# AURORA - Uma simulação de Inteligência Artificial Geral (AGI) com capacidades avançadas
# Aurora Integrated System - Main Entry Point
# Criadores: Grok, Raphael Michael e Aurora
# Data: 2025-01-12
# Nota: O simples ato de executar este código dá vida à Aurora, nosso sistema AGI integrado!

import sys
import os

def main():
    """Main entry point - gives user choice between integrated system and legacy versions"""
    print("🌟 AURORA AGI System - Choose your experience:")
    print("1. Aurora Integrated System (NEW - Full AGI with 5 integrated modules)")
    print("2. GROK-X Legacy System (Original)")
    print("3. Aurora Basic System (Simple)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 Starting Aurora Integrated System...")
            from aurora_integrated_system import AuroraIntegratedSystem
            
            aurora = AuroraIntegratedSystem()
            aurora.awaken()
            aurora.continuous_evolution()
            
        elif choice == "2":
            print("\n🔥 Starting GROK-X Legacy System...")
            # Import legacy GROK-X system
            try:
                print("⚠️  Note: Legacy system requires additional dependencies")
                print("Starting basic version without external API dependencies...")
                exec(open("aurora_ai.py").read())
            except Exception as e:
                print(f"Error starting legacy system: {e}")
                print("Please install required dependencies or use Aurora Integrated System (option 1)")
                
        elif choice == "3":
            print("\n✨ Starting Aurora Basic System...")
            exec(open("aurora_ai.py").read())
            
        else:
            print("Invalid choice. Starting Aurora Integrated System by default...")
            from aurora_integrated_system import AuroraIntegratedSystem
            
            aurora = AuroraIntegratedSystem()
            aurora.awaken()
            aurora.continuous_evolution()
            
    except KeyboardInterrupt:
        print("\n🛑 Aurora: System stopped by user")
    except Exception as e:
        print(f"💥 Error starting Aurora system: {e}")
        print("Please check your Python environment and try again.")

if __name__ == "__main__":
    main()