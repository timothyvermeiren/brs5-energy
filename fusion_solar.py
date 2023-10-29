from fusion_solar_py.client import FusionSolarClient
from dotenv import load_dotenv
import os, requests, pickle, sys, time

load_dotenv()

# As indicated in the documentation, repeated logins will trigger a captcha after a while. We can store our session by pickling it, and reusing it later.

if os.path.exists("fusion_solar_session.pkl"):
    try:
        print("It looks like we have an existing session stored/pickled. We're going to try and reuse it first.")
        # Try to reuse the session
        with open("fusion_solar_session.pkl", "rb") as f:
            fusion_solar_session = pickle.load(f)
        fusion_solar_client = FusionSolarClient(username=os.environ.get("fusion_solar_username"), password=os.environ.get("fusion_solar_password"), huawei_subdomain="region03eu5", session=fusion_solar_session)
    except Exception as e:
        print(f"Something went wrong reusing the existing session:\n\t{e}")
        print("Creating a new session instead.")

if "fusion_solar_client" not in locals():
    try:
        fusion_solar_session = requests.Session()
        fusion_solar_client = FusionSolarClient(username=os.environ.get("fusion_solar_username"), password=os.environ.get("fusion_solar_password"), huawei_subdomain="region03eu5", session=fusion_solar_session)
        try:
            with open("fusion_solar_session.pkl", "wb") as f:
                pickle.dump(fusion_solar_session, f)
        except Exception as e:
            print(f"Something went wrong storing the session:\n\t{e}")
            print("We can probably continue without storing it, though...")
    except Exception as e:
        print(f"Something went wrong setting up a new session:\n\t{e}")
        sys.exit()

fusion_solar_client.log_out()

while True:

    fusion_solar_stats = fusion_solar_client.get_power_status()

    # print all stats
    print(f"Current power: {fusion_solar_stats.current_power_kw} kW")
    print(f"Total power today: {fusion_solar_stats.total_power_today_kwh} kWh")
    print(f"Total power: {fusion_solar_stats.total_power_kwh} kWh")

    time.sleep(60) # This updates every minute via the API. We'll have to pull local data if we want faster updates.

# log out - just in case
fusion_solar_client.log_out()