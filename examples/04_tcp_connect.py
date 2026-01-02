"""
04) TCP 접속 테스트: 포트가 열려 있는지(가장 기본)
"""
from __future__ import annotations
import argparse, socket, time

def tcp_connect(host: str, port: int, timeout: float) -> dict:
    t0 = time.time()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"ok": True, "latency_ms": int((time.time()-t0)*1000)}  #시간 표시
    except Exception as e:
        return {"ok": False, "latency_ms": int((time.time()-t0)*1000), "error": str(e)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="naver.com")  #host 주소가 없을 경우 디폴트 경로 사용
    ap.add_argument("--port", type=int, default=443)
    ap.add_argument("--timeout", type=float, default=1.5)
    args = ap.parse_args()

    print(tcp_connect(args.host, args.port, args.timeout))

if __name__ == "__main__":
    main()
