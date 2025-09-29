from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, time, json, re, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Providence:
    def __init__(self) -> None:
        self.BASE_API = "https://hub.playprovidence.io/api"
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.cookie_headers = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
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
    
    async def load_proxies(self):
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
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
    
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
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
        
        return None
    
    async def user_stats(self, token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/user/stats"
        headers = {
            **self.HEADERS[token],
            "Cookie": self.cookie_headers[token]
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Account :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Data Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def checkin_status(self, token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/daily-checkin/status"
        headers = {
            **self.HEADERS[token],
            "Cookie": self.cookie_headers[token]
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Status Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def claim_checkin(self, token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/daily-checkin/checkin"
        headers = {
            **self.HEADERS[token],
            "Content-Length": "0",
            "Cookie": self.cookie_headers[token]
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
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
    
    async def daily_tasks(self, token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/quests/daily-link/today"
        headers = {
            **self.HEADERS[token],
            "Cookie": self.cookie_headers[token]
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Tasks   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Fetch Daily Tasks Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
    
    async def complete_tasks(self, token: str, quest_id: str, quest_name: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/quests/daily-link/complete"
        data = json.dumps({"questId": quest_id})
        headers = {
            **self.HEADERS[token],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Cookie": self.cookie_headers[token]
        }
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
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
            
    async def process_check_connection(self, token: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if not is_valid:
                if rotate_proxy:
                    proxy = self.rotate_proxy_for_account(token)

                continue

            return True
        
    async def process_accounts(self, token: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(token, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(token) if use_proxy else None

            stats = await self.user_stats(token, proxy)
            if stats:
                email = stats.get("data", {}).get("user_email", "Unknown")
                level = stats.get("data", {}).get("level", 0)
                points = stats.get("data", {}).get("total_xp", 0)

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Account :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Level   :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {level} {Style.RESET_ALL}"
                )
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Points  :{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {points} XP {Style.RESET_ALL}"
                )

            checkin_status = await self.checkin_status(token, proxy)
            if checkin_status:
                can_checkin = checkin_status.get("data", {}).get("canCheckinToday")
                if can_checkin:
                    claim = await self.claim_checkin(token, proxy)
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
                    formatted_next_checkin = datetime.fromtimestamp(next_checkin_datetime).astimezone(wib).strftime('%x %X %Z')
                    
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}Check-In:{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Not Time To Claim {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Claim At: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{formatted_next_checkin}{Style.RESET_ALL}"
                    )

            quest_lists = await self.daily_tasks(token, proxy)
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

                        complete = await self.complete_tasks(token, quest_id, quest_name, proxy)
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
            with open('tokens.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            proxy_choice, rotate_proxy = self.print_question()

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                use_proxy = True if proxy_choice == 1 else False
                if use_proxy:
                    await self.load_proxies()
                
                separator = "=" * 26
                for idx, token in enumerate(accounts, 1):
                    if token:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        self.cookie_headers[token] = f"__Secure-authjs.session-token={token}"

                        self.HEADERS[token] = {
                            "Accept": "*/*",
                            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Origin": "https://hub.playprovidence.io",
                            "Referer": "https://hub.playprovidence.io/",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "User-Agent": FakeUserAgent().random
                        }
                            
                        await self.process_accounts(token, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*63)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Providence()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Providence - BOT{Style.RESET_ALL}                                       "                              
        )