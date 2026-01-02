"""
04) TCP 접속 테스트: cleaned_sites.txt의 URL 목록을 읽어서 포트 오픈 여부 확인 후 result.txt로 저장
"""
#exe 파일 실행방법
# 1.실행 전에 터미널(CMD) 등에 pip install pyinstaller 명령어 입력
# 2. pyinstaller --onefile tcp_check.py

from __future__ import annotations

import argparse
import socket
import time
from urllib.parse import urlparse

IN_FILE = "cleaned_sites.txt"
OUT_FILE = "result.txt"

def tcp_connect(host: str, port: int, timeout: float) -> dict:
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"ok": True, "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as e:
        return {"ok": False, "latency_ms": int((time.time() - t0) * 1000), "error": str(e)}

# URL 파일 읽기 : 주석과 빈줄은 무시
def iter_urls(path: str, encoding: str):
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            yield s


def parse_host_port(url: str, default_port: int) -> tuple[str, int]:
    """
    cleaned_sites.txt에 아래 형태들이 섞여 있어도 최대한 처리:
      - https://www.naver.com
      - http://example.com
      - www.google.com   (scheme 없음)
      - https://example.com:8443/path
    """
    u = url.strip()

    # scheme 없으면 https로 간주(원하면 여기서 http로 바꿔도 됨)
    if "://" not in u:
        u = "https://" + u

    p = urlparse(u)

    # urlparse에서 hostname/port 제공
    host = p.hostname or ""
    port = p.port

    if not host:
        # 파싱 실패 시 원문에서 최대한 host만 추출(마지막 안전장치)
        host = url.split("/")[0].replace("https://", "").replace("http://", "").split(":")[0].strip()

    if port is None:
        if (p.scheme or "").lower() == "http":
            port = 80
        elif (p.scheme or "").lower() == "https":
            port = 443
        else:
            port = default_port

    return host, int(port)

# URL 추가
def add_url(url_path: str, new_url: str):
    with open(url_path, "a", encoding="utf-8") as f:
        f.write(new_url.strip() + "\n")
    print(f"URL이 추가되었습니다.")

# URL 삭제
def delete_url(url_path: str, del_url: str):
    with open(url_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(url_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip() != del_url.strip():
                f.write(line)
    print(f"URL이 삭제되었습니다.")

# URL 리스트 불러오기
def load_urls(path: str, encoding: str) -> list[str]:
    urls = []
    with open(path, "r", encoding=encoding) as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                urls.append(s)
    return urls

# URL 체크 : TCP 연결 시도 및 결과 기록
def check(infile, outfile, timeout, default_port, encoding):
    total = 0
    ok_cnt = 0
    ok_urls = []
    fail_urls = []

    # 결과 파일
    with open(outfile, "w", encoding="utf-8", newline="\n") as out:
        out.write("url\thost\tport\tok\tlatency_ms\terror\n")

        # 파일 내 URL 반복
        for url in iter_urls(infile, encoding):
            total += 1
            host, port = parse_host_port(url, default_port)
            if not host or not isinstance(port, int):
                res = {"ok": False, "latency_ms": 0, "error": "Invalid host/port"}
            else:
                res = tcp_connect(host, port, timeout)

        # 오류 구분
            if res.get("ok"):
                ok_cnt += 1
                ok_urls.append(url)
            else:
                fail_urls.append(url)
            out.write(
                f"{url}\t{host}\t{port}\t{res.get('ok')}\t{res.get('latency_ms')}\t{res.get('error', '')}\n"
            )
    return total, ok_cnt, ok_urls, fail_urls

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infile", default="IN_FILE")
    ap.add_argument("--outfile", default="OUT_FILE")
    ap.add_argument("--timeout", type=float, default=1.5)
    ap.add_argument("--default-port", type=int, default=443, help="scheme 판단 불가시 사용할 기본 포트")
    ap.add_argument("--encoding", default="utf-8", help="입력 파일 인코딩(예: utf-8, cp949)")
    args = ap.parse_args()
    
    total, ok_cnt, ok_urls, fail_urls = check(
            args.infile,
            args.outfile,
            args.timeout,
            args.default_port,
            args.encoding,
        )
    
    while True:
        print(f"\n총 {total}줄 확인, 정상={ok_cnt}개, 에러={total-ok_cnt}개")
        print(f"saved: {args.outfile}\n")

        print("=== 정상 URL 목록 ===")
        for u in ok_urls:
            print(u)

        print("\n=== 오류 URL 목록 ===")
        for u in fail_urls:
            print(u)
             
        ac = CRUD(args.infile)
        if ac == "EXIT":
            break
        elif ac == "CONTINUE":
            total, ok_cnt, ok_urls, fail_urls = check(
            args.infile,
            args.outfile,
            args.timeout,
            args.default_port,
            args.encoding,
        )
    

def CRUD(url_path: str):
    print("----------------------")
    print("무엇을 실행하시겠습니까?\n")
    print("1: URL 추가\n")
    print("2: URL 삭제\n")
    print("3: End\n")
    print("----------------------")

    inpt = input("Enter choice: ").strip()
    if inpt.isdigit():            
        if inpt == "1":
            new_url = input("추가할 URL을 입력하세요: ").strip()
            add_url(url_path, new_url)
            return "CONTINUE"
        elif inpt == "2":
            del_url = input("삭제할 URL을 입력하세요: ").strip()
            delete_url(url_path, del_url)
            return "CONTINUE"
        elif inpt == "3":
            print("프로그램을 종료합니다")
            return "EXIT"
        else:
            print("\n1, 2, 3 중에서만 입력 가능합니다")
            return "CONTINUE"
    else:
        print("\n1, 2, 3 중에서만 입력 가능합니다")
        return "CONTINUE"

if __name__ == "__main__":
    main()