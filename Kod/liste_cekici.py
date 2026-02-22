import requests

def bist_hisselerini_getir():
    print("TradingView API'sine bağlanılıyor...")
    
    # TradingView Türkiye Tarayıcı API'si
    url = "https://scanner.tradingview.com/turkey/scan"
    
    # Sadece 'hisse senedi' tipindeki varlıkları iste
    payload = {
        "filter": [{"left": "type", "operation": "equal", "right": "stock"}],
        "columns": ["name"],
        "sort": {"sortBy": "name", "sortOrder": "asc"},
        "range": [0, 2000] # BIST'te 500 civarı hisse var, limiti geniş tutuyoruz
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        # Gelen verinin başına 'BIST:' ekleyerek listeyi oluştur
        bist_hisseler = [f"BIST:{item['d'][0]}" for item in data['data']]
        
        # Listeyi bir .txt dosyasına kaydet
        with open("bist_semboller.txt", "w", encoding="utf-8") as dosya:
            for hisse in bist_hisseler:
                dosya.write(hisse + "\n")
                
        print(f">>> BAŞARILI: {len(bist_hisseler)} adet hisse bulundu ve 'bist_semboller.txt' dosyasına kaydedildi!")
        return bist_hisseler
    else:
        print(f"Hata: API'ye ulaşılamadı. Durum Kodu: {response.status_code}")
        return []

if __name__ == "__main__":
    bist_hisselerini_getir()