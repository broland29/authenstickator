import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Final
from typing_extensions import override

from tpm2_pytss import FAPI

import requests

from src.config.config_manager import ConfigManager
from src.logger.logger_manager import LoggerManager
from src.tpm.abstract_tpm import AbstractTPM

class LinuxTPM(AbstractTPM):
    """
    TPM interface for Linux.

    TPM has to be set up by the user. The config is usually at path /etc/tpm2-tss/fapi-config.json
    """

    KEY_PATH: Final[str] = "HS/SRK/authenstickator"
    """Encryption and decryption uses a key, which is identified by this path."""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = LoggerManager()
        self.setup_fapi()
        self.provision_fapi()
        self.init_key()


    def setup_fapi(self):
        base_dir = Path(__file__).parent.absolute()
        fapi_dir = base_dir / "fapi-config"
        self.logger.info(f"Setting up FAPI in {fapi_dir}")

        system_dir = fapi_dir / "system-dir"
        user_dir = fapi_dir / "user-dir"
        profile_dir = fapi_dir / "profile-dir"
        log_dir = fapi_dir / "log-dir"
        for directory in [system_dir, user_dir, profile_dir, log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        profile_file_path = profile_dir / self.config.get('tpm.fapi_profile_file')
        self.download_profile_file(profile_file_path)

        config_file = fapi_dir / "fapi-config.json"
        self.create_config_file(config_file, profile_dir, user_dir, system_dir, fapi_dir)

        self.start_virtual_tpm()

        # Set the environment variable so that the session picks up the right FAPI configuration.
        os.environ["TSS2_FAPICONF"] = str(config_file)

        self.logger.info(f"FAPI setup complete.")


    def download_profile_file(self, profile_file_path):
        if profile_file_path.exists():
            self.logger.info(f"FAPI profile file already exists at {profile_file_path}, skipping download.")
            return
        try:
            url = self.config.get('tpm.fapi_profile_url')
            self.logger.info(f"Downloading FAPI profile file from {url}")
            response = requests.get(url, timeout = 10)
            response.raise_for_status()
            with open(profile_file_path, "w") as f:
                f.write(response.text)
        except Exception as e:
            self.logger.error(f"Failed to download FAPI profile.")
            raise e


    def create_config_file(self, config_file, profile_dir, user_dir, system_dir, fapi_dir):
        if config_file.exists():
            self.logger.info(f"FAPI config file already exists at {config_file}, skipping creation.")
            return

        config_data = {
            "profile_name": self.config.get('tpm.fapi_profile_name'),
            "profile_dir": f"{profile_dir}",
            "user_dir": f"{user_dir}",
            "system_dir": f"{system_dir}",
            "system_pcrs": [],
            "log_dir": f"{fapi_dir}",
            "ek_cert_less": "yes"
        }

        if self.config.get('tpm.virtualized'):
            config_data["tcti"] = f"swtpm:port={self.config.get('tpm.virtualized_tpm_port')}"
        else:
            config_data["tcti"] = ""

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)


    def start_virtual_tpm(self):
        if not self.config.get("tpm.virtualized"):
            return

        tpm_port = self.config.get('tpm.virtualized_tpm_port')
        ctrl_port = self.config.get('tpm.virtualized_tpm_ctrl_port')

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if self.is_tpm_on(tpm_port):
                self.logger.info(f"Could connect to localhost port {tpm_port}, considering virtual TPM running")
                return

        path = Path(self.config.get("tpm.virtualized_tpm_path"))
        self.logger.info(f"Starting virtual TPM at {path}")
        path.mkdir(parents=True, exist_ok=True)

        command = [
            "swtpm", "socket", "--tpm2",
            "--tpmstate", f"dir={path}",
            "--ctrl", f"type=tcp,port={ctrl_port}",
            "--server", f"type=tcp,port={tpm_port}",
            "--flags", "not-need-init"
        ]

        # no try-catch, let it raise
        seconds_to_wait = self.config.get("tpm.virtualized_tpm_startup_seconds")
        subprocess.Popen(command)
        time.sleep(seconds_to_wait)
        if not self.is_tpm_on(tpm_port):
            raise RuntimeError(f"Could connect to localhost port {tpm_port} after waiting {seconds_to_wait} seconds, considering virtual TPM startup failed.")


    def provision_fapi(self):
        """
        Even though is_provisioned_ok is set to true, the underlying C library will throw an error message in the logs if
        the TPM is already provisioned. But no exception is raised, and execution happens as expected. Checking wether
        TPM is provisioned beforehand is not worth the hassle:
        - Could check if system_dir was created, but that is not a guarantee.
        - Could check if the path "/P_RSA2048SHA256/HS/SRK" exists in the result of fapi.list(), but that needs a fapi
        instance, which fails if not provisioned => does not take us any further.
        """
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            fapi.provision(is_provisioned_ok=True)


    def is_tpm_on(self, tpm_port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", tpm_port)) == 0:  # 0 means success... wrapper for C function
                return True
        return False


    def auth_callback(self, path, description, user_data=None):
        """FAPI"""
        print(path)
        return b""

    def init_key(self):
        """
        Similarly to provision, this will throw an error message if the key already exists, but that affects only logs.
        """
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            fapi.create_key(
                path = self.KEY_PATH,
                type_ = "decrypt",
                exists_ok = True
            )

    @override
    def encrypt(self, plaintext: str) -> bytes:
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            return fapi.encrypt(self.KEY_PATH, plaintext.encode("utf-8"))


    @override
    def decrypt(self, ciphertext: bytes) -> str:
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback)
            return fapi.decrypt(self.KEY_PATH, ciphertext).decode("utf-8")
