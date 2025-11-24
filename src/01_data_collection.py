"""
NBA Oyuncu Verileri Toplama Scripti
Kaggle'dan CSV dosyalarını indirir ve data/raw/ klasörüne kaydeder
"""

import os
import sys
import zipfile
import subprocess
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ------------------------------
# AYARLAR
# ------------------------------
DATASET = "ratin21/nba-player-stats-and-salaries-2010-2025"
RAW_DIR = os.path.join("data", "raw")

# ------------------------------
# KAGGLE KİMLİK KONTROLÜ
# ------------------------------
def check_kaggle_api():
    """Kaggle kimlik doğrulaması kontrolü"""
    kaggle_path = os.path.expanduser("~/.kaggle/kaggle.json")
    
    if not os.path.exists(kaggle_path):
        print("❌ Kaggle kimlik dosyası bulunamadı!")
        print(f"📁 Beklenen konum: {kaggle_path}")
        print("\n🔧 Çözüm:")
        print("1. Kaggle hesabınıza giriş yapın: https://www.kaggle.com/")
        print("2. Account → API → 'Create New API Token' tıklayın")
        print("3. İndirilen kaggle.json dosyasını şu konuma taşıyın:")
        print(f"   {kaggle_path}")
        print("4. Linux/Mac için: chmod 600 ~/.kaggle/kaggle.json")
        
        raise FileNotFoundError(f"Kaggle kimlik dosyası bulunamadı: {kaggle_path}")
    
    print("✅ Kaggle kimlik doğrulaması bulundu")

# ------------------------------
# KLASÖR OLUŞTURMA
# ------------------------------
def ensure_folders():
    """Gerekli klasörleri oluştur"""
    os.makedirs(RAW_DIR, exist_ok=True)
    print(f"✅ {RAW_DIR} klasörü hazır")

# ------------------------------
# ZIP DOSYASINI AÇMA
# ------------------------------
def extract_zip(zip_path: str, extract_to: str):
    """Zip dosyasını aç ve sil"""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        os.remove(zip_path)
        print(f"   ✅ ZIP açıldı ve silindi")
        return True
    except Exception as e:
        print(f"   ⚠️  ZIP açma hatası: {e}")
        return False

# ------------------------------
# YÖNTEM 1: Kaggle Python API (TERCİH EDİLEN)
# ------------------------------
def download_with_kaggle_api():
    """Kaggle Python API kullanarak indir"""
    try:
        import kaggle
        
        print(f"📥 Veri seti indiriliyor: {DATASET}")
        print("🔄 Yöntem: Kaggle Python API")
        
        # Tüm dataset'i zip olarak indir
        kaggle.api.dataset_download_files(
            dataset=DATASET,
            path=RAW_DIR,
            unzip=True,
            force=True,
            quiet=False  # Progress bar göster
        )
        
        print(f"✅ Veri başarıyla indirildi: {RAW_DIR}")
        return True
        
    except UnicodeDecodeError:
        print("⚠️  Unicode hatası oluştu, alternatif yöntem deneniyor...")
        return False
    except Exception as e:
        print(f"⚠️  Kaggle API hatası: {e}")
        print("🔄 Alternatif yöntem deneniyor...")
        return False

# ------------------------------
# YÖNTEM 2: Kaggle CLI (ALTERNATİF)
# ------------------------------
def download_with_cli():
    """Kaggle CLI komut satırı ile indir"""
    try:
        print(f"📥 Veri seti indiriliyor: {DATASET}")
        print("🔄 Yöntem: Kaggle CLI")
        
        # PowerShell/CMD için komut
        cmd = [
            "kaggle", "datasets", "download",
            "-d", DATASET,
            "-p", RAW_DIR,
            "--unzip",
            "--force"
        ]
        
        # subprocess ile çalıştır (encoding sorununu önler)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=False,  # Binary mode - encoding sorununu önler
            shell=True
        )
        
        if result.returncode == 0:
            print(f"✅ Veri başarıyla indirildi: {RAW_DIR}")
            return True
        else:
            # Hata mesajını güvenli decode et
            try:
                error_msg = result.stderr.decode('utf-8', errors='ignore')
            except:
                error_msg = "Bilinmeyen hata"
            
            print(f"❌ İndirme hatası: {error_msg}")
            return False
            
    except Exception as e:
        print(f"⚠️  CLI hatası: {e}")
        return False

