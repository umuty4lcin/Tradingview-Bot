import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def setup_driver():
    options = Options()
    
    # Bota özel ve manuel giriş yaptığımız o klasörü gösteriyoruz
    options.add_argument(r"user-data-dir=C:\TV_Bot_Profile")
    
    # Stabilite ayarları
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")

    # Selenium'un otomasyon bayraklarını gizler
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # İndirilen CSV dosyalarının kaydedileceği klasör
    prefs = {"download.default_directory": r"D:\Tradingview Bot\Veriler"}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def download_bist_data():
    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 15)
    except Exception as e:
        print(f"Tarayıcı başlatılamadı. Hata: {e}")
        return

    # Test için 3 hisse
    semboller = ["BIST:GARAN","BIST:THYAO","BIST:ASELS"]
    
    for sembol in semboller:
        print(f"-----------------------------------")
        print(f"{sembol} grafiği açılıyor...")
        driver.get(f"https://tr.tradingview.com/chart/?symbol={sembol}&interval=15")
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Grafiğin tam yüklenmesi için bekleme (İnternet hızına göre artırılabilir)
        time.sleep(8) 
        # Sayfayı rastgele bir miktar aşağı kaydırır
        scroll_miktari = random.randint(300, 700)
        driver.execute_script(f"window.scrollBy(0, {scroll_miktari});")
        time.sleep(random.uniform(1.5, 5.0)) # 1.5 ile 3 saniye arası küsuratlı bekleme

        # --- YENİ: HEDEF ODAKLI TARİHE GİT (GO TO DATE) YÖNTEMİ ---
        try:
            print(">>> 'Tarihe Git' penceresi açılıyor...")
            
            # 1. Grafiğe tıklayıp odağı al ve Alt + G ile pencereyi aç
            body = driver.find_element(By.TAG_NAME, 'body')
            body.click()
            time.sleep(1)
            ActionChains(driver).key_down(Keys.ALT).send_keys('g').key_up(Keys.ALT).perform()
            
            # 2. Görsel 1'deki tarih kutusunu YYYY-MM-DD placeholder'ından bul
            tarih_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='YYYY-MM-DD']")))
            tarih_input.click() # Kutuya tıkla
            time.sleep(0.5)
            
            # 3. Kutunun içinde hazır yazan bugünün tarihini tamamen sil (Ctrl+A ve Backspace)
            tarih_input.send_keys(Keys.CONTROL + "a")
            tarih_input.send_keys(Keys.BACK_SPACE)
            time.sleep(0.5)
            
            # 4. Hedef tarihi görseldeki formata (YYYY-MM-DD) birebir uygun şekilde yaz
            hedef_tarih = "2020-01-01"
            tarih_input.send_keys(hedef_tarih)
            time.sleep(1)
            
            # 5. Görsel 2'deki "Tarihe git" butonunu bul ve tıkla
            # (İndirme pop-up'ındaki submit butonuyla karışmaması için text() filtresi ekledik)
            git_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-name='submit-button' and contains(., 'Tarihe git')]")))
            git_btn.click()
            
            print(f">>> {hedef_tarih} tarihine gidildi. 40.000+ mumun yüklenmesi bekleniyor...")
            
            # On binlerce satır verinin sunucudan inip çizilmesi için bekleme
            time.sleep(12) 
            
        except Exception as e:
            print(f"!!! Tarihe gitme işlemi sırasında bir hata oluştu: {e}")
        # ----------------------------------------------
        
        try:
            print("1. Adım: Menü (Aşağı Ok) butonu aranıyor...")
            # Görsel 1'deki data-name='save-load-menu' olan butonu bul ve tıkla
            menu_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-name='save-load-menu']")))
            driver.execute_script("arguments[0].click();", menu_btn)
            time.sleep(2) # Menünün aşağı açılması için kısa bekleme
            
            print("2. Adım: İndir butonu aranıyor...")
            # Görsel 2'deki data-role='menuitem' olan ve içinde 'Grafik verilerini indir' yazan span'ı bul
            indir_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-role='menuitem']//span[contains(text(), 'Grafik verilerini indir')]")))
            driver.execute_script("arguments[0].click();", indir_btn)
            time.sleep(2) # Pop-up penceresinin ekrana gelmesini bekle
            
            print("3. Adım: Pop-up içindeki Onay (İndir) butonu aranıyor...")
            # Görselden alınan güncel XPath: data-qa-id='download-btn' veya name='download' olan buton
            onay_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@data-qa-id='download-btn' or @name='download']")))
            driver.execute_script("arguments[0].click();", onay_btn)
            
            print(f">>> BAŞARILI: {sembol} verisi indirildi!")
            
            # Anti-Ban beklemesi
            bekleme = random.randint(10, 20)
            print(f"Sıradaki hisseye geçmeden önce {bekleme} saniye bekleniyor...\n")
            time.sleep(bekleme)
            
        except Exception as e:
            print(f"!!! HATA - {sembol} atlanıyor. Element bulunamadı veya tıklanamadı.")
            print(f"Detay: {e}\n")
            
    print("Tüm işlemler tamamlandı, bot kapatılıyor.")
    driver.quit()

if __name__ == "__main__":
    download_bist_data()