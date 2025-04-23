import socket
import ipinfo
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import folium
from folium.plugins import MarkerCluster

handler = ipinfo.getHandler("")


def extract_domains_from_history():
    with open("history-data.txt") as file:
        urls = file.readlines()

    domain_names = set()
    for url in urls:
        url = url.strip()
        if url:
            parsed_url = urlparse(url)
            if parsed_url.netloc:
                final_url = parsed_url.netloc.split(":")[0]
                domain_names.add(final_url)

    return lookup_domain_ips(domain_names)


def lookup_domain_ips(domain_names):
    unique_ips = set()
    for domain in domain_names:
        try:
            ip = socket.gethostbyname(domain)
            unique_ips.add(ip)
        except socket.gaierror:
            print(f"Not found: {domain}.")
    return unique_ips


def fetch_ip_geolocation(ip_address):
    try:
        details = handler.getDetails(ip_address)
        return details.all
    except Exception as e:
        print(f"Error getting details for {ip_address}: {e}")
        return None


def collect_geolocation_data(ip_addresses):
    geolocation_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ip = {executor.submit(fetch_ip_geolocation, ip): ip for ip in ip_addresses}

        for future in as_completed(future_to_ip):
            ip = future_to_ip[future]
            try:
                data = future.result()
                if data:
                    geolocation_results.append(data)
                    print(f"Processed: {ip}")
            except Exception as e:
                print(f"Exception for {ip}: {e}")
    return geolocation_results


def main():
    ip_addresses = extract_domains_from_history()
    geolocation_data = collect_geolocation_data(ip_addresses)
    print(f"Total processed IPs: {len(geolocation_data)}")

    # Create a map centered at a default location
    map = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB dark_matter")

    # Add a marker cluster
    marker_cluster = MarkerCluster().add_to(map)

    # Add markers for each IP location
    for location in geolocation_data:
        try:
            lat = float(location["latitude"])
            lon = float(location["longitude"])

            # Extract additional information
            ip = location.get("ip", "Unknown")
            city = location.get("city", "Unknown")
            country = location.get("country_name", "Unknown")
            org = location.get("org", "Unknown")

            popup_text = f"""
            <b>IP</b>: {ip}<br>
            <b>City</b>: {city}<br>
            <b>Country</b>: {country}<br>
            <b>Organization</b>: {org}
            """

            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(marker_cluster)
        except (KeyError, ValueError) as e:
            print(f"Could not map location: {e}")

    # Save the map as an HTML file
    map.save("interactive_ip_map.html")
    print("Interactive map saved as 'interactive_ip_map.html'")


if __name__ == "__main__":
    main()