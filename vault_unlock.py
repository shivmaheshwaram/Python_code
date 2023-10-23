import json
import configparser
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class UnlockVault(object):

    def __init__(self, environment: str):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.property_file_location = self.root_dir + "\environmentconfig.properties"
        self.config_prop = configparser.RawConfigParser()
        self.config_prop.read(self.property_file_location)
        self.role_id = self.config_prop.get("VAULT", "role_id")
        self.auth_url = self.config_prop.get("VAULT", "auth_url")
        self.secret_url = self.config_prop.get("VAULT", f"secret_url_{environment}")

    def get_secrets(self) -> dict:
        data = {"role_id": self.role_id}
        retries = Retry(
            total=5,
            backoff_factor=1,
            method_whitelist=["GET", "POST", "PUT", "HEAD"],
            status_forcelist=[429, 500, 502, 503, 504]
        )
        s = requests.Session()
        s.mount("https://", HTTPAdapter(max_retries=retries))
        res = s.post(url=self.auth_url, data=json.dumps(data))
        print(res.status_code)
        if res.status_code != 200:
            # sleep then retry add retry count
            # TODO: log error
            print("connection error")
        vault_res = json.loads(res.content.decode("utf-8"))
        token = vault_res["auth"]["client_token"]
        headers = {
            "X-Vault-Token": token
        }
        get_sess = requests.Session()
        get_sess.mount("https://", HTTPAdapter(max_retries=retries))
        res_secrets = get_sess.get(url=self.secret_url, headers=headers)
        if res_secrets.status_code != 200:
            # TODO: log error
            print("connection error")
        secrets = json.loads(res_secrets.content.decode("utf-8"))
        passwords = secrets["data"]["data"]
        return passwords


if __name__ == "__main__":
    unlock = UnlockVault(environment="nonprod")
    secs = unlock.get_secrets()
    print(secs)
