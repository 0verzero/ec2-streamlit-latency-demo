# EC2 Streamlit Network Latency Demo

AWS Learner Lab EC2 환경에서 실행할 수 있는 간단한 Streamlit 앱입니다.

버튼을 누르면 EC2 서버 기준으로 다음 정보를 출력합니다.

- 서버 호스트명
- 서버 로컬 IP
- EC2 Public IP 확인
- DNS 조회 지연시간
- TCP 연결 지연시간
- HTTP 요청 지연시간
- 전체 처리 시간
- 버튼 클릭 및 측정 완료 로그

> 참고: 이 앱은 EC2 서버가 외부 인터넷으로 나갈 때의 지연시간을 측정합니다.  
> 브라우저와 EC2 사이의 정확한 왕복 지연시간은 순수 Streamlit 코드만으로는 직접 측정하기 어렵습니다.

## 파일 구성

```text
ec2-streamlit-latency-demo/
├─ app.py
├─ requirements.txt
├─ README.md
├─ .gitignore
└─ .streamlit/
   └─ config.toml
```

## EC2 실행 방법

EC2에 접속한 뒤 아래 명령어를 실행합니다.

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip git

git clone https://github.com/본인아이디/ec2-streamlit-latency-demo.git
cd ec2-streamlit-latency-demo

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 브라우저 접속

EC2의 Public IPv4 주소를 확인한 뒤 브라우저에서 아래 주소로 접속합니다.

```text
http://EC2_PUBLIC_IP:8501
```

예시:

```text
http://3.91.123.45:8501
```

## 보안 그룹 설정

EC2 보안 그룹 인바운드 규칙에 다음 포트가 필요합니다.

| 유형 | 포트 | 소스 |
|---|---:|---|
| SSH | 22 | 내 IP 또는 0.0.0.0/0 |
| Custom TCP | 8501 | 내 IP 또는 0.0.0.0/0 |

실습과 녹화가 끝나면 22번과 8501번 포트는 다시 닫거나 내 IP로 제한하는 것을 권장합니다.
