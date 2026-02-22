import sqlite3
import pandas as pd

# 1. Veritabanına bağlan
veritabani_yolu = r"D:\Tradingview Bot\BorsaVeritabani.db"
conn = sqlite3.connect(veritabani_yolu)

# 2. SQL Sorgunu Yaz (Timestamp'i tarihe çeviren kod burada)
# DİKKAT: Görselindeki tablo adını birebir kullandım.
sorgu = """
SELECT 
    datetime(time, 'unixepoch', 'localtime') AS Tarih_Saat,
    open, 
    high, 
    low, 
    close, 
    volume 
FROM "BIST_DLY_ASELS, 15"
ORDER BY time ASC 
LIMIT 50;
"""

try:
    # 3. Sorguyu çalıştır ve sonucu bir DataFrame'e al
    df = pd.read_sql_query(sorgu, conn)
    
    # Ekrana düzgün basılması için Pandas ayarları
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    print(">>> ASELSAN 15 Dakikalık Son 15 Mum Verisi:\n")
    print(df)
    
except Exception as e:
    print(f"Sorgu hatası: {e}")
finally:
    conn.close()