#!/usr/bin/env python3
"""
Web Scraping Agent
Playwright 기반 동적 웹 스크래핑 에이전트 (로그인 지원)

사용법:
    python agent.py                    # 기본 실행
    python agent.py --url <URL>        # 특정 URL 스크래핑
    python agent.py --headless false   # 브라우저 표시 모드
    python agent.py --output result.csv # 출력 파일 지정
    python agent.py --skip-login       # 로그인 건너뛰기
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout

import config


class WebScrapingAgent:
    """Playwright 기반 웹 스크래핑 에이전트 (로그인 지원)"""

    def __init__(
        self,
        url: Optional[str] = None,
        headless: Optional[bool] = None,
        output_file: Optional[str] = None,
        skip_login: bool = False,
    ):
        self.url = url or config.TARGET_URL
        self.headless = headless if headless is not None else config.BROWSER_CONFIG["headless"]
        self.output_file = output_file or config.OUTPUT_CONFIG["filename"]
        self.skip_login = skip_login
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.scraped_data: list[dict] = []

    def start_browser(self) -> None:
        """브라우저 시작"""
        print(f"🚀 브라우저 시작 중... (headless: {self.headless})")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=config.BROWSER_CONFIG["slow_mo"],
        )
        context = self.browser.new_context(
            user_agent=config.USER_AGENT,
            viewport={"width": 1920, "height": 1080},
        )
        self.page = context.new_page()
        self.page.set_default_timeout(config.BROWSER_CONFIG["timeout"])
        print("✅ 브라우저 준비 완료")

    def close_browser(self) -> None:
        """브라우저 종료"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            print("🔒 브라우저 종료")

    def login(self) -> bool:
        """로그인 수행"""
        if not hasattr(config, 'LOGIN_CONFIG') or not config.LOGIN_CONFIG.get("enabled"):
            print("ℹ️ 로그인 비활성화됨")
            return True

        if self.skip_login:
            print("ℹ️ 로그인 건너뛰기")
            return True

        login_config = config.LOGIN_CONFIG
        print(f"🔐 로그인 시도 중: {login_config['login_url']}")

        try:
            # 로그인 페이지로 이동
            self.page.goto(login_config["login_url"], wait_until="networkidle")
            self.page.wait_for_timeout(2000)

            # 이메일 입력
            email_selectors = login_config["selectors"]["email_input"].split(", ")
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = self.page.query_selector(selector)
                    if email_input:
                        break
                except Exception:
                    continue

            if email_input:
                email_input.click()
                email_input.fill(login_config["credentials"]["email"])
                print(f"  ✓ 이메일 입력: {login_config['credentials']['email']}")
            else:
                print("  ⚠️ 이메일 입력란을 찾을 수 없습니다. 선택자를 확인하세요.")
                self._print_available_inputs()
                return False

            self.page.wait_for_timeout(500)

            # 비밀번호 입력
            password_selectors = login_config["selectors"]["password_input"].split(", ")
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.page.query_selector(selector)
                    if password_input:
                        break
                except Exception:
                    continue

            if password_input:
                password_input.click()
                password_input.fill(login_config["credentials"]["password"])
                print("  ✓ 비밀번호 입력 완료")
            else:
                print("  ⚠️ 비밀번호 입력란을 찾을 수 없습니다.")
                return False

            self.page.wait_for_timeout(500)

            # 로그인 버튼 클릭
            submit_selectors = login_config["selectors"]["submit_button"].split(", ")
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.page.query_selector(selector)
                    if submit_button and submit_button.is_visible():
                        break
                except Exception:
                    continue

            if submit_button:
                submit_button.click()
                print("  ✓ 로그인 버튼 클릭")
            else:
                # 버튼을 못 찾으면 Enter 키로 시도
                print("  ℹ️ 로그인 버튼을 찾을 수 없어 Enter 키로 시도")
                self.page.keyboard.press("Enter")

            # 로그인 완료 대기
            self.page.wait_for_timeout(3000)
            self.page.wait_for_load_state("networkidle")

            # 로그인 성공 확인
            current_url = self.page.url
            if "auth" not in current_url.lower() and "login" not in current_url.lower():
                print("✅ 로그인 성공!")
                return True

            # 로그인 성공 지시자 확인
            success_selectors = login_config.get("success_indicator", "").split(", ")
            for selector in success_selectors:
                try:
                    if self.page.query_selector(selector):
                        print("✅ 로그인 성공!")
                        return True
                except Exception:
                    continue

            print("⚠️ 로그인 상태 확인 불가 - 계속 진행합니다")
            return True

        except PlaywrightTimeout:
            print("❌ 로그인 타임아웃")
            return False
        except Exception as e:
            print(f"❌ 로그인 실패: {e}")
            return False

    def _print_available_inputs(self) -> None:
        """페이지의 입력 요소들을 출력 (디버깅용)"""
        try:
            inputs = self.page.query_selector_all("input")
            print("\n  📋 페이지에서 발견된 input 요소들:")
            for i, inp in enumerate(inputs):
                inp_type = inp.get_attribute("type") or "text"
                inp_name = inp.get_attribute("name") or ""
                inp_id = inp.get_attribute("id") or ""
                inp_placeholder = inp.get_attribute("placeholder") or ""
                print(f"    [{i+1}] type={inp_type}, name={inp_name}, id={inp_id}, placeholder={inp_placeholder}")
        except Exception:
            pass

    def navigate_to_page(self) -> bool:
        """페이지로 이동"""
        print(f"📄 페이지 로딩 중: {self.url}")
        try:
            self.page.goto(self.url, wait_until="networkidle")

            # 특정 요소 대기 (설정된 경우)
            if config.WAIT_CONFIG["wait_for_selector"]:
                self.page.wait_for_selector(
                    config.WAIT_CONFIG["wait_for_selector"],
                    timeout=config.BROWSER_CONFIG["timeout"],
                )

            # 추가 대기 시간
            if config.WAIT_CONFIG["wait_time"]:
                self.page.wait_for_timeout(config.WAIT_CONFIG["wait_time"])

            print("✅ 페이지 로딩 완료")
            return True

        except PlaywrightTimeout:
            print("❌ 페이지 로딩 타임아웃")
            return False
        except Exception as e:
            print(f"❌ 페이지 로딩 실패: {e}")
            return False

    def extract_text(self, element, selector: str) -> str:
        """요소에서 텍스트 추출 (여러 선택자 지원)"""
        selectors = selector.split(", ")
        for sel in selectors:
            try:
                target = element.query_selector(sel.strip())
                if target:
                    text = target.inner_text().strip()
                    if text:
                        return text
            except Exception:
                continue
        return ""

    def extract_attribute(self, element, selector: str, attribute: str) -> str:
        """요소에서 속성값 추출 (여러 선택자 지원)"""
        selectors = selector.split(", ")
        for sel in selectors:
            try:
                target = element.query_selector(sel.strip())
                if target:
                    value = target.get_attribute(attribute)
                    if value:
                        return value
            except Exception:
                continue
        return ""

    def scrape_current_page(self) -> list[dict]:
        """현재 페이지에서 데이터 스크래핑"""
        container_selectors = config.SELECTORS["item_container"].split(", ")

        items = []
        for selector in container_selectors:
            try:
                found = self.page.query_selector_all(selector.strip())
                if found and len(found) > len(items):
                    items = found
            except Exception:
                continue

        print(f"📦 {len(items)}개 아이템 발견")

        if len(items) == 0:
            print("  ⚠️ 아이템을 찾을 수 없습니다. 선택자를 확인하세요.")
            self._print_page_structure()

        page_data = []
        for idx, item in enumerate(items, 1):
            row = {}
            fields = config.SELECTORS["fields"]

            for field_name, selector in fields.items():
                # 링크와 이미지는 속성값 추출
                if field_name == "link":
                    row[field_name] = self.extract_attribute(item, selector, "href")
                elif field_name == "image":
                    row[field_name] = self.extract_attribute(item, selector, "src")
                else:
                    row[field_name] = self.extract_text(item, selector)

            # 빈 데이터 필터링 (모든 필드가 비어있으면 스킵)
            if any(row.values()):
                page_data.append(row)
                # 첫 2개 필드만 표시
                preview = [v for v in row.values() if v][:2]
                print(f"  [{idx}] {preview}")

        return page_data

    def _print_page_structure(self) -> None:
        """페이지 구조 출력 (디버깅용)"""
        try:
            print("\n  📋 페이지 주요 요소:")
            # 주요 컨테이너 확인
            for tag in ["div", "article", "section", "ul", "li"]:
                elements = self.page.query_selector_all(tag)
                if elements:
                    classes = set()
                    for el in elements[:20]:
                        cls = el.get_attribute("class")
                        if cls:
                            classes.update(cls.split()[:2])
                    if classes:
                        print(f"    {tag}: {', '.join(list(classes)[:5])}")
        except Exception:
            pass

    def handle_pagination(self) -> bool:
        """다음 페이지로 이동 (페이지네이션 처리)"""
        if not config.PAGINATION["enabled"]:
            return False

        try:
            next_selectors = config.PAGINATION["next_button"].split(", ")
            next_button = None

            for selector in next_selectors:
                try:
                    next_button = self.page.query_selector(selector.strip())
                    if next_button and next_button.is_visible():
                        break
                except Exception:
                    continue

            if next_button and next_button.is_visible():
                next_button.click()
                self.page.wait_for_load_state("networkidle")
                self.page.wait_for_timeout(config.WAIT_CONFIG["wait_time"])
                return True
        except Exception as e:
            print(f"⚠️ 페이지네이션 처리 중 오류: {e}")

        return False

    def scrape(self) -> list[dict]:
        """스크래핑 실행"""
        print("\n" + "=" * 50)
        print("🕷️  Web Scraping Agent 시작")
        print("=" * 50 + "\n")

        try:
            self.start_browser()

            # 로그인 수행
            if not self.login():
                print("❌ 로그인 실패로 스크래핑 중단")
                return []

            # 대상 페이지로 이동
            if not self.navigate_to_page():
                return []

            # 첫 페이지 스크래핑
            self.scraped_data = self.scrape_current_page()

            # 페이지네이션 처리
            if config.PAGINATION["enabled"]:
                page_count = 1
                while page_count < config.PAGINATION["max_pages"]:
                    if not self.handle_pagination():
                        print("📄 마지막 페이지 도달")
                        break
                    page_count += 1
                    print(f"\n📄 페이지 {page_count} 스크래핑 중...")
                    page_data = self.scrape_current_page()
                    self.scraped_data.extend(page_data)

            print(f"\n✅ 총 {len(self.scraped_data)}개 데이터 수집 완료")
            return self.scraped_data

        finally:
            self.close_browser()

    def save_to_csv(self) -> str:
        """결과를 CSV 파일로 저장"""
        if not self.scraped_data:
            print("⚠️ 저장할 데이터가 없습니다")
            return ""

        output_path = Path(self.output_file)

        # 타임스탬프 추가 (파일 덮어쓰기 방지)
        if output_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_path.with_stem(f"{output_path.stem}_{timestamp}")

        # CSV 저장
        fieldnames = list(self.scraped_data[0].keys())
        with open(output_path, "w", newline="", encoding=config.OUTPUT_CONFIG["encoding"]) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.scraped_data)

        print(f"\n💾 CSV 저장 완료: {output_path}")
        print(f"   - 총 {len(self.scraped_data)}개 행")
        print(f"   - 컬럼: {', '.join(fieldnames)}")

        return str(output_path)


