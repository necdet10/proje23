"""
NBA Player Ranking Pipeline Orchestrator - FIXED VERSION
"""

import sys
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Any

# ------------------------------
# Pipeline Steps - GÜNCEL YOLLAR
# ------------------------------
PIPELINE_STEPS: List[Dict[str, Any]] = [
    {
        "name": "Data Collection",
        "script": "01_data_collection.py",
        "description": "Kaggle'dan NBA verilerini indir",
    },
    {
        "name": "Data Preprocessing", 
        "script": "02_data_preprocessing.py",
        "description": "Veriyi temizle ve düzenle",
    },
    {
        "name": "Feature Engineering",
        "script": "03_feature_engineering.py",
        "description": "PCA feature extraction",
    },
    {
        "name": "Model Training",
        "script": "04_moel_training.py",  # Burada typo var ama dosya adı böyle
        "description": "LOF modeli eğit",
    },
    {
        "name": "Model Evaluation",
        "script": "05_model_evalution.py",  # Burada da typo var ama dosya adı böyle
        "description": "Oyuncu sıralaması oluştur",
    }
]

# ------------------------------
# Color Codes
# ------------------------------
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

# Renkleri kontrol et
if os.name == "nt" or not sys.stdout.isatty():
    for attr in dir(Colors):
        if not attr.startswith("_"):
            setattr(Colors, attr, "")

# ------------------------------
# Helper Functions
# ------------------------------
def print_banner(text: str, char: str = "=") -> None:
    width = 70
    print("\n" + char * width)
    print(f"  {text.center(width - 4)}")
    print(char * width + "\n")

def find_script(script_name: str) -> str:
    """Script dosyasını bul"""
    # Önce mevcut dizinde ara
    if os.path.exists(script_name):
        return os.path.abspath(script_name)
    
    # src/ klasöründe ara
    src_path = os.path.join("src", script_name)
    if os.path.exists(src_path):
        return os.path.abspath(src_path)
    
    # Sadece dosya adı verilmişse ara
    for root, dirs, files in os.walk("."):
        if script_name in files:
            return os.path.abspath(os.path.join(root, script_name))
    
    return None

def run_step(step_name: str, script_name: str, description: str) -> bool:
    """Run a single pipeline step"""
    print(f"{Colors.OKGREEN}🚀 Starting: {step_name}{Colors.ENDC}")
    print(f"📄 Looking for: {script_name}")
    print(f"📝 Description: {description}")
    print("-" * 70)

    start_time = time.time()

    try:
        # Script dosyasını bul
        script_path = find_script(script_name)
        
        if not script_path or not os.path.exists(script_path):
            print(f"{Colors.FAIL}❌ Script not found: {script_name}{Colors.ENDC}")
            print(f"{Colors.WARNING}Searched in:{Colors.ENDC}")
            print(f"  - Current directory: ./{script_name}")
            print(f"  - src directory: ./src/{script_name}")
            print(f"  - All subdirectories")
            return False

        print(f"{Colors.OKGREEN}✅ Found script: {script_path}{Colors.ENDC}")

        # Run the script
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Stream output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        # Check for errors
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"{Colors.WARNING}Stderr: {stderr_output}{Colors.ENDC}")

        return_code = process.wait()
        elapsed = time.time() - start_time

        if return_code == 0:
            print(f"\n{Colors.OKGREEN}✅ {step_name} completed in {elapsed:.2f}s{Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.FAIL}❌ {step_name} failed after {elapsed:.2f}s{Colors.ENDC}")
            print(f"{Colors.FAIL}Exit code: {return_code}{Colors.ENDC}")
            return False

    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n{Colors.WARNING}⚠️  {step_name} interrupted after {elapsed:.2f}s{Colors.ENDC}")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n{Colors.FAIL}❌ {step_name} failed after {elapsed:.2f}s{Colors.ENDC}")
        print(f"{Colors.FAIL}Exception: {str(e)}{Colors.ENDC}")
        return False

def run_full_pipeline() -> int:
    """Run all pipeline steps"""
    print_banner("🏀 NBA PLAYER RANKING PIPELINE - FIXED", "=")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Scripts will be searched in current directory and subdirectories")

    total_start = time.time()
    failed_steps = []
    completed_steps = []

    # Mevcut dosyaları listele (debug için)
    print(f"\n{Colors.OKCYAN}Current directory files:{Colors.ENDC}")
    for file in os.listdir("."):
        if file.endswith(".py"):
            print(f"  - {file}")

    # Her step'i çalıştır
    for i, step in enumerate(PIPELINE_STEPS, 1):
        print(f"\n{Colors.OKBLUE}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}STEP {i}/{len(PIPELINE_STEPS)}: {step['name']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{step['description']}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'=' * 70}{Colors.ENDC}\n")

        success = run_step(step["name"], step["script"], step["description"])

        if success:
            completed_steps.append(step["name"])
        else:
            failed_steps.append(step["name"])
            print(f"\n{Colors.WARNING}⚠️  Pipeline failed at: {step['name']}{Colors.ENDC}")
            
            # Kullanıcıya devam etmek isteyip istemediğini sor
            if i < len(PIPELINE_STEPS):
                response = input(f"{Colors.WARNING}Continue with next step? (y/n): {Colors.ENDC}").strip().lower()
                if response != 'y':
                    break

    # Özet
    total_elapsed = time.time() - total_start
    print_banner("PIPELINE SUMMARY", "=")

    print(f"{Colors.BOLD}Completed: {len(completed_steps)}/{len(PIPELINE_STEPS)}{Colors.ENDC}")
    for step in completed_steps:
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {step}")

    if failed_steps:
        print(f"\n{Colors.BOLD}Failed:{Colors.ENDC}")
        for step in failed_steps:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {step}")

    print(f"\n{Colors.BOLD}Total Time: {total_elapsed:.2f}s{Colors.ENDC}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0 if not failed_steps else 1

def list_steps() -> None:
    """List all available pipeline steps"""
    print_banner("AVAILABLE PIPELINE STEPS", "=")

    for i, step in enumerate(PIPELINE_STEPS, 1):
        print(f"{Colors.BOLD}{i}. {step['name']}{Colors.ENDC}")
        print(f"   Script: {step['script']}")
        print(f"   Description: {step['description']}\n")

    print(f"{Colors.OKCYAN}Usage:{Colors.ENDC}")
    print(f"  python run_pipeline.py          # Run full pipeline")
    print(f"  python run_pipeline.py --list   # List steps")
    print(f"  python run_pipeline.py --help   # Show help")

def main() -> int:
    """Main entry point"""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["-h", "--help", "help"]:
            list_steps()
            return 0
        elif arg in ["-l", "--list", "list"]:
            list_steps()
            return 0
        else:
            print(f"{Colors.FAIL}Unknown argument: {arg}{Colors.ENDC}")
            list_steps()
            return 1

    return run_full_pipeline()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Pipeline interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)