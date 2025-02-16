# 📦 NAS_SERVER

> 개인 PC에서 NAS 서버를 구축하는 프로젝트입니다. FastAPI와 Supabase를 활용하여 구축합니다.

This is a project to build NAS servers on personal PCs, leveraging **FastAPI** and **Supabase**.

---

## ⚙️ 요구 사항 (Requirements)

### 🏗 FastAPI 설치
```bash
pip3 install fastapi
pip3 install "uvicorn[standard]"
```

### 🗄 Supabase 설치
> **주의:**
> - `POSTGRES_PASSWORD` -> SHA-256으로 인코딩된 값 사용
> - `VAULT_ENC_KEY` -> AES-256 키 사용

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

# 전체 컨테이너 삭제
docker rm $(docker ps -a -q)

# 전체 이미지 삭제
docker rmi $(docker images -q)
```

#### 🚨 ERROR 발생 시
```bash
** (ErlangError) Erlang error: {:badarg, {'aead.c', 90}, 'Unknown cipher or invalid key size'}:

  * 1st argument: Unknown cipher or invalid key size

    (crypto 5.1.3) crypto.erl:985: :crypto.crypto_one_time_aead(:aes_256_gcm, "gD1Yx2DSR8IBUnzsPcOjwCQqbAmA5IF+C/0c5/B1/P8=", <<88, 118, 194, 91, 119, 3, 195, 101, 41, 219, 189, 136, 12, 141, 49, 93>>, "0ce939249d02573e51e022df82e27bfd2db209be30fb21e04239a6361a49b491", "AES256GCM", 16, true)
    (cloak 1.1.2) lib/cloak/ciphers/aes_gcm.ex:47: Cloak.Ciphers.AES.GCM.encrypt/2
    (supavisor 1.1.56) lib/cloak_ecto/type.ex:37: Supavisor.Encrypted.Binary.dump/1
    (ecto 3.10.3) lib/ecto/type.ex:931: Ecto.Type.process_dumpers/3
    (ecto 3.10.3) lib/ecto/repo/schema.ex:1015: Ecto.Repo.Schema.dump_field!/6
    (ecto 3.10.3) lib/ecto/repo/schema.ex:1028: anonymous fn/6 in Ecto.Repo.Schema.dump_fields!/5
    (stdlib 4.3) maps.erl:411: :maps.fold_1/3
    nofile:29: (file)
```
---

### ✅ 해결 방법
```bash
VAULT_ENC_KEY -> key를 ase_256키 생성 -> base64 인코딩 -> 해당 값을 .env에 넣기기
```



---

## 🔑 Admin 권한 설정
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

## 🗄 Create Bucket Policy
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
