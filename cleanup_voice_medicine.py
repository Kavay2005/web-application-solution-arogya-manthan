import os
import shutil

files_to_delete = [
    'voice_processor.py',
    'diagnose_medicine.py',
    'test_medicine_response.py',
    'components/VoiceChat.tsx',
    'components/VoiceInput.tsx',
    'styles/VoiceChat.css',
    'components/MedicineAvailability.tsx',
    'components/MedicineFinder.tsx',
    'components/MedicineMetricsDisplay.tsx',
    'styles/MedicineAvailability.css',
    'src/medicine'
]

for file_path in files_to_delete:
    full_path = os.path.join(r"c:\Users\kavay\OneDrive\Desktop\APP\final_health", file_path)
    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            print(f"✓ Deleted directory: {file_path}")
        elif os.path.isfile(full_path):
            os.remove(full_path)
            print(f"✓ Deleted file: {file_path}")
        else:
            print(f"✗ Not found: {file_path}")
    except Exception as e:
        print(f"✗ Error deleting {file_path}: {e}")

print("\nCleanup complete!")
