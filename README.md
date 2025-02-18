# 📦 NAS_SERVER

> # 📦 NAS_SERVER

> 개인 PC에서 NAS 서버를 구축하는 프로젝트입니다. **FastAPI**와 **Supabase**를 활용하여 구축합니다. 저는 **WSL**에서 구현하였고, WSL과 윈도우 port연결 후 공유기의 DNS를 이용하여, **https** 설정하여 외부에서 https로 접속이 가능하도록 구현하였습니다.

서버 API만 1차적으록 구현 하였고, WEB , APP 버전도 추 후 공개 예정입니다.

This is a project to build NAS servers on personal PCs, leveraging 
It is a project to build a NAS server from a personal PC. It is built using **FastAPI** and **Supabase**. I implemented it in WSL, and after connecting WSL and Windows port, I set up https using the DNS of the router to enable access to https from outside.

Only the server API was first implemented, and the WEB and APP versions will be released later.

---
---
## [API 사용법]
###보러가기(https://docs.google.com/spreadsheets/d/e/2PACX-1vTUklq0EeNiHzqqw37IvZkHaM6BSG68wkQzLh1aZJ8S8_HZM9OoJhJfFRE-KMAV0JKi65dJ_NdO5DzS/pubhtml?gid=481048107&single=true)
---

## ⚙️ 요구 사항 (Requirements)

### 🏗 FastAPI 설치
```bash
pip3 install fastapi
pip3 install "uvicorn[standard]"
```

### 🗄 Supabase 설치

> **⚠️ 주의:**
> - `POSTGRES_PASSWORD` → **SHA-256으로 인코딩된 값 사용**
> - `VAULT_ENC_KEY` → **AES-256 키 사용**

📌 Supabase 공식 문서를 참고하여 개인 설정 진행: [Supabase Self-Hosting Guide](https://supabase.com/docs/guides/self-hosting/docker)

```bash
git clone --filter=blob:none --no-checkout https://github.com/supabase/supabase
cd supabase
git sparse-checkout set --cone docker && git checkout master

# Docker 폴더로 이동
cd docker

# 환경 변수 파일 복사
cp .env.example .env

# 최신 이미지 다운로드
docker compose pull

# 서비스 시작 (백그라운드 실행)
docker compose up -d
```

---

## 🔑 Supabase 설정

### 1️⃣ **Supabase-Kong 접속**
- 접속 주소: `http://localhost:8000`

### 2️⃣ **로그인**
- `supabase/docker/.env`에 설정된 계정으로 로그인

### 3️⃣ **Auth 계정 등록**
- 접속 주소: `http://localhost:8000/project/default/auth/users`

### 4️⃣ **Admin 권한 설정**
- 접속 주소: `http://localhost:8000/project/default/sql/1`
- SQL 쿼리 실행:

```sql
CREATE TABLE roles (
  id UUID REFERENCES auth.users ON DELETE CASCADE,
  role TEXT NOT NULL,
  PRIMARY KEY (id)
);

INSERT INTO roles (id, role)
SELECT id, 'user' FROM auth.users WHERE id = '새로 추가된 유저의 ID';

UPDATE roles
SET role = 'admin'
WHERE id = '변경할 유저의 ID';

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admins can view all users"
ON users
FOR SELECT
USING (EXISTS (
    SELECT 1 FROM roles
    WHERE roles.id = auth.uid() AND roles.role = 'admin'
));
```

---

## 🗄 Create Bucket Policy (스토리지 정책 설정)

```sql
-- 버킷 정책
CREATE POLICY "Enable bucket creation for service role"
ON storage.buckets
FOR INSERT
TO authenticated
WITH CHECK ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable bucket select for service role"
ON storage.buckets
FOR SELECT
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable bucket update for service role"
ON storage.buckets
FOR UPDATE
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' )
WITH CHECK ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable bucket delete for service role"
ON storage.buckets
FOR DELETE
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

-- 오브젝트 정책
CREATE POLICY "Enable object insert for service role"
ON storage.objects
FOR INSERT
TO authenticated
WITH CHECK ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable object select for service role"
ON storage.objects
FOR SELECT
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable object update for service role"
ON storage.objects
FOR UPDATE
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' )
WITH CHECK ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );

CREATE POLICY "Enable object delete for service role"
ON storage.objects
FOR DELETE
TO authenticated
USING ( auth.role() = 'authenticated' OR auth.role() = 'service_role' );
```

---

## 🚀 빠른 시작 (Quick Start)

```bash
docker compose up -d
```

> 💡 **Tip:** 모든 서비스가 정상적으로 실행되었는지 확인하려면 `docker ps`를 실행하세요.

