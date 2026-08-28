import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Final

import requests
from tpm2_pytss import FAPI
from typing_extensions import override

from model.config.config_manager import ConfigManager
from model.logger.logger_manager import LoggerManager
from model.tpm.abstract_tpm import AbstractTPM


class LinuxTPM(AbstractTPM):
    """
    TPM interface for Linux.

    Provides support for virtual TPM, for development and testing.

    For real TPM, the user is expected to set up and provision FAPI by themselves, since this
    operation may differ from device to device, and might require authentication/ authorization
    through auth_callback. Apps beforehand might have already provisioned a real TPM setup.
    Subsequent failed attempts to authorize cause a Dictionary Attack Lockout.
    """
    config: ConfigManager
    logger: LoggerManager

    NV_PATH: Final[str] = "/nv/Owner/authenstickator"
    """Secret is stored in NVRAM at a location abstractized by this key."""

    def __init__(self):
        self.config = ConfigManager()
        self.logger = LoggerManager()
        virtual = self.config.get("tpm.virtual.enabled")
        if virtual:
            self.setup_fapi_virtual()
            self.start_tpm_virtual()
            self.provision_fapi_virtual()
        self.setup_secret()
        self.logger.info("LinuxTPM initialized.")

    @override
    def setup_secret(self) -> None:
        with FAPI() as fapi:
            tpm_paths = fapi.list("/")
            if any(tpm_path.endswith(self.NV_PATH) for tpm_path in tpm_paths):
                self.logger.info("Secret setup skipped since it already exists.")
                return

            random_bytes = fapi.get_random(16)
            fapi.create_nv(self.NV_PATH, 16, exists_ok=True)
            fapi.nv_write(self.NV_PATH, random_bytes)
        self.logger.info("Secret setup successful.")

    @override
    def get_secret(self) -> bytes:
        with FAPI() as fapi:
            secret = fapi.nv_read(self.NV_PATH)[0]
        self.logger.info("Secret retrieval successful.")
        return secret

    def setup_fapi_virtual(self):
        fapi_dir = Path.home() / ".local" / "share" / "authenstickator"
        if fapi_dir.exists():
            self.logger.info(f"Directory {fapi_dir} exists, skipping virtual FAPI setup.")
            return

        self.logger.info(f"Starting virtual FAPI setup in {fapi_dir}")

        system_dir = fapi_dir / "system-dir"
        user_dir = fapi_dir / "user-dir"
        profile_dir = fapi_dir / "profile-dir"
        log_dir = fapi_dir / "log-dir"
        for directory in [system_dir, user_dir, profile_dir, log_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        profile = self.config.get("tpm.virtual.fapi_profile")
        profile_file = f"{profile}.json"
        profile_file_path = profile_dir / profile_file
        self.download_profile_file(profile_file_path)

        config_file = fapi_dir / "fapi-config.json"
        self.create_fapi_config_virtual(config_file, profile_dir, user_dir, system_dir, fapi_dir)

        # Set the environment variable so that the session picks up the right FAPI configuration.
        os.environ["TSS2_FAPICONF"] = str(config_file)

        self.logger.info(f"Virtual FAPI setup done.")

    def download_profile_file(self, profile_file_path):
        """
        Downloads the FAPI profile file specified in configs.
        """
        if profile_file_path.exists():
            self.logger.info(f"File {profile_file_path} exists, skipping profile file download.")
            return
        try:
            profile_url = self.config.get("tpm.virtual.fapi_profile_url")
            self.logger.info(f"Downloading profile file from {profile_url}")
            response = requests.get(profile_url, timeout=10)
            response.raise_for_status()
            with open(profile_file_path, "w") as f:
                f.write(response.text)
        except Exception as e:
            self.logger.error(f"Failed to download profile file.")
            raise e

    def create_fapi_config_virtual(self, config_file, profile_dir, user_dir, system_dir, fapi_dir):
        """
        Creates the fapi-config.json file for the virtual TPM.
        """
        if config_file.exists():
            self.logger.info(f"File {config_file} exists, skipping virtual FAPI config creation.")
            return

        port = self.config.get("tpm.virtual.tpm_port")
        config_data = {
            "profile_name": self.config.get('tpm.virtual.fapi_profile'),
            "profile_dir": f"{profile_dir}",
            "user_dir": f"{user_dir}",
            "system_dir": f"{system_dir}",
            "tcti": f"swtpm:port={port}",
            "system_pcrs": [],
            "log_dir": f"{fapi_dir}",
            "ek_cert_less": "yes"
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f, indent=4)

    def start_tpm_virtual(self):
        tpm_port = self.config.get("tpm.virtual.tpm_port")
        ctrl_port = self.config.get("tpm.virtual.tpm_ctrl_port")

        if self.is_virtual_tpm_on(tpm_port):
            self.logger.info(f"Virtual TPM is on, skipping virtual TPM start")
            return

        path = Path(self.config.get("tpm.virtual.tpm_path"))
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
        tpm_start_wait_s = self.config.get("tpm.virtual.tpm_start_wait_s")
        subprocess.Popen(command)
        time.sleep(tpm_start_wait_s)
        if not self.is_virtual_tpm_on(tpm_port):
            raise RuntimeError(
                f"Could connect to localhost port {tpm_port} after waiting {tpm_start_wait_s} "
                f"seconds, considering virtual TPM startup failed.")

        self.logger.info("Virtual TPM started")

    def provision_fapi_virtual(self):
        """
        Even though is_provisioned_ok is set to true, the underlying C library will show an error
        message in the logs if the TPM is already provisioned. However, no exception is raised,
        and execution happens as expected. Checking whether TPM is provisioned beforehand is not
        worth the hassle.
        """
        with FAPI() as fapi:
            fapi.set_auth_callback(self.auth_callback_virtual)
            fapi.provision(is_provisioned_ok=True)

    @staticmethod
    def is_virtual_tpm_on(tpm_port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # 0 means success... it is a wrapper for a C function
            if s.connect_ex(("localhost", tpm_port)) == 0:
                return True
        return False

    @staticmethod
    def auth_callback_virtual(path, description, user_data=None):  # noqa
        """FAPI expects this; for virtual TPM, it is just a dummy method respecting the signature"""
        print(path)
        return b""
