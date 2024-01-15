CREATE DATABASE brs5_energy;

CREATE USER brs5_energy WITH ENCRYPTED PASSWORD '';
GRANT ALL PRIVILEGES ON DATABASE brs5_energy TO brs5_energy;

-- As it's not possible to switch databases interactively or specify a schema like this when granting privileges ...
-- GRANT ALL PRIVILEGES ON SCHEMA brs5_energy.public TO brs5_energy;
-- ... it's probably best to connect to the brs5_energy database as the postgres user after creating it and just running this
-- GRANT ALL PRIVILEGES ON SCHEMA public TO brs5_energy;