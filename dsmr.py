import socket, select
import datetime, re

if __name__ == '__main__':
    
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ip = socket.gethostbyname("192.168.68.61")
    port = 9988
    address = (ip, port)
    # client.setblocking(False)
    client.connect(address)

    code_mapping = {
        "1.8.1": {
            "label": "Actieve energie afname dagtarief",
            "description": "Totale afname van energie in kWh dagtarief"
        },
        "1.8.2": {
            "label": "Actieve energie afname nachttarief",
            "description": "Totale afname van energie in kWh nachttarief"
        },
        "1.8.0": {
            "label": "Totale actieve energie afname",
            "description": "Totale afname van energie in kWh"
        },

        "2.8.1": {
            "label": "Actieve energie injectie dagtarief",
            "description": "Totale injectie van energie in kWh dagtarief"
        },
        "2.8.2": {
            "label": "Actieve energie injectie nachttarief",
            "description": "Totale injectie van energie in kWh nachttarief"
        },
        "2.8.0": {
            "label": "Totale actieve energie injectie",
            "description": "Totale injectie van energie in kWh"
        },
        
        "1.7.0": {
            "label": "Afgenomen ogenblikkelijk vermogen",
            "description": "Afgenomen ogenblikkelijk vermogen in kW"
        },
        
        "2.7.0": {
            "label": "Geïnjecteerd ogenblikkelijk vermogen",
            "description": "Geïnjecteerd ogenblikkelijk vermogen in kW"
        }
    }

    while True:
        print("-")
        print(f"{ datetime.datetime.utcnow() }")
        ready = select.select([client], [], [], 3)
        if ready[0]:
            data = client.recv(2048)
            data_parsed = data.decode("utf-8").split("\r\n")
            for code in code_mapping:
                try:
                    recorded_data = next((data_point for data_point in data_parsed if data_point.find(code) > 0), None)
                    data_point_value = float(re.findall(r"\(([\d\.]+)\*", recorded_data)[0])
                    data_point_unit = re.findall(r"\*(\w+)\)$", recorded_data)[0]
                except Exception as e:
                    data_point_value = 0
                    data_point_unit = "None"
                print(f"{ code_mapping[code]['label'] }: { data_point_value } { data_point_unit }")
        else:
            print("No data")