from sickle import Sickle
from sickle.oaiexceptions import OAIError
import xml.etree.ElementTree as ET
import time
import os

# Initialize Sickle
sickle = Sickle("http://export.arxiv.org/oai2")

# Function to download records
def download_records(metadata_prefix, set_spec, num_records, output_file):
    records = sickle.ListRecords(metadataPrefix=metadata_prefix, set=set_spec)

    root = ET.Element("records")
    count = 0
    retries = 0
    max_retries = 5

    for record in records:
        if count >= num_records:
            break
        try:
            record_xml = record.raw
            record_element = ET.fromstring(record_xml)
            root.append(record_element)
            count += 1
            retries = 0  # Reset retries on successful fetch
            print(f"Downloaded record {count}/{num_records}")
        except OAIError as e:
            print(f"OAIError: {e}")
            if retries < max_retries:
                retries += 1
                wait_time = retries * 5  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Aborting.")
                break
        except Exception as e:
            print(f"Error: {e}")
            if retries < max_retries:
                retries += 1
                wait_time = retries * 5  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Aborting.")
                break

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Saved {count} records to {output_file}")

if __name__ == "__main__":
    metadata_prefix = "oai_dc"  # Use "arXiv" for more detailed metadata
    set_spec = "cs"  # Use a specific set, e.g., "cs" for computer science, "math" for mathematics
    num_records = 30  # Specify the number of records to download
    output_file = os.path.join("data", "arxiv_data.xml")  # Specify the output XML file

    download_records(metadata_prefix, set_spec, num_records, output_file)
    print(f"Downloaded {num_records} records and saved to {output_file}")
