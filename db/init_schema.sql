CREATE TABLE "sites" (
  "id" bigint PRIMARY KEY,
  "name" varchar NOT NULL,
  "zipcode" varchar NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "data" (
  "site_id" bigint NOT NULL,
  "date" varchar  NOT NULL,
  "firstshot" bigint NOT NULL,
  "secondshot" bigint NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

ALTER TABLE "data" ADD FOREIGN KEY ("site_id") REFERENCES "sites" ("id");

CREATE UNIQUE INDEX ON "sites" ("name");
CREATE UNIQUE INDEX ON "sites" ("id");
CREATE UNIQUE INDEX ON "data" ("site_id");
CREATE UNIQUE INDEX ON "data" ("date");