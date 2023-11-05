-- Run as the newly created user from database_setup.sql

CREATE TABLE energy_raw (
    record_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255) NOT NULL, -- either 'dsmr' or 'solar_modbus'
    metric VARCHAR(255),
    value NUMERIC,
    unit VARCHAR(255)
);
