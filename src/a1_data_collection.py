"""
NBA Oyuncu Verileri Toplama Scripti
Kaggle'dan CSV dosyalarını indirir ve data/raw/ klasörüne kaydeder
"""

import os
import sys
import zipfile
import subprocess
import traceback
from pathlib import Path
import io

# Windows terminali için UTF-8 çıktı zorlaması
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    # Ev dizinini doğru bir şekilde genişlet
    kaggle_path = os.path.expanduser("~/.kaggle/kaggle.json")
    
    if not os.path.exists(kaggle_path):
        print("❌ Kaggle kimlik dosyası bulunamadı!", flush=True)
        print(f"📁 Beklenen konum: {kaggle_path}", flush=True)
        print("\n🔧 Çözüm:", flush=True)
        print("1. Kaggle hesabınıza giriş yapın: https://www.kaggle.com/", flush=True)
        print("2. Account → API → 'Create New API Token' tıklayın", flush=True)
        print("3. İndirilen kaggle.json dosyasını şu konuma taşıyın:", flush=True)
        print(f"   {kaggle_path}", flush=True)
        print("4. Linux/Mac için: chmod 600 ~/.kaggle/kaggle.json", flush=True)
        
        raise FileNotFoundError(f"Kaggle kimlik dosyası bulunamadı: {kaggle_path}")
    
    print("✅ Kaggle kimlik doğrulaması bulundu", flush=True)

# ------------------------------
# KLASÖR OLUŞTURMA
# ------------------------------
def ensure_folders():
    """Gerekli klasörleri oluştur"""
    os.makedirs(RAW_DIR, exist_ok=True)
    print(f"✅ {RAW_DIR} klasörü hazır", flush=True)

# ------------------------------
# YÖNTEM 1: Kaggle Python API (TERCİH EDİLEN)
# ------------------------------
def download_with_kaggle_api():
    """Kaggle Python API kullanarak indir"""
    try:
        import kaggle
        
        print(f"📥 Veri seti indiriliyor: {DATASET}", flush=True)
        print("🔄 Yöntem: Kaggle Python API", flush=True)
        
        # Tüm dataset'i zip olarak indir
        # quiet=True ile ilerleme çubuğunun neden olduğu charmap hatasını önlüyoruz.
        kaggle.api.dataset_download_files(
            dataset=DATASET,
            path=RAW_DIR,
            unzip=True,
            force=True,
            quiet=True
        )
        
        print(f"✅ Veri başarıyla indirildi: {RAW_DIR}", flush=True)
        return True
        
    except UnicodeDecodeError:
        print("⚠️  Unicode hatası oluştu, alternatif yöntem deneniyor...", flush=True)
        return False
    except Exception as e:
        print(f"⚠️  Kaggle API hatası: {e}", flush=True)
        print("🔄 Alternatif yöntem deneniyor...", flush=True)
        return False

# ------------------------------
# YÖNTEM 2: Kaggle CLI (ALTERNATİF)
# ------------------------------
def download_with_cli():
    """Kaggle CLI komut satırı ile indir"""
    try:
        print(f"📥 Veri seti indiriliyor: {DATASET}", flush=True)
        print("🔄 Yöntem: Kaggle CLI", flush=True)
        
        # Komut listesi
        cmd = [
            "kaggle", "datasets", "download",
            "-d", DATASET,
            "-p", RAW_DIR,
            "--unzip",
            "--force",
            "--quiet" # CLI'da da ilerleme çubuğunu devre dışı bırakıyoruz
        ]
        
        # subprocess ile çalıştır
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,  # Metin modunda çalıştırıyoruz
            encoding='utf-8', # Çıktıyı doğrudan UTF-8 olarak decode etmeye zorluyoruz
            errors='replace', # Geçersiz karakterleri güvenli karakterlerle değiştirir.
            shell=False # Güvenlik ve kontrol için shell kullanmıyoruz
        )
        
        if result.returncode == 0:
            print(f"✅ Veri başarıyla indirildi: {RAW_DIR}", flush=True)
            return True
        else:
            # Hata mesajı zaten UTF-8 olarak decode edildiği için direk kullanabiliriz
            error_msg = result.stderr.strip()
            
            # CLI'dan gelen çıktıları (stdout/stderr) ana scriptin çıktısına yönlendir
            if result.stdout:
                print(f"CLI Çıktısı:\n{result.stdout.strip()}", flush=True)
            if error_msg:
                # Hata mesajını görmezden gelmek yerine, çıktıda gösteriyoruz.
                print(f"❌ İndirme hatası (CLI Mesajı):\n{error_msg}", flush=True)
            
            # Başarılı olmadığı için False dön
            return False
            
    except FileNotFoundError:
        print("❌ Kaggle CLI bulunamadı. Lütfen 'pip install kaggle' ile kurun.", flush=True)
        return False
    except Exception as e:
        print(f"⚠️  CLI hatası: {e}", flush=True)
        return False

