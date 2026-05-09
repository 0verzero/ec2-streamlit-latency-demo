import platform
import socket
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
import streamlit as st


TCP_TARGETS = [
    ("Google DNS", "8.8.8.8", 53),
    ("GitHub HTTPS", "github.com", 443),
    ("PyPI HTTPS", "pypi.org", 443),
    ("Google HTTPS", "www.google.com", 443),
]

HTTP_TARGETS = [
    ("Public IP 확인", "https://api.ipify.org?format=json"),
    ("GitHub", "https://github.com"),
    ("PyPI", "https://pypi.org"),
    ("Google", "https://www.google.com"),
]


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_local_ip() -> str:
    """Return the private/local IP used for outbound traffic."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception as exc:
        return f"확인 실패: {exc}"


def measure_dns(host: str) -> dict:
    start = time.perf_counter()
    try:
        result = socket.getaddrinfo(host, None)
        elapsed_ms = (time.perf_counter() - start) * 1000
        addresses = sorted({item[4][0] for item in result})
        return {
            "대상": host,
            "상태": "성공",
            "지연시간(ms)": round(elapsed_ms, 2),
            "결과": ", ".join(addresses[:3]),
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "대상": host,
            "상태": "실패",
            "지연시간(ms)": round(elapsed_ms, 2),
            "결과": str(exc),
        }


def measure_tcp(name: str, host: str, port: int, timeout: float = 3.0) -> dict:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "대상": name,
            "호스트": f"{host}:{port}",
            "상태": "성공",
            "지연시간(ms)": round(elapsed_ms, 2),
            "비고": "TCP 연결 성공",
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "대상": name,
            "호스트": f"{host}:{port}",
            "상태": "실패",
            "지연시간(ms)": round(elapsed_ms, 2),
            "비고": str(exc),
        }


def measure_http(name: str, url: str, timeout: float = 5.0) -> dict:
    start = time.perf_counter()
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "ec2-streamlit-latency-demo/1.0"},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        content_length = len(response.content or b"")
        return {
            "대상": name,
            "URL": url,
            "상태": "성공",
            "HTTP 코드": response.status_code,
            "지연시간(ms)": round(elapsed_ms, 2),
            "응답 크기(bytes)": content_length,
        }
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "대상": name,
            "URL": url,
            "상태": "실패",
            "HTTP 코드": "-",
            "지연시간(ms)": round(elapsed_ms, 2),
            "응답 크기(bytes)": "-",
            "오류": str(exc),
        }


def get_public_ip() -> str:
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        response.raise_for_status()
        return response.json().get("ip", "확인 실패")
    except Exception as exc:
        return f"확인 실패: {exc}"


st.set_page_config(
    page_title="EC2 Network Latency Demo",
    page_icon="🌐",
    layout="wide",
)

st.title("🌐 EC2 Streamlit 네트워크 레이턴시 측정 데모")
st.write(
    "AWS Learner Lab EC2에서 실행되는 Streamlit 앱입니다. "
    "버튼을 누르면 EC2 서버 기준의 인터넷 연결 정보와 간단한 지연시간을 측정합니다."
)

st.info(
    "참고: 이 앱은 EC2 서버가 외부 사이트로 접속할 때의 DNS/TCP/HTTP 지연시간을 측정합니다. "
    "브라우저 ↔ EC2 사이의 정확한 왕복 지연시간은 순수 Streamlit 코드만으로는 직접 측정하기 어렵습니다."
)

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("서버 호스트명", socket.gethostname())
with col2:
    st.metric("서버 로컬 IP", get_local_ip())
with col3:
    st.metric("Python 버전", platform.python_version())

st.write("### 서버 환경 정보")
server_info = {
    "측정 기준": "EC2 서버 내부",
    "OS": platform.platform(),
    "시스템": platform.system(),
    "머신": platform.machine(),
    "현재 시각": now_text(),
}
st.json(server_info)

st.divider()

if st.button("🚀 레이턴시 및 인터넷 연결 정보 측정하기", type="primary"):
    total_start = time.perf_counter()
    measured_at = now_text()
    print(f"[LOG] {measured_at} - latency check button clicked", flush=True)

    with st.spinner("네트워크 상태를 측정하는 중입니다..."):
        public_ip = get_public_ip()

        dns_hosts = ["github.com", "pypi.org", "www.google.com", "api.ipify.org"]
        dns_results = [measure_dns(host) for host in dns_hosts]

        tcp_results = [
            measure_tcp(name, host, port)
            for name, host, port in TCP_TARGETS
        ]

        http_results = [
            measure_http(name, url)
            for name, url in HTTP_TARGETS
        ]

    total_elapsed_ms = (time.perf_counter() - total_start) * 1000
    print(
        f"[LOG] {now_text()} - latency check completed / total_elapsed_ms={total_elapsed_ms:.2f} / public_ip={public_ip}",
        flush=True,
    )

    st.success("측정이 완료되었습니다.")

    a, b, c = st.columns(3)
    a.metric("측정 시각", measured_at)
    b.metric("EC2 Public IP", public_ip)
    c.metric("전체 처리 시간", f"{total_elapsed_ms:.2f} ms")

    st.write("### 1. DNS 조회 지연시간")
    st.table(dns_results)

    st.write("### 2. TCP 연결 지연시간")
    st.table(tcp_results)

    st.write("### 3. HTTP 요청 지연시간")
    st.table(http_results)

    st.write("### 과제 영상 확인 포인트")
    st.write("- 버튼 클릭 시 EC2 터미널에 `[LOG] latency check button clicked` 로그가 출력됩니다.")
    st.write("- 측정 완료 시 EC2 터미널에 전체 처리 시간과 Public IP가 출력됩니다.")
    st.write("- 브라우저에는 DNS/TCP/HTTP 지연시간 표가 출력됩니다.")

else:
    st.warning("위 버튼을 눌러 네트워크 상태를 측정하세요.")

st.divider()
st.caption("Open Source Software Practice - AWS Learner Lab EC2 Streamlit Deployment")
