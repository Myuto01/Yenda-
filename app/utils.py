import hashlib
from django.urls import path
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def hash_trip_id(trip_id):
    """
    Hashes the trip_id using SHA-256 and returns the result as a URL-safe base64 string.
    """
    trip_id_bytes = force_bytes(str(trip_id))  # Ensure trip_id is encoded as bytes
    hashed_trip_id = hashlib.sha256(trip_id_bytes).digest()
    return urlsafe_base64_encode(hashed_trip_id)

def decode_hashed_trip_id(uidb64):
    """
    Decodes the hashed trip_id back to its original value.
    """
    # Decode the base64-encoded string
    hashed_trip_id = urlsafe_base64_decode(force_bytes(uidb64))
    return hashed_trip_id.decode()



# This dictionary will store the mapping between original trip IDs and hashed trip IDs
trip_id_mapping = {}

# Assuming you have a mapping function to generate and store hashed trip IDs
def generate_and_store_hashed_trip_id(trip_id):
    hashed_trip_id = hash_trip_id(trip_id)
    trip_id_mapping[hashed_trip_id] = trip_id  # Store the mapping between hashed trip ID and original trip ID
    print("Hashed trip ID:", hashed_trip_id)
    print("Original trip ID:", trip_id)
    return hashed_trip_id