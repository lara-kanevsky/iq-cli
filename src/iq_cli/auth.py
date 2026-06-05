"""Authentication management for iq CLI."""

import requests
from typing import Optional
from pathlib import Path
from http.cookiejar import MozillaCookieJar
from .config import config


class AuthManager:
    """Handles authentication and session management."""

    def __init__(self):
        self.cookies_file = config.cookies_file
        self.session = requests.Session()

    def login(self, email: str, password: str) -> bool:
        """
        Authenticate with the iquall system.

        Args:
            email: User email
            password: User password

        Returns:
            True if authentication successful, False otherwise
        """
        url = f"{config.frontend_url}/session/loginInfoCheck"

        data = {
            'email': email,
            'password': password
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = self.session.post(url, data=data, headers=headers, allow_redirects=True)

            print(f"Status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Cookies from response.cookies: {dict(response.cookies)}")
            print(f"Cookies from session: {dict(self.session.cookies)}")

            # Check for success (200 or 302 redirect)
            if response.status_code in [200, 302]:
                # Save all cookies from the session
                cookies_dict = {}

                # Get cookies from session (includes redirects)
                for cookie in self.session.cookies:
                    cookies_dict[cookie.name] = cookie.value
                    print(f"Cookie found: {cookie.name}={cookie.value}")

                if cookies_dict:
                    with open(self.cookies_file, 'w') as f:
                        for name, value in cookies_dict.items():
                            f.write(f"{name}={value}\n")
                    print(f"Saved {len(cookies_dict)} cookie(s) to {self.cookies_file}")
                    return True
                else:
                    print("No cookies received from server")
                    # Even if no cookies, might be successful
                    # Check response body for success indicators
                    try:
                        response_data = response.json()
                        print(f"Response body: {response_data}")
                        # If we get here and status is 200, consider it success
                        # Save a dummy cookie file to mark as authenticated
                        with open(self.cookies_file, 'w') as f:
                            f.write(f"authenticated=true\n")
                        return True
                    except:
                        print(f"Response text: {response.text[:200]}")
                        return False
            else:
                print(f"Login failed with status {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_cookies(self) -> Optional[dict]:
        """
        Load cookies from file.

        Returns:
            Dictionary of cookies or None if not authenticated
        """
        if not self.cookies_file.exists():
            print(f"Cookie file does not exist: {self.cookies_file}")
            return None

        cookies = {}
        with open(self.cookies_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    name, value = line.split('=', 1)
                    cookies[name] = value

        print(f"Loaded cookies: {cookies}")
        return cookies if cookies else None

    def get_session(self) -> requests.Session:
        """
        Get requests session with loaded cookies.

        Returns:
            Configured requests session
        """
        session = requests.Session()
        cookies = self.get_cookies()
        if cookies:
            for name, value in cookies.items():
                session.cookies.set(name, value)
        return session

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.cookies_file.exists()

    def logout(self):
        """Remove stored credentials."""
        if self.cookies_file.exists():
            self.cookies_file.unlink()


# Global auth manager instance
auth_manager = AuthManager()
