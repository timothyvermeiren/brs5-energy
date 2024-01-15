-- As postgres on any database
CREATE DATABASE brs5_energy;
CREATE USER brs5_energy WITH ENCRYPTED PASSWORD 'hunter2';
GRANT ALL PRIVILEGES ON DATABASE brs5_energy TO brs5_energy;
-- Reconnect to brs5_energy as postgres
GRANT ALL PRIVILEGES ON SCHEMA public TO brs5_energy;

-- Then, run as brs5_energy

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

-- DSMR: Gas measurements are only performed every so often, and only show the cumulative total, so we "translate" that here. 
CREATE VIEW er_gas_consumption AS
WITH er_gas_consumption AS (
	SELECT
		MIN(record_timestamp) AS record_timestamp,
		"source",
		metric,
		value,
		unit
	FROM public.energy_raw er
	WHERE unit = 'm3'
	GROUP BY "source", metric, value, unit 
	ORDER BY MIN(record_timestamp) ASC
)
SELECT
	record_timestamp,
	LAG(record_timestamp) OVER time_window AS previous_timestamp,
	record_timestamp - LAG(record_timestamp) OVER time_window AS time_interval,
	EXTRACT(epoch FROM record_timestamp - LAG(record_timestamp) OVER time_window) AS time_seconds,
	"source",
	metric,
	value,
	LAG(value) OVER time_window AS previous_value,
	value - LAG(value) OVER time_window AS total_consumption,
	(value - LAG(value) OVER time_window) / (EXTRACT(epoch FROM record_timestamp - LAG(record_timestamp) OVER time_window) / 3600) AS consumption_m3_per_h, 
	unit
FROM er_gas_consumption
WINDOW time_window AS (ORDER BY record_timestamp)
