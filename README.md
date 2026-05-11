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