# ------------------------------
# YÖNTEM 3: Manuel ZIP İndirme (EN GÜVENLİ)
# ------------------------------
def download_manual_zip():
    """Tek zip dosyası olarak indir ve aç"""
    try:
        import kaggle
        
        print(f"📥 Veri seti indiriliyor (ZIP): {DATASET}")
        print("🔄 Yöntem: Manuel ZIP indirme")
        
        # Zip olarak indir (unzip=False)
        zip_file = os.path.join(RAW_DIR, "dataset.zip")
        
        kaggle.api.dataset_download_files(
            dataset=DATASET,
            path=RAW_DIR,
            unzip=False,
            force=True,
            quiet=True  # Sessiz mod
        )
        
        # Varsayılan zip adı: dataset-name.zip
        dataset_name = DATASET.split('/')[-1]
        possible_zips = [
            os.path.join(RAW_DIR, f"{dataset_name}.zip"),
            os.path.join(RAW_DIR, "dataset.zip"),
            os.path.join(RAW_DIR, f"{DATASET.replace('/', '-')}.zip")
        ]
        
        # Zip dosyasını bul
        zip_path = None
        for path in possible_zips:
            if os.path.exists(path):
                zip_path = path
                break
        
        # Eğer bulunamazsa, raw dizinindeki ilk zip'i al
        if not zip_path:
            zip_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.zip')]
            if zip_files:
                zip_path = os.path.join(RAW_DIR, zip_files[0])
        
        if not zip_path or not os.path.exists(zip_path):
            print("❌ ZIP dosyası bulunamadı")
            return False
        
        print(f"📦 ZIP bulundu: {zip_path}")
        print("📂 Dosyalar açılıyor...")
        
        # Zip'i aç
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DIR)
        
        # Zip'i sil
        os.remove(zip_path)
        
        print(f"✅ Veri başarıyla indirildi ve açıldı: {RAW_DIR}")
        return True
        
    except Exception as e:
        print(f"⚠️  Manuel ZIP hatası: {e}")
        return False

# ------------------------------
# İNDİRİLEN DOSYALARI LİSTELE
# ------------------------------
def list_downloaded_files():
    """İndirilen CSV dosyalarını listele"""
    if not os.path.exists(RAW_DIR):
        print("❌ Veri klasörü bulunamadı")
        return
    
    csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        print("⚠️  CSV dosyası bulunamadı")
        return
    
    print(f"\n📊 İndirilen CSV dosyaları ({len(csv_files)} adet):")
    for i, filename in enumerate(csv_files, 1):
        filepath = os.path.join(RAW_DIR, filename)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"   {i}. {filename} ({size_mb:.2f} MB)")

# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    """Ana çalıştırma fonksiyonu"""
    print("\n" + "="*60)
    print("🏀 NBA VERİ TOPLAMA - KAGGLE'DAN İNDİRME")
    print("="*60 + "\n")
    
    try:
        # 1. Kaggle kimlik kontrolü
        check_kaggle_api()
        
        # 2. Klasörleri oluştur
        ensure_folders()
        
        # 3. İndirme işlemini dene (3 yöntem)
        success = False
        
        # Yöntem 1: Python API
        if not success:
            print("\n--- YÖNTEM 1: Kaggle Python API ---")
            success = download_with_kaggle_api()
        
        # Yöntem 2: CLI
        if not success:
            print("\n--- YÖNTEM 2: Kaggle CLI ---")
            success = download_with_cli()
        
        # Yöntem 3: Manuel ZIP
        if not success:
            print("\n--- YÖNTEM 3: Manuel ZIP İndirme ---")
            success = download_manual_zip()
        
        # 4. Başarı kontrolü
        if success:
            list_downloaded_files()
            print("\n" + "="*60)
            print("✅ VERİ TOPLAMA İŞLEMİ BAŞARIYLA TAMAMLANDI")
            print("="*60 + "\n")
        else:
            print("\n" + "="*60)
            print("❌ TÜM İNDİRME YÖNTEMLERİ BAŞARISIZ OLDU")
            print("="*60)
            print("\n🔧 MANUEL ÇÖZÜM:")
            print(f"1. Kaggle'a gidin: https://www.kaggle.com/datasets/{DATASET}")
            print("2. 'Download' butonuna tıklayın")
            print(f"3. İndirilen ZIP'i {os.path.abspath(RAW_DIR)} klasörüne çıkarın")
            print()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından iptal edildi")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()