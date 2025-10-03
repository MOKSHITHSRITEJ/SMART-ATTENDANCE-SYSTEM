import csv
import os
from datetime import datetime
import qrcode
import cv2   # OpenCV for live QR scanning
import pyttsx3 as pt
import speech_recognition as sr

# File paths
STUDENTS_FILE = "students.csv"
ATTENDANCE_FILE = "attendance.csv"


# --- Initialize CSV files if they don't exist ---
def init_files():
    if not os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["URN", "Name", "Photo"])   # Added photo column

    if not os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "URN", "Name", "Status", "Timestamp"])


# --- Save attendance record ---
def save_attendance(urn, status="Present"):
    with open(STUDENTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        student = next((row for row in reader if row["URN"] == urn), None)

    if not student:
        print("⚠️ Student not found.")
        return

    date_str = datetime.now().date().isoformat()
    timestamp = datetime.now().isoformat(timespec="seconds")

    record = [date_str, urn, student["Name"], status, timestamp]
    with open(ATTENDANCE_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(record)

    print(f"✅ Attendance marked for {student['Name']} ({urn})")


# --- Add a new student ---
def add_student():
    urn = input("Enter URN: ").strip()
    name = input("Enter Name: ").strip()
    photo = input("Enter path to student photo (e.g., C:/photos/student1.jpg): ").strip()

    with open(STUDENTS_FILE, newline="") as f:
        reader = csv.DictReader(f)
        if any(row["URN"] == urn for row in reader):
            print("⚠️ A student with that URN already exists.")
            return

    with open(STUDENTS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([urn, name, photo])

    print(f"✅ Added student: {name} ({urn}) with photo {photo}")


# --- Mark attendance manually ---
def mark_attendance_manual():
    with open(STUDENTS_FILE, newline="") as f:
        students = list(csv.DictReader(f))

    if not students:
        print("⚠️ No students found. Add students first.")
        return

    date_str = datetime.now().date().isoformat()
    print(f"\nMarking attendance for {date_str}")
    print("Enter: p = present, a = absent, s = skip\n")

    records_to_save = []
    for s in students:
        while True:
            ans = input(f"{s['URN']} - {s['Name']}: ").strip().lower()
            if ans in ("p", "a", "s"):
                break
            print("Invalid input. Use 'p', 'a', or 's'.")
        if ans == "s":
            continue

        status = "Present" if ans == "p" else "Absent"
        timestamp = datetime.now().isoformat(timespec="seconds")
        records_to_save.append([date_str, s["URN"], s["Name"], status, timestamp])

    if records_to_save:
        with open(ATTENDANCE_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(records_to_save)
        print(f"✅ Saved {len(records_to_save)} records.")
    else:
        print("No attendance was marked.")


# --- View attendance ---
def view_attendance():
    date = input("Enter date (YYYY-MM-DD) or leave blank for today: ").strip()
    if not date:
        date = datetime.now().date().isoformat()

    found = False
    with open(ATTENDANCE_FILE, newline="") as f:
        for row in csv.DictReader(f):
            if row["Date"] == date:
                if not found:
                    print(f"\nAttendance for {date}:")
                    print(f"{'URN':15} {'Name':25} {'Status':10} {'Timestamp'}")
                    found = True
                print(f"{row['URN']:15} {row['Name']:25} {row['Status']:10} {row['Timestamp']}")

    if not found:
        print(f"⚠️ No attendance records found for {date}.")


# --- Generate QR code for student ---
def generate_qr():
    urn = input("Enter URN of student: ").strip()
    filename = f"QR_{urn}.png"
    qrcode.make(urn).save(filename)
    print(f"✅ QR code saved as {filename}")


# --- Live QR code scanner ---
def mark_attendance_qr():
    print("📷 Starting live QR scanner. Press 'q' to quit.")
    cap = cv2.VideoCapture(0)
    detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            urn = data.strip()
            with open(STUDENTS_FILE, newline="") as f:
                student = next((row for row in csv.DictReader(f) if row["URN"] == urn), None)

            if student:
                save_attendance(urn, "Present")
                print(f"🎉 Scanned: {student['Name']} ({urn})")
                # Show student photo
                if student["Photo"] and os.path.exists(student["Photo"]):
                    img = cv2.imread(student["Photo"])
                    if img is not None:
                        cv2.imshow(f"{student['Name']} - {urn}", img)
                    else:
                        print("⚠️ Could not load photo.")
                else:
                    print("⚠️ Photo not found.")
        cv2.imshow("QR Scanner - Press 'q' to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
# --- Main menu ---
def main():
    init_files()
    while True:
        print("\n=== Attendance System ===")
        print("1. Add student")
        print("2. Mark attendance (manual)")
        print("3. View attendance")
        print("4. Show file locations")
        print("5. Generate QR code")
        print("6. Mark attendance via QR code (Camera)")
        print("7. Exit")
        choice = input("Choose (1-7): ").strip()
        if choice == "1":
            add_student()
        elif choice == "2":
            mark_attendance_manual()
        elif choice == "3":
            view_attendance()
        elif choice == "4":
            print(f"📂 Students: {STUDENTS_FILE}")
            print(f"📂 Attendance: {ATTENDANCE_FILE}")
        elif choice == "5":
            generate_qr()
        elif choice == "6":
            mark_attendance_qr()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Try again.")
if __name__ == "__main__":
    main()