# ------------------------------
# YÖNTEM 3: Manuel ZIP İndirme (EN GÜVENLİ)
# ------------------------------
def download_manual_zip():
    """Tek zip dosyası olarak indir ve aç"""
    try:
        import kaggle
        
        print(f"📥 Veri seti indiriliyor (ZIP): {DATASET}", flush=True)
        print("🔄 Yöntem: Manuel ZIP indirme", flush=True)
        
        # Zip olarak indir (unzip=False)
        kaggle.api.dataset_download_files(
            dataset=DATASET,
            path=RAW_DIR,
            unzip=False,
            force=True,
            quiet=True  # Sessiz mod
        )
        
        # Zip dosyasını bulmak için olası adları kontrol et
        dataset_name = DATASET.split('/')[-1]
        possible_zips = [
            os.path.join(RAW_DIR, f"{dataset_name}.zip"),
            os.path.join(RAW_DIR, "dataset.zip"),
            os.path.join(RAW_DIR, f"{DATASET.replace('/', '-')}.zip")
        ]
        
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
            print("❌ ZIP dosyası bulunamadı", flush=True)
            return False
        
        print(f"📦 ZIP bulundu: {zip_path}", flush=True)
        print("📂 Dosyalar açılıyor...", flush=True)
        
        # Zip'i aç ve sil
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(RAW_DIR)
        
        os.remove(zip_path)
        
        print(f"✅ Veri başarıyla indirildi ve açıldı: {RAW_DIR}", flush=True)
        return True
        
    except Exception as e:
        print(f"⚠️  Manuel ZIP hatası: {e}", flush=True)
        return False

# ------------------------------
# İNDİRİLEN DOSYALARI LİSTELE
# ------------------------------
def list_downloaded_files():
    """İndirilen CSV dosyalarını listele"""
    if not os.path.exists(RAW_DIR):
        print("❌ Veri klasörü bulunamadı", flush=True)
        return
    
    csv_files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]
    
    if not csv_files:
        print("⚠️  CSV dosyası bulunamadı", flush=True)
        return
    
    print(f"\n📊 İndirilen CSV dosyaları ({len(csv_files)} adet):", flush=True)
    for i, filename in enumerate(csv_files, 1):
        filepath = os.path.join(RAW_DIR, filename)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"   {i}. {filename} ({size_mb:.2f} MB)", flush=True)

# ------------------------------
# CHARMAP HATASI İÇİN YARDIMCI FONKSİYON
# ------------------------------
def print_traceback_utf8():
    """Traceback çıktısını io.StringIO ile yakalar ve UTF-8 olarak basar"""
    try:
        # Traceback'i bir StringIO nesnesine yaz
        tb_stream = io.StringIO()
        traceback.print_exc(file=tb_stream)
        tb_value = tb_stream.getvalue()
        
        # Yakalanan traceback'i UTF-8 olarak konsola yaz
        sys.stderr.write(tb_value)
        sys.stderr.flush()
    except Exception as e:
        # Bu da başarısız olursa, sadece hatayı bas
        print(f"Traceback yazdırma hatası: {e}", flush=True)
        print("Hata izi detayları için konsolu kontrol edin.", flush=True)


# ------------------------------
# ANA FONKSİYON
# ------------------------------
def main():
    """Ana çalıştırma fonksiyonu"""
    print("\n" + "="*60, flush=True)
    print("🏀 NBA VERİ TOPLAMA - KAGGLE'DAN İNDİRME", flush=True)
    print("="*60 + "\n", flush=True)
    
    try:
        # 1. Kaggle kimlik kontrolü
        check_kaggle_api()
        
        # 2. Klasörleri oluştur
        ensure_folders()
        
        # 3. İndirme işlemini dene (3 yöntem)
        success = False
        
        # Yöntem 1: Python API
        if not success:
            print("\n--- YÖNTEM 1: Kaggle Python API ---", flush=True)
            success = download_with_kaggle_api()
        
        # Yöntem 2: CLI
        if not success:
            print("\n--- YÖNTEM 2: Kaggle CLI ---", flush=True)
            success = download_with_cli()
        
        # Yöntem 3: Manuel ZIP
        if not success:
            print("\n--- YÖNTEM 3: Manuel ZIP İndirme ---", flush=True)
            success = download_manual_zip()
        
        # 4. Başarı kontrolü
        if success:
            list_downloaded_files()
            print("\n" + "="*60, flush=True)
            print("✅ VERİ TOPLAMA İŞLEMİ BAŞARIYLA TAMAMLANDI", flush=True)
            print("="*60 + "\n", flush=True)
        else:
            print("\n" + "="*60, flush=True)
            print("❌ TÜM İNDİRME YÖNTEMLERİ BAŞARISIZ OLDU", flush=True)
            print("="*60, flush=True)
            print("\n🔧 MANUEL ÇÖZÜM:", flush=True)
            print(f"1. Kaggle'a gidin: https://www.kaggle.com/datasets/{DATASET}", flush=True)
            print("2. 'Download' butonuna tıklayın", flush=True)
            print(f"3. İndirilen ZIP'i {os.path.abspath(RAW_DIR)} klasörüne çıkarın", flush=True)
            print(flush=True)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  İşlem kullanıcı tarafından iptal edildi", flush=True)
    except Exception as e:
        # Hatanın kendisini basarken charmap hatası almamak için Türkçe karakterleri basit tutuyoruz
        print(f"\n❌ Beklenmeyen bir hata oluştu: {e}", flush=True)
        # Traceback'i güvenli yöntemle yazdır
        print_traceback_utf8()

if __name__ == "__main__":
    main()