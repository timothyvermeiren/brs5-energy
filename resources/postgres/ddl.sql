-- Run as the newly created user from database_setup.sql

CREATE TABLE energy_raw (
    record_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255) NOT NULL, -- either 'dsmr' or 'solar_modbus'
    metric VARCHAR(255),
    value NUMERIC,
    unit VARCHAR(255)
);

-- Solar forecast is stored in the same format for convenience (it could be unioned if desired). It comes in this format from the source anyway.
CREATE TABLE solar_forecast (
    record_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(255) NOT NULL, -- 'forecast.solar'
    metric VARCHAR(255),
    value NUMERIC,
    unit VARCHAR(255)
);
