import sys
import os
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Any, Optional 
from pathlib import Path

# Proje kök dizinini belirler
PROJECT_ROOT = Path(__file__).parent.resolve()

# ------------------------------
# Pipeline Adımları
# ------------------------------
PIPELINE_STEPS: List[Dict[str, Any]] = [
    {"name": "Data Collection (Aşama 1)", "script": "a1_data_collection.py",
     "description": "Kaggle'dan NBA verilerini indir ve data/raw klasörüne kaydet."},
    {"name": "Data Preprocessing (Aşama 2)", "script": "a2_data_preprocessing.py",
     "description": "Veriyi temizle, eksik değerleri doldur ve ön işleme tabi tut."},
    {"name": "Feature Engineering (Aşama 3)", "script": "a3_feature_engineering.py",
     "description": "Yeni oyuncu özellikleri çıkar ve PCA ile boyut indirgeme yap."},
    {"name": "Model Training (Aşama 4)", "script": "a4_model_training.py",
     "description": "Anomali tespiti veya kümeleme modeli eğit."},
    {"name": "Model Evaluation (Aşama 5)", "script": "a5_model_evaluation.py",
     "description": "Model performansını değerlendir ve nihai oyuncu sıralamasını oluştur."},
    {"name": "LLM Reporting (Aşama 6)", "script": "a6_llm_reporting.py",
     "description": "Oluşturulan sıralamayı ve metrikleri kullanarak Streamlit LLM raporu hazırla."}
]

# ------------------------------
# Renk Kodları
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

if os.name == "nt" or not sys.stdout.isatty():
    for attr in dir(Colors):
        if not attr.startswith("_"):
            setattr(Colors, attr, "")

# ------------------------------
# Yardımcı Fonksiyonlar
# ------------------------------
def print_banner(text: str, char: str = "=") -> None:
    width = 70
    print("\n" + char * width)
    print(f"  {text.center(width - 4)}")
    print(char * width + "\n")

def find_script(script_name: str) -> Optional[str]:
    search_paths = [PROJECT_ROOT, PROJECT_ROOT / "src", PROJECT_ROOT / "src" / "data", PROJECT_ROOT / "src" / "model"]
    for path in search_paths:
        full_path = path / script_name
        if full_path.exists():
            return str(full_path.resolve())
    return None

def run_step(step_name: str, script_name: str, description: str) -> bool:
    """Tek bir pipeline adımını çalıştırır, Streamlit için özel destek içerir."""
    print(f"{Colors.OKGREEN}🚀 Starting: {step_name}{Colors.ENDC}")
    print(f"📄 Looking for: {script_name}")
    print(f"📝 Description: {description}")
    print("-" * 70)

    start_time = time.time()

    try:
        script_path = find_script(script_name)
        if not script_path:
            print(f"{Colors.FAIL}❌ Script not found: {script_name}{Colors.ENDC}")
            return False

        print(f"{Colors.OKGREEN}✅ Found script: {script_path}{Colors.ENDC}")

        # ------------------------------
        # a6_llm_reporting.py -> Streamlit olarak çalıştır
        # ------------------------------
        if "a6_llm_reporting.py" in script_name:
            print(f"{Colors.OKBLUE}🌐 Streamlit raporu başlatılıyor...{Colors.ENDC}")
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "streamlit", "run", script_path],
                    capture_output=False,
                    text=True
                )
                return result.returncode == 0
            except Exception as e:
                print(f"{Colors.FAIL}❌ Streamlit başlatılamadı: {str(e)}{Colors.ENDC}")
                return False

        # ------------------------------
        # Normal Python script çalıştır
        # ------------------------------
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        elapsed = time.time() - start_time

        if result.stdout:
            print(f"{Colors.OKCYAN}--- SCRIPT OUTPUT START ---{Colors.ENDC}")
            print(result.stdout)
            print(f"{Colors.OKCYAN}--- SCRIPT OUTPUT END ---{Colors.ENDC}")

        if result.stderr:
            print(f"{Colors.WARNING}--- SCRIPT STDERR START ---{Colors.ENDC}")
            print(result.stderr)
            print(f"{Colors.WARNING}--- SCRIPT STDERR END ---{Colors.ENDC}")

        if result.returncode == 0:
            print(f"\n{Colors.OKGREEN}✅ {step_name} başarıyla tamamlandı ({elapsed:.2f}s){Colors.ENDC}")
            return True
        else:
            print(f"\n{Colors.FAIL}❌ {step_name} başarısız oldu ({elapsed:.2f}s){Colors.ENDC}")
            return False

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  {step_name} kullanıcı tarafından kesildi ({time.time() - start_time:.2f}s){Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ {step_name} beklenmedik bir hatayla başarısız oldu: {str(e)}{Colors.ENDC}")
        return False

def run_full_pipeline() -> int:
    print_banner("🏀 NBA PLAYER RANKING PIPELINE", "=")
    print(f"Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Sürümü: {sys.version.split()[0]}")
    print(f"Çalışma Dizini: {os.getcwd()}")

    total_start = time.time()
    failed_steps = []
    completed_steps = []

    for i, step in enumerate(PIPELINE_STEPS, 1):
        print(f"\n{Colors.OKBLUE}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}STEP {i}/{len(PIPELINE_STEPS)}: {step['name']}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{step['description']}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{'='*70}{Colors.ENDC}\n")

        success = run_step(step["name"], step["script"], step["description"])
        if success:
            completed_steps.append(step["name"])
        else:
            failed_steps.append(step["name"])
            if i < len(PIPELINE_STEPS):
                try:
                    response = input(f"{Colors.WARNING}Sonraki adıma devam etmek istiyor musunuz? (y/n): {Colors.ENDC}").strip().lower()
                    if response != 'y':
                        break
                except EOFError:
                    break

    total_elapsed = time.time() - total_start
    print_banner("PIPELINE ÖZETİ", "=")
    print(f"{Colors.BOLD}Tamamlandı: {len(completed_steps)}/{len(PIPELINE_STEPS)}{Colors.ENDC}")
    for step in completed_steps:
        print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {step}")

    if failed_steps:
        print(f"\n{Colors.BOLD}Başarısız:{Colors.ENDC}")
        for step in failed_steps:
            print(f"  {Colors.FAIL}✗{Colors.ENDC} {step}")

    print(f"\n{Colors.BOLD}Toplam Süre: {total_elapsed:.2f}s{Colors.ENDC}")
    print(f"Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return 0 if not failed_steps else 1

def list_steps() -> None:
    print_banner("MEVCUT PIPELINE ADIMLARI", "=")
    for i, step in enumerate(PIPELINE_STEPS, 1):
        print(f"{Colors.BOLD}{i}. {step['name']}{Colors.ENDC}")
        print(f"    Script: {step['script']}")
        print(f"    Description: {step['description']}\n")
    print(f"{Colors.OKCYAN}Kullanım:{Colors.ENDC}")
    print(f"  python pipeline.py          # Tüm pipeline'ı çalıştır")
    print(f"  python pipeline.py --list   # Adımları listele")
    print(f"  python pipeline.py --help   # Yardım göster")

def main() -> int:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ["-h", "--help", "help"]:
            list_steps()
            return 0
        elif arg in ["-l", "--list", "list"]:
            list_steps()
            return 0
        else:
            print(f"{Colors.FAIL}Bilinmeyen argüman: {arg}{Colors.ENDC}")
            list_steps()
            return 1
    return run_full_pipeline()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Pipeline kullanıcı tarafından kesildi{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Beklenmedik hata: {str(e)}{Colors.ENDC}")
        sys.exit(1)
