"""
Register Face from Image File
Properly registers a face image into the database
"""

import cv2
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from face_verifier import FaceVerifier

def main():
    print("="*60)
    print("Face Registration from Image File")
    print("="*60)
    print()
    
    # Initialize face verifier
    verifier = FaceVerifier()
    
    # Get image path
    image_path = input("Enter image file path: ").strip()
    
    if not image_path:
        # Try to find the WhatsApp image
        default_path = "data/faces/01/WhatsApp Image 2026-01-24 at 18.41.05.jpeg"
        if os.path.exists(default_path):
            image_path = default_path
            print(f"Using: {image_path}")
        else:
            print("No image path provided!")
            return
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File not found: {image_path}")
        return
    
    # Load image
    print(f"\nLoading image: {image_path}")
    frame = cv2.imread(image_path)
    
    if frame is None:
        print("Error: Could not load image!")
        return
    
    print(f"Image loaded: {frame.shape[1]}x{frame.shape[0]}")
    
    # Show image
    cv2.imshow("Image to Register", frame)
    print("\nShowing image... Press any key to continue")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Get person ID
    person_id = input("\nEnter Person ID (e.g., '01', '123', 'john'): ").strip()
    
    if not person_id:
        print("Error: Person ID is required!")
        return
    
    # Get person name
    person_name = input("Enter Person Name (e.g., 'John Doe', 'Akash'): ").strip()
    
    # Register face
    print(f"\nRegistering face...")
    print(f"  ID: {person_id}")
    if person_name:
        print(f"  Name: {person_name}")
    
    success, message, bbox = verifier.register_face(frame, person_id, person_name)
    
    if success:
        print(f"\n✓ {message}")
        print(f"  Face detected at: {bbox}")
        print(f"\nRegistered faces in database:")
        for pid in verifier.database.keys():
            name = verifier.names_database.get(pid, "No name")
            print(f"  - {pid}: {name}")
    else:
        print(f"\n✗ {message}")
        print("\nTroubleshooting:")
        print("1. Make sure the image contains a clear face")
        print("2. Face should be front-facing")
        print("3. Good lighting")
        print("4. Not too blurry")

if __name__ == "__main__":
    main()
