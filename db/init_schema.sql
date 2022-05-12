CREATE TABLE "sites" (
  id bigint PRIMARY KEY NOT NULL UNIQUE,
  name varchar NOT NULL,
  zipcode varchar NOT NULL,
  created_at timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "data" (
  site_id bigint PRIMARY KEY NOT NULL,
  date varchar  NOT NULL,
  firstshot bigint NOT NULL,
  secondshot bigint NOT NULL,
  created_at timestamptz NOT NULL DEFAULT (now()),
  unique(site_id, date)
);

ALTER TABLE data ADD FOREIGN KEY (site_id) REFERENCES sites(id);

CREATE UNIQUE INDEX ON sites (name);
CREATE UNIQUE INDEX ON sites (id);
CREATE UNIQUE INDEX ON data (site_id);