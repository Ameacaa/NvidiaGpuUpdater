from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from colorama import Fore
from pathlib import Path
import subprocess
import urllib3


DOWNLOAD_PATH = Path(Path.home(), "Desktop", "GPU_UPDATE")


def get_nvidia_driver_version() -> float:
	try:
		result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], capture_output=True, text=True)
		return float(result.stdout.strip()) if result.returncode == 0 else -1.0
	except FileNotFoundError:
		return 0.0


def get_chrome_webdriver(headless: bool = True):
	service = None  # Service(ChromeDriverManager().install())
	options = webdriver.ChromeOptions()
	options.add_experimental_option('detach', True)
	options.add_argument('--mute-audio')
	options.add_argument('--ignore-ssl-errors=yes')
	options.add_argument('--ignore-certificate-errors')
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	if headless: options.add_argument('--headless=new')
	return webdriver.Chrome(options=options, service=service)


def get_scraped_infos():
	try:
		driver = get_chrome_webdriver(headless=True)
		driver.implicitly_wait(20)
		driver.get("https://www.nvidia.com/download/index.aspx")

		# Page 1 - Select in dropboxes what GPU we want to check
		driver.find_element(By.XPATH, '//*[@id="selProductSeriesType"]/option[1]').click()  # Product Type
		driver.find_element(By.XPATH, '//*[@id="selProductSeries"]/option[14]').click()  # Product Serie
		driver.find_element(By.XPATH, '//*[@id="selProductFamily"]/option[5]').click()  # Product
		driver.find_element(By.XPATH, '//*[@id="selOperatingSystem"]/option[3]').click()  # OS
		driver.find_element(By.XPATH, '//*[@id="ddlDownloadTypeCrdGrd"]/option[1]').click()  # Download Type
		driver.find_element(By.XPATH, '//*[@id="ddlLanguage"]/option[1]').click()  # Language
		driver.find_element(By.XPATH, '//*[@id="ManualSearchButtonTD"]/a').click()  # Click Search Button

		# Page 2 - Get the version and click the first download button
		avaliable_version = float(driver.find_element(By.XPATH, '//*[@id="tdVersion"]').text.split()[0])
		driver.find_element(By.XPATH, '//*[@id="lnkDwnldBtn"]').click()

		# Page 3 - Click the second download button
		download_url = driver.find_element(By.XPATH, '//*[@id="mainContent"]/table/tbody/tr/td/a').get_attribute("href")

		driver.close()

		return float(avaliable_version), download_url
	except:
		return "", ""


def download_webfile(url: str, filepath: Path | str, create_folder: bool = True, chunk_size: int = 1073741824) -> bool:
	try: _file = Path(filepath)
	except Exception as e: print(e); return False

	if create_folder: _file.parent.mkdir(exist_ok=True, parents=True)

	try:
		lib = urllib3.PoolManager()
		response = lib.request('GET', url, preload_content=False)
		with open(str(filepath), 'wb') as f:
			data = response.read(chunk_size)
			if not data: pass
			f.write(data)
		response.release_conn()
		return True
	except Exception as e: print(e); return False


def driver_checker():
	local_version = get_nvidia_driver_version()
	if local_version == -1.0: print(f"{Fore.RED}An error as occured while getting the driver version - Retry Later{Fore.RESET}"); quit()
	elif local_version == 0.0: print(f"Appears that you have no NVIDIA driver installed - Downloading the latest version")

	online_version, download_url = get_scraped_infos()
	if online_version == "" or download_url == "": print(f"{Fore.RED}An error as occured while scraping nvidia website - Retry Later{Fore.RESET}"); quit()

	# Nvidia version => Major.minor.patch => Just check major and minor here
	print(f"Installed Version: {local_version} | Avaliable Version: {online_version}")
	if online_version > local_version:
		print("Downloading latest version")
		outpath = Path(DOWNLOAD_PATH, f"{str(online_version).replace('.','_')}.exe")  # Example: 541_14.exe
		if download_webfile(download_url, outpath, True): print(f"{Fore.GREEN}Download done{Fore.RESET}")
		else: print(f"{Fore.RED}Download Failed{Fore.RESET}")
	else: print(f"{Fore.GREEN}You have the latest driver{Fore.RESET}")


if __name__ == '__main__':
	driver_checker()
