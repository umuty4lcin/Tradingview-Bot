import sqlite3
import pandas as pd
import glob
import os

# Ayarlar
CSV_KLASORU = r"D:\Tradingview Bot\Veriler\15 dk"
VERITABANI_YOLU = r"D:\Tradingview Bot\BorsaVeritabani.db"

def csv_to_sqlite():
    # 1. Klasördeki tüm .csv dosyalarını bul
    csv_dosyalar = glob.glob(os.path.join(CSV_KLASORU, "*.csv"))
    
    if not csv_dosyalar:
        print("Klasörde aktarılacak CSV dosyası bulunamadı!")
        return

    # 2. SQLite veritabanına bağlan (Dosya yoksa anında sıfırdan oluşturur)
    print(f"Veritabanına bağlanılıyor: {VERITABANI_YOLU}")
    conn = sqlite3.connect(VERITABANI_YOLU)
    
    try:
        for dosya in csv_dosyalar:
            # Dosya adından tablo ismini çıkar (Örn: "AKBNK_15m_2020_2026.csv" -> "AKBNK_15m_2020_2026")
            tablo_adi = os.path.basename(dosya).replace(".csv", "")
            
            print(f"'{tablo_adi}' dosyası okunuyor...")
            
            # 3. Pandas ile CSV dosyasını DataFrame (Sanal Tablo) olarak hafızaya al
            df = pd.read_csv(dosya)
            
            # Sütun isimlerini veritabanı standartlarına uygun hale getirelim (Boşlukları sil, küçük harf yap vb.)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            # 4. Veriyi SQLite'a yaz! 
            # if_exists='replace': Tablo zaten varsa silip üzerine yazar. ('append' dersen üstüne ekler)
            # index=False: Pandas'ın kendi satır numaralarını veritabanına sütun olarak eklemesini engeller.
            df.to_sql(tablo_adi, conn, if_exists='replace', index=False)
            
            satir_sayisi = len(df)
            print(f">>> BAŞARILI: {satir_sayisi} satır veri '{tablo_adi}' tablosuna yazıldı!\n")
            
    except Exception as e:
        print(f"Veritabanı işlemi sırasında bir hata oluştu: {e}")
        
    finally:
        # 5. Bağlantıyı güvenlice kapat
        conn.close()
        print("Veritabanı bağlantısı kapatıldı. Aktarım tamamlandı.")

if __name__ == "__main__":
    csv_to_sqlite()