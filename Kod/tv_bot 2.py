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
CEKILECEK_HISSELER = ["BIST:AKBNK"]
PERIYOT = "60"                # 15, 60, D, W, M
HEDEF_TARIH = "2020-01-01"   # YYYY-MM-DD
INDIRME_KLASORU = r"D:\Tradingview Bot\Veriler\1 saat" # Klasör yolun
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
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 15)
    except Exception as e:
        print(f"Tarayıcı başlatılamadı. Hata: {e}")
        return

    for sembol in CEKILECEK_HISSELER:
        print(f"\n-----------------------------------")
        print(f"{sembol} grafiği ({PERIYOT} periyot) açılıyor...")
        
        driver.get(f"https://tr.tradingview.com/chart/?symbol={sembol}&interval={PERIYOT}")
        time.sleep(8) 
        
        # --- TARİHE GİT ADIMI ---
        try:
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
            time.sleep(18) 
        except Exception as e:
            print(f"!!! Tarihe gitme hatası: {e}")
            
        # --- İNDİRME ADIMI ---
        try:
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
            
            # --- YENİ EKLENEN DOSYA YAKALAMA VE İSİMLENDİRME BÖLÜMÜ ---
            print(">>> Dosyanın inmesi bekleniyor...")
            
            # İndirme bitene kadar (Chrome'un geçici .crdownload dosyası kaybolana kadar) bekle
            saniye_sayaci = 0
            while True:
                cr_dosyalar = glob.glob(os.path.join(INDIRME_KLASORU, "*.crdownload"))
                if len(cr_dosyalar) == 0:
                    break
                time.sleep(1)
                saniye_sayaci += 1
                if saniye_sayaci > 30: # 30 saniyeden uzun sürerse döngüden çık (hata önlemi)
                    break
            
            time.sleep(1) # Dosya sisteminin (Windows) kendine gelmesi için ekstra 1 saniye
            
            # Klasördeki en son indirilen .csv dosyasını bul
            csv_dosyalar = glob.glob(os.path.join(INDIRME_KLASORU, "*.csv"))
            if csv_dosyalar:
                en_yeni_dosya = max(csv_dosyalar, key=os.path.getctime)
                
                # Yeni ismi dinamik olarak oluştur
                hisse_adi = sembol.split(":")[-1] # "BIST:AKBNK" içinden sadece "AKBNK" kısmını alır
                baslangic_yili = HEDEF_TARIH.split("-")[0] # "2020-01-01" -> "2020"
                bitis_yili = datetime.now().year # Güncel yıl (2026)
                
                # Periyot rakamsa yanına "m" ekle (15 -> 15m), harfse direkt yaz (D -> D)
                periyot_formati = f"{PERIYOT}m" if str(PERIYOT).isdigit() else PERIYOT
                
                yeni_isim = f"{hisse_adi}_{periyot_formati}_{baslangic_yili}_{bitis_yili}.csv"
                yeni_yol = os.path.join(INDIRME_KLASORU, yeni_isim)
                
                # Klasörde aynı isimli eski bir dosya varsa hata vermemesi için onu sil
                if os.path.exists(yeni_yol):
                    os.remove(yeni_yol)
                    
                # Dosyayı yeniden adlandır
                os.rename(en_yeni_dosya, yeni_yol)
                print(f">>> BAŞARILI: Veri klasöre '{yeni_isim}' olarak kaydedildi!")
            
            # Anti-Ban beklemesi
            bekleme = random.randint(10, 20)
            print(f"Sıradaki hisseye geçmeden önce {bekleme} saniye bekleniyor...")
            time.sleep(bekleme)
            
        except Exception as e:
            print(f"!!! HATA - {sembol} atlanıyor. Detay:\n{e}\n")
            
    print("\nTüm işlemler tamamlandı, bot kapatılıyor.")
    driver.quit()

if __name__ == "__main__":
    download_bist_data()