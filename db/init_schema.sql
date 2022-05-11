CREATE TABLE "sites" (
  "id" bigserial PRIMARY KEY,
  "name" varchar NOT NULL,
  "zipcode" bigint NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "data" (
  "id" bigserial PRIMARY KEY,
  "site_id" bigint NOT NULL,
  "date" bigint NOT NULL,
  "firstshot" bigint NOT NULL,
  "secondshot" bigint NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

ALTER TABLE "data" ADD FOREIGN KEY ("site_id") REFERENCES "sites" ("id");

CREATE INDEX ON "sites" ("name");
CREATE INDEX ON "data" ("site_id");

);
