from bs4 import BeautifulSoup
from colorama import Fore
from pathlib import Path
import subprocess
import requests
import urllib3
import logging
import sys


# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
logger = logging.getLogger(__name__)

NVIDIA_DOWNLOAD_URL = "https://www.nvidia.com/download/driverResults.aspx/224155/en-us/"
DOWNLOAD_PATH = Path(Path.home(), "Desktop", "GPU_UPDATE")


# My Module Functions

def progress_bar(progress, total, length, pre_text='', colored=True, color_doing=Fore.YELLOW, color_end=Fore.GREEN):
	color_reset = Fore.RESET

	if progress == total:
		bar = '-' * length
		if colored: print(color_end + f'\r{pre_text}[{bar}] 100.00%' + color_reset, end='\n')
		else: print(f'\r{pre_text}[{bar}] 100.00%', end='\n')
		return

	percent: float = progress / total * 100
	done: int = int(percent / (100 / length))
	todo: int = length - done
	bar = '-' * done + '.' * todo

	if colored: print(color_doing + f'\r{pre_text}[{bar}] {percent:.2f}%' + color_reset, end='')
	else: print(f'\r{pre_text}[{bar}] {percent:.2f}%', end='')


def download_webfile(url: str, filepath: Path | str, progress_callback=None, create_folder: bool = True, chunk_size: int = 1024 * 1024) -> bool:
	# Convert filepath to Path object
	try: filepath = Path(filepath)
	except TypeError as e: logger.error(f"Invalid file path: {e}"); return False

	# Create parent folder if it doesn't exist
	if create_folder: filepath.parent.mkdir(exist_ok=True, parents=True)

	try:
		# Start HTTP request session
		with urllib3.PoolManager() as http:
			# Send HTTP GET request with streaming enabled
			with http.request('GET', url, preload_content=False) as response:
				# Get content length from response headers
				content_length = int(response.headers['Content-Length'])
				logger.info(f"Downloading {url} to {filepath} ({content_length} bytes)")

				# Open file for writing in binary mode
				with open(str(filepath), 'wb') as f:
					downloaded_bytes = 0
					# Iterate over response content in chunks
					for chunk in response.stream(chunk_size):
						# Write chunk to file
						f.write(chunk)
						downloaded_bytes += len(chunk)
						# Calculate download progress
						progress = min(int(downloaded_bytes / content_length * 100), 100)
						# Call the progress callback, if provided
						if progress_callback: progress_callback(progress)

		logger.info(f"\nDownload complete")
		return True

	# Catch HTTP errors
	except urllib3.exceptions.HTTPError as e: logger.error(f"HTTP Error: {e}"); return False
	# Catch OS errors
	except OSError as e: logger.error(f"OS Error: {e}"); return False
	# Catch other exceptions
	except Exception as e: logger.error(f"An error occurred: {e}"); return False


# Projects Functions

def download_webfile_callback(progress: int):
	progress_bar(progress, 100, 40, "Downloading: ", Fore.MAGENTA)


def get_local_version() -> float | None:
	try:
		result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'], capture_output=True, text=True)
		if result.returncode == 0:
			driver_version = float(result.stdout.strip())
			return driver_version
		else:
			return None  # Indicate failure
	except FileNotFoundError:
		raise FileNotFoundError("nvidia-smi command not found")
	except subprocess.CalledProcessError:
		raise RuntimeError("Error while running nvidia-smi command")


def get_online_version(soup: BeautifulSoup):
	return float(str(soup.find(id="tdVersion").text).strip().split()[0])


def get_download_url(soup: BeautifulSoup):
	new_soup = BeautifulSoup(requests.get(f"https://www.nvidia.com{soup.find(id="lnkDwnldBtn")["href"]}").text, 'lxml')
	return f"https:{new_soup.find_all("a")[9]["href"]}"


def main():
	soup = BeautifulSoup(requests.get(NVIDIA_DOWNLOAD_URL).text, 'lxml')

	# Get installed driver version
	local_version = get_local_version()
	if local_version is None: print(f"{Fore.RED}Driver version not found - Retry Later{Fore.RESET}"); return
	print(f"{Fore.CYAN}Installed driver version found: {local_version}{Fore.RESET}")

	# Get online available driver version
	online_version = get_online_version(soup)
	print(f"{Fore.MAGENTA}Online available driver version found: {online_version}{Fore.RESET}")

	# Compare versions
	if online_version == local_version: print(f"{Fore.GREEN}You already have the latest available driver{Fore.RESET}"); return

	# Create a filepath like 541_14.exe
	filepath = Path(DOWNLOAD_PATH, f"{str(online_version).replace('.', '_')}.exe")

	# Get Download url
	download_url = get_download_url(soup)

	# Download latest driver url
	if download_webfile(download_url, filepath, download_webfile_callback): print(f"{Fore.GREEN}Download ends successfully{Fore.RESET}")
	else: print(f"{Fore.RED}Download has an error{Fore.RESET}")


if __name__ == '__main__':
	main()
