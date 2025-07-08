import cv2
import numpy as np
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os

# Azure Blob Storage Config
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=numberplates;AccountKey=UVB9HnEAWKDlq5lbGafLsz183mne7Y216RHliq4LxEyCflFo3SADIvALVmI1HSS8miXH2frLqshr+AStUDZCjg==;EndpointSuffix=core.windows.net"
CONTAINER_NAME = "vehicle-plate-images"

# Azure OCR Config
COMPUTER_VISION_ENDPOINT = "https://numberplate-cv.cognitiveservices.azure.com/"
COMPUTER_VISION_SUBSCRIPTION_KEY = "71kxuEKo6qhfr08KBcyuXmCk7BzetT7HoJkyz1NGqUk3Hg2kImPtJQQJ99ALACGhslBXJ3w3AAAFACOG1HuX"

# Initialize Clients
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
computer_vision_client = ComputerVisionClient(COMPUTER_VISION_ENDPOINT, CognitiveServicesCredentials(COMPUTER_VISION_SUBSCRIPTION_KEY))

def download_image_from_blob(blob_name, download_path):
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
    with open(download_path, "wb") as file:
        file.write(blob_client.download_blob().readall())
    print(f"Image downloaded to {download_path}")

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    enhanced_image_path = "enhanced_image.jpg"
    cv2.imwrite(enhanced_image_path, thresh)
    print(f"Preprocessed image saved at {enhanced_image_path}")
    return enhanced_image_path

def perform_ocr(image_path):
    with open(image_path, "rb") as image_stream:
        result = computer_vision_client.read_in_stream(image_stream, raw=True)
        operation_location = result.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

    # Poll for the OCR result
    while True:
        result = computer_vision_client.get_read_result(operation_id)
        if result.status not in [OperationStatusCodes.not_started, OperationStatusCodes.running]:
            break

    if result.status == OperationStatusCodes.succeeded:
        license_plate_text = []
        for read_result in result.analyze_result.read_results:
            for line in read_result.lines:
                license_plate_text.append(line.text)
        return license_plate_text
    return []

def main():
    # Image details
    blob_name = "Cars36.png"
    local_image_path = "D:\PYTHON_ML\Data Sets\images\Cars36.png"

    # Step 1: Download the image
    download_image_from_blob(blob_name, local_image_path)

    # Step 2: Preprocess the image
    enhanced_image_path = preprocess_image(local_image_path)

    # Step 3: Perform OCR
    detected_text = perform_ocr(enhanced_image_path)
    print("Detected License Plate Text:", detected_text)

if __name__ == "__main__":
    main()
