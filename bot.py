from curl_cffi import requests
from datetime import datetime
from colorama import *
import asyncio, random, time, sys, re, os

class Providence:
    def __init__(self) -> None:
        self.BASE_API = "https://hub.playprovidence.io"
        self.USE_PROXY = False
        self.ROTATE_PROXY = False
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.accounts = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Providence {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_tokens(self):
        filename = "tokens.txt"
        try:
            with open(filename, 'r') as file:
                tokens = [line.strip() for line in file if line.strip()]
            return tokens
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Tokens: {e}{Style.RESET_ALL}")
            return None

    def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"
    
    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        return account
    
    def initialize_headers(self, idx: int):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Origin": "https://hub.playprovidence.io",
            "Pragma": "no-cache",
            "Referer": "https://hub.playprovidence.io/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self.accounts[idx]["user_agent"]
        }

        return headers.copy()
        
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")
    
    def ensure_ok(self, response):
        err_code = response.status_code
        err_text = response.text

        if err_code >= 400:
            raise Exception(f"HTTP {err_code}: {err_text}")
    
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"

        proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
        try:
            response = await asyncio.to_thread(
                requests.get, 
                url=url, 
                proxies=proxies, 
                timeout=30, 
                impersonate="chrome120"
            )
            self.ensure_ok(response)
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def auth_session(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/auth/session"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx]["cookie"]

                response = await asyncio.to_thread(
                    requests.get, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                print(f"{response.status_code}:{response.text}")
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Session :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Authenticate {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def user_stats(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/user/stats"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx]["cookie"]

                response = await asyncio.to_thread(
                    requests.get, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Account :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Stats {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def checkin_status(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/daily-checkin/status"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx]["cookie"]

                response = await asyncio.to_thread(
                    requests.get, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Status {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_checkin(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/daily-checkin/checkin"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx]["cookie"]

                response = await asyncio.to_thread(
                    requests.post, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def daily_tasks(self, idx: int, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/quests/daily-link/today"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                cookies = self.accounts[idx]["cookie"]

                response = await asyncio.to_thread(
                    requests.get, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Failed to Fetch Daily Tasks {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def complete_tasks(self, idx: int, quest_id: str, quest_name: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/api/quests/daily-link/complete"
        
        for attempt in range(retries):
            proxies = {"http":proxy_url, "https":proxy_url} if proxy_url else None
            try:
                headers = self.initialize_headers(idx)
                headers["Content-Type"] = "application/json"
                cookies = self.accounts[idx]["cookie"]
                payload = {
                    "questId": quest_id
                }

                response = await asyncio.to_thread(
                    requests.post, 
                    url=url, 
                    headers=headers, 
                    cookies=cookies, 
                    json=payload,
                    proxies=proxies, 
                    timeout=120, 
                    impersonate="chrome120"
                )
                self.ensure_ok(response)
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}   > {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{quest_name}{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Completed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def process_check_connection(self, idx: int, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(idx)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.display_proxy(proxy_url)} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True

            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(idx)
                await asyncio.sleep(1)
                continue

            return False
    
    async def process_accounts(self, idx: int, proxy_url=None):
        is_valid = await self.process_check_connection(idx, proxy_url)
        if not is_valid: return False

        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(idx)

        stats = await self.user_stats(idx, proxy_url)
        if stats:
            email = stats.get("data", {}).get("user_email", "Unknown")
            points = stats.get("data", {}).get("total_xp", 0)
            level = stats.get("data", {}).get("level", 0)

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Account :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Points  :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {points} XP {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Level   :{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {level} {Style.RESET_ALL}"
            )

        checkin_status = await self.checkin_status(idx, proxy_url)
        if checkin_status:
            can_checkin = checkin_status.get("data", {}).get("canCheckinToday")
            if can_checkin:
                claim = await self.claim_checkin(idx, proxy_url)
                if claim:
                    reward = claim.get("data", {}).get("xpEarned")
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Claimed Successfully {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{reward} XP{Style.RESET_ALL}"
                    )
                
            else:
                next_checkin_timestamp = checkin_status.get("data", {}).get("nextCheckinIn")
                next_checkin_datetime = int(time.time()) + (next_checkin_timestamp / 1000)
                formatted_next_checkin = datetime.fromtimestamp(next_checkin_datetime).strftime('%x %X')
                
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Not Time To Claim {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Claim At: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{formatted_next_checkin}{Style.RESET_ALL}"
                )

        quest_lists = await self.daily_tasks(idx, proxy_url)
        if quest_lists:
            quests = quest_lists.get("data", [])

            if quests:
                self.log(f"{Fore.CYAN + Style.BRIGHT}Tasks   :{Style.RESET_ALL}")

                for quest in quests:
                    quest_id = quest["id"]
                    quest_name = quest["title"]
                    quest_xp = quest["xp"]
                    is_completed = quest["isCompleted"]

                    if is_completed:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}   > {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{quest_name}{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} Already Completed {Style.RESET_ALL}"
                        )
                        continue

                    complete = await self.complete_tasks(idx, quest_id, quest_name, proxy_url)
                    if complete:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}   > {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{quest_name}{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Completed {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {quest_xp} XP {Style.RESET_ALL}"
                        )

            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} No Available Daily Tasks Found {Style.RESET_ALL}"
                )

    async def main(self):
        try:
            tokens = self.load_tokens()
            if not tokens:
                print(f"{Fore.RED+Style.BRIGHT}No Tokens Loaded.{Style.RESET_ALL}") 
                return

            self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(tokens)}{Style.RESET_ALL}"
                )

                if self.USE_PROXY: self.load_proxies()

                separator = "=" * 25
                for idx, session_token in enumerate(tokens, start=1):
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(tokens)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    if idx not in self.accounts:
                        self.accounts[idx] = {
                            "user_agent": random.choice(self.USER_AGENTS),
                            "cookie": {
                                "__Secure-authjs.session-token": session_token
                            }
                        }
                        
                    await self.process_accounts(idx)
                    await asyncio.sleep(random.uniform(2.0, 3.0))

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*60)
                
                delay = 24 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Providence()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().strftime('%x %X')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Providence - BOT{Style.RESET_ALL}                                       "                              
        )
        sys.exit(0)