def main():
    """CLI 엔트리포인트"""
    parser = argparse.ArgumentParser(
        description="Playwright 기반 웹 스크래핑 에이전트 (로그인 지원)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python agent.py
  python agent.py --url https://example.com
  python agent.py --headless false --output result.csv
  python agent.py --skip-login
        """,
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        help="스크래핑할 URL (기본값: config.py의 TARGET_URL)",
    )
    parser.add_argument(
        "--headless",
        type=str,
        choices=["true", "false"],
        help="브라우저 숨김 모드 (기본값: config.py 설정)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="출력 CSV 파일명 (기본값: config.py의 OUTPUT_CONFIG)",
    )
    parser.add_argument(
        "--skip-login",
        action="store_true",
        help="로그인 건너뛰기",
    )

    args = parser.parse_args()

    # headless 문자열을 bool로 변환
    headless = None
    if args.headless:
        headless = args.headless.lower() == "true"

    # 에이전트 실행
    agent = WebScrapingAgent(
        url=args.url,
        headless=headless,
        output_file=args.output,
        skip_login=args.skip_login,
    )

    try:
        data = agent.scrape()
        if data:
            agent.save_to_csv()
            print("\n🎉 스크래핑 완료!")
            sys.exit(0)
        else:
            print("\n⚠️ 데이터를 수집하지 못했습니다. config.py 설정을 확인하세요.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
