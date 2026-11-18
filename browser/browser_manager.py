
import os
import shutil
import subprocess
import tempfile
import platform


class BrowserManager:

    def __init__(self):
        self.process = None
        self.profile_dir = None
        self.chrome_path = self.find_chrome()

    def find_chrome(self):

        system = platform.system()

        if system == "Windows":

            possible_paths = [
                os.path.join(
                    os.environ.get("PROGRAMFILES", ""),
                    "Google",
                    "Chrome",
                    "Application",
                    "chrome.exe"
                ),
                os.path.join(
                    os.environ.get("PROGRAMFILES(X86)", ""),
                    "Google",
                    "Chrome",
                    "Application",
                    "chrome.exe"
                ),
                os.path.join(
                    os.environ.get("LOCALAPPDATA", ""),
                    "Google",
                    "Chrome",
                    "Application",
                    "chrome.exe"
                )
            ]

            for path in possible_paths:
                if path and os.path.isfile(path):
                    return path

            return shutil.which("chrome")

        if system == "Darwin":
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            ]

            for path in possible_paths:
                if os.path.isfile(path):
                    return path

            return shutil.which("google-chrome")

        return (
            shutil.which("google-chrome")
            or shutil.which("chromium")
            or shutil.which("chromium-browser")
        )

    def open_chrome(self, url="https://www.google.com"):

        if not self.chrome_path:
            raise RuntimeError(
                "Google Chrome was not found on this computer."
            )

        if self.process and self.process.poll() is None:
            # Reuse the Chrome instance launched by this application.
            self.process = subprocess.Popen(
                [self.chrome_path, url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            return "Opened the requested page in Chrome."

        self.profile_dir = tempfile.mkdtemp(
            prefix="llm_gateway_chrome_"
        )

        command = [
            self.chrome_path,
            "--user-data-dir=" + self.profile_dir,
            "--no-first-run",
            "--no-default-browser-check",
            url
        ]

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return "Chrome opened successfully."

    def close_chrome(self):

        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None

            if self.profile_dir and os.path.isdir(self.profile_dir):
                shutil.rmtree(self.profile_dir, ignore_errors=True)

            self.profile_dir = None

            return "Closed the Chrome instance launched by this application."

        return "No Chrome instance launched by this application is running."


browser_manager = BrowserManager()
