import os
import time
import random
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# ==========================================
# --- BOT AYARLARI ---
# ==========================================
PERIYOT = "15"                # 15, 60, D, W, M
HEDEF_TARIH = "2020-01-01"   # YYYY-MM-DD
INDIRME_KLASORU = r"D:\Tradingview Bot\Veriler\15 dk" # Klasör yolun
# ==========================================

def setup_driver():
    options = Options()
    options.add_argument(r"user-data-dir=C:\TV_Bot_Profile")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    
    # Anti-Ban Gizlilik Ayarları
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if not os.path.exists(INDIRME_KLASORU):
        os.makedirs(INDIRME_KLASORU)

    prefs = {
        "download.default_directory": INDIRME_KLASORU,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_settings.popups": 0
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Tarayıcıyı WebDriver olarak tanıtan kimliği sil
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def download_bist_data():
    # ==========================================
    # --- BATCH (PARTİ) AYARLARI ---
    # ==========================================
    BATCH_SIZE = 50           # Kaç hissede bir uzun mola verilecek?
    UZUN_MOLA_DK = 15         # Uzun mola kaç dakika sürecek?
    # ==========================================

    # 1. Tüm hisse listesini txt'den oku
    try:
        with open("bist_semboller.txt", "r", encoding="utf-8") as f:
            tum_hisseler = [satir.strip() for satir in f.readlines() if satir.strip()]
    except FileNotFoundError:
        print("HATA: 'bist_semboller.txt' bulunamadı! Lütfen önce liste çekici scripti çalıştırın.")
        return

    # 2. Kaldığımız yerden devam etmek için işlenenleri oku
    islenenler_dosyasi = "islenen_hisseler.txt"
    if os.path.exists(islenenler_dosyasi):
        with open(islenenler_dosyasi, "r", encoding="utf-8") as f:
            islenenler = [satir.strip() for satir in f.readlines() if satir.strip()]
    else:
        islenenler = []

    # 3. İndirilecek kalan hisseleri filtrele
    kalan_hisseler = [h for h in tum_hisseler if h not in islenenler]
    
    print(f"\nToplam Hisse: {len(tum_hisseler)} | Daha Önce İndirilen: {len(islenenler)} | KALAN: {len(kalan_hisseler)}\n")
    
    if len(kalan_hisseler) == 0:
        print("Harika! Tüm hisseler zaten başarıyla indirilmiş.")
        return

    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 15)
    except Exception as e:
        print(f"Tarayıcı başlatılamadı. Hata: {e}")
        return

    sayac = 0
    for sembol in kalan_hisseler:
        sayac += 1
        print(f"\n-----------------------------------")
        print(f"[{sayac}/{len(kalan_hisseler)}] {sembol} grafiği ({PERIYOT} periyot) açılıyor...")
        
        try:
            driver.get(f"https://tr.tradingview.com/chart/?symbol={sembol}&interval={PERIYOT}")
            time.sleep(8) 
            
            # --- TARİHE GİT ADIMI ---
            print(f">>> {HEDEF_TARIH} tarihine gidiliyor...")
            body = driver.find_element(By.TAG_NAME, 'body')
            body.click()
            time.sleep(1)
            ActionChains(driver).key_down(Keys.ALT).send_keys('g').key_up(Keys.ALT).perform()
            
            tarih_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='YYYY-MM-DD']")))
            tarih_input.click()
            time.sleep(0.5)
            
            tarih_input.send_keys(Keys.CONTROL + "a")
            tarih_input.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)
            
            tarih_input.send_keys(HEDEF_TARIH)
            time.sleep(1)
            
            git_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-name='submit-button' and contains(., 'Tarihe git')]")))
            git_btn.click()
            
            print(">>> Tarihe gidildi. Verilerin yüklenmesi bekleniyor...")
            time.sleep(10) 
            
            # --- İNDİRME ADIMI ---
            print("1. Adım: Menü aranıyor...")
            menu_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-name='save-load-menu']")))
            driver.execute_script("arguments[0].click();", menu_btn)
            time.sleep(2) 
            
            print("2. Adım: İndir butonu aranıyor...")
            indir_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-role='menuitem']//span[contains(text(), 'Grafik verilerini indir')]")))
            driver.execute_script("arguments[0].click();", indir_btn)
            time.sleep(2) 
            
            print("3. Adım: Pop-up Onay butonu aranıyor...")
            onay_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-qa-id='download-btn' or @name='download']")))
            driver.execute_script("arguments[0].click();", onay_btn)
            
            # --- DOSYA YAKALAMA VE İSİMLENDİRME BÖLÜMÜ ---
            print(">>> Dosyanın inmesi bekleniyor...")
            
            saniye_sayaci = 0
            while True:
                cr_dosyalar = glob.glob(os.path.join(INDIRME_KLASORU, "*.crdownload"))
                if len(cr_dosyalar) == 0:
                    break
                time.sleep(1)
                saniye_sayaci += 1
                if saniye_sayaci > 30: 
                    break
            
            time.sleep(1) 
            
            csv_dosyalar = glob.glob(os.path.join(INDIRME_KLASORU, "*.csv"))
            if csv_dosyalar:
                en_yeni_dosya = max(csv_dosyalar, key=os.path.getctime)
                
                hisse_adi = sembol.split(":")[-1] 
                baslangic_yili = HEDEF_TARIH.split("-")[0] 
                bitis_yili = datetime.now().year 
                
                periyot_formati = f"{PERIYOT}m" if str(PERIYOT).isdigit() else PERIYOT
                
                yeni_isim = f"{hisse_adi}_{periyot_formati}_{baslangic_yili}_{bitis_yili}.csv"
                yeni_yol = os.path.join(INDIRME_KLASORU, yeni_isim)
                
                if os.path.exists(yeni_yol):
                    os.remove(yeni_yol)
                    
                os.rename(en_yeni_dosya, yeni_yol)
                print(f">>> BAŞARILI: Veri klasöre '{yeni_isim}' olarak kaydedildi!")
            
            # 4. BAŞARILI OLAN HİSSEYİ İŞLENENLER DOSYASINA YAZ (Kaldığı yerden devam etmek için)
            with open(islenenler_dosyasi, "a", encoding="utf-8") as f:
                f.write(sembol + "\n")
            
            # 5. MOLA VE BATCH KONTROLÜ
            if sayac % BATCH_SIZE == 0 and sayac != len(kalan_hisseler):
                bekleme_suresi = UZUN_MOLA_DK * 60
                print(f"\n{'='*50}")
                print(f"🛡️ ANTİ-BAN KORUMASI DEVREDE!")
                print(f"🛡️ {BATCH_SIZE} hisselik parti tamamlandı.")
                print(f"🛡️ TradingView radarına yakalanmamak için {UZUN_MOLA_DK} DAKİKA UZUN MOLA veriliyor...")
                print(f"{'='*50}\n")
                time.sleep(bekleme_suresi)
                print(">>> Mola bitti, sıradaki partiye geçiliyor...\n")
            else:
                bekleme = random.randint(10, 20)
                print(f"Sıradaki hisseye geçmeden önce {bekleme} saniye bekleniyor...\n")
                time.sleep(bekleme)
            
        except Exception as e:
            # Hata verirse islenenlere yazmaz, diğer çalışmada tekrar dener
            print(f"!!! HATA - {sembol} atlanıyor. Detay:\n{e}\n")
            
    print("\nTüm işlemler tamamlandı, bot kapatılıyor.")
    driver.quit()

if __name__ == "__main__":
    download_bist_data()