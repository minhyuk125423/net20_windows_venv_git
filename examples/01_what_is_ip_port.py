"""
01) IP/Port 개념 맛보기 + DNS로 IP 확인
- host 이름(example.com)을 IP로 바꾸는 과정이 DNS
- port는 "서비스 문" 번호 (80 HTTP, 443 HTTPS)
"""
from __future__ import annotations
import argparse, socket

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="google.co.kr")
    args = ap.parse_args()

    ip = socket.gethostbyname(args.host)
    print(f"host={args.host} -> ip={ip}")
    print("예) https는 보통 443 포트, http는 80 포트를 사용합니다.")

if __name__ == "__main__":
    main()
