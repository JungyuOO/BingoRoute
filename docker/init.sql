\connect skn_travel_db;

-- 벡터 연산을 사용하기 위해 pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 분류/코드 기준 테이블
CREATE TABLE IF NOT EXISTS code_table (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    upper_code VARCHAR(20) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_code_table_self FOREIGN KEY (upper_code)
        REFERENCES code_table(code)
        ON UPDATE CASCADE ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS ix_code_table_upper ON code_table (upper_code);

-- 관광지 기본 정보 테이블
CREATE TABLE IF NOT EXISTS tourist_spot (
    content_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    firstimage VARCHAR(500),
    firstimage2 VARCHAR(500),
    category_code VARCHAR(20),
    category_name VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cat_code FOREIGN KEY (category_code)
        REFERENCES code_table(code)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- 관광지 상세 정보 테이블
CREATE TABLE IF NOT EXISTS tourist_spot_detail (
    id BIGSERIAL PRIMARY KEY,
    content_id VARCHAR(20) NOT NULL,
    address_code VARCHAR(20),
    sigungu_name VARCHAR(100),
    zip_code VARCHAR(20),
    address VARCHAR(200),
    map_x NUMERIC(11, 6),
    map_y NUMERIC(11, 6),
    intro_serial_num INT,
    content_type_id VARCHAR(10),
    tel VARCHAR(50),
    restdate TEXT,
    useseason TEXT,
    usetime TEXT,
    is_parking SMALLINT,
    is_baby_carriage SMALLINT,
    is_pet SMALLINT,
    is_credit_card SMALLINT,
    info_serial_num VARCHAR(50),
    info_name VARCHAR(200),
    info_text TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_content_intro_info UNIQUE (content_id, intro_serial_num, info_serial_num),
    CONSTRAINT fk_detail_sigungu FOREIGN KEY (address_code)
        REFERENCES code_table(code)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- RAG 임베딩 저장 테이블 (JSONB 메타데이터로 검색 필터 지원)
CREATE TABLE IF NOT EXISTS my_vectors (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ############################################################
-- 회원 관리 시스템
-- ############################################################

-- 회원 테이블
CREATE TABLE IF NOT EXISTS accounts_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- CustomUser 추가 필드들
    user_id VARCHAR(50) NOT NULL UNIQUE,
    birth_date DATE,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(100) DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_accounts_user_user_id ON accounts_user (user_id);
CREATE INDEX IF NOT EXISTS ix_accounts_user_email ON accounts_user (email);
CREATE INDEX IF NOT EXISTS ix_accounts_user_username ON accounts_user (username);

-- 찜(jjim) 테이블
CREATE TABLE IF NOT EXISTS jjim (
    jjim_id      BIGSERIAL PRIMARY KEY,
    user_id      BIGINT NOT NULL,
    content_id   VARCHAR(100) NOT NULL,
    jjim_on_off  BOOLEAN     NOT NULL,
    CONSTRAINT fk_jjim_content
        FOREIGN KEY (content_id)
        REFERENCES tourist_spot(content_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT uq_user_content UNIQUE (user_id, content_id),
    CONSTRAINT fk_jjim_user FOREIGN KEY (user_id)
        REFERENCES accounts_user(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- 회원별 여행 테이블
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'trip_status_enum') THEN
        CREATE TYPE trip_status_enum AS ENUM ('PLANNED', 'COMPLETED', 'RECOMMENDED');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS member_trip (
    trip_id     BIGSERIAL       PRIMARY KEY,
    user_id     BIGINT          NOT NULL,
    status      trip_status_enum NOT NULL,
    trip_title  VARCHAR(100)     NOT NULL,
    travel_date DATE,
    created_at  TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_member_trip_user FOREIGN KEY (user_id)
        REFERENCES accounts_user(id)
        ON UPDATE CASCADE ON DELETE CASCADE
);

-- 각 여행별 관광지 테이블
CREATE TABLE IF NOT EXISTS member_trip_itinerary (
    trip_id    BIGINT        NOT NULL,
    seq        SMALLINT      NOT NULL,
    content_id VARCHAR(100)  NOT NULL,
    visit_date DATE,
    stay_time  INTERVAL,
    PRIMARY KEY (trip_id, seq),
    CONSTRAINT fk_itinerary_trip
        FOREIGN KEY (trip_id)
        REFERENCES member_trip(trip_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_itinerary_content
        FOREIGN KEY (content_id)
        REFERENCES tourist_spot(content_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_member_trip_itinerary_content
    ON member_trip_itinerary (content_id);

-- ############################################################
-- 밑에부터는 회원 관리 시스템
-- ############################################################

-- 회원 테이블 
CREATE TABLE IF NOT EXISTS accounts_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- CustomUser 추가 필드들
    user_id VARCHAR(50) NOT NULL UNIQUE,
    birth_date DATE,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    is_email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    email_verification_token VARCHAR(100) DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_accounts_user_user_id ON accounts_user (user_id);
CREATE INDEX IF NOT EXISTS ix_accounts_user_email ON accounts_user (email);
CREATE INDEX IF NOT EXISTS ix_accounts_user_username ON accounts_user (username);
