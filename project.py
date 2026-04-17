import streamlit as st
from collections import deque

# بيانات المريض
class Patient:
    def __init__(self, name, booking_time, condition, duration, age, referral):
        self.name = name
        self.booking_time = float(booking_time)
        self.condition = condition.lower()
        self.duration = int(duration)
        self.age = int(age)
        self.referral = referral
        self.assigned = False
        self.assignment = ""

class Doctor:
    def __init__(self, name):
        self.name = name
        self.schedule = []

class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.schedule = []

# التحقق من التعارض
def no_conflict(schedule, start, end):
    for s, e in schedule:
        if not (end <= s or start >= e):
            return False
    return True

# أفضل وقت متاح
def best_fit_slot(schedule, duration):
    time = 8.0
    while time <= 16:
        if no_conflict(schedule, time, time + duration / 60):
            return time
        time += 0.25
    return None

# تخصيص المريض
def assign_patient(patient, doctors, rooms):
    for doc in doctors:
        for room in rooms:
            start_time = best_fit_slot(doc.schedule, patient.duration)
            if start_time is not None and no_conflict(room.schedule, start_time, start_time + patient.duration / 60):
                doc.schedule.append((start_time, start_time + patient.duration / 60))
                room.schedule.append((start_time, start_time + patient.duration / 60))
                patient.assigned = True
                patient.assignment = f"🧑‍⚕️ {doc.name} | 🏥 {room.room_id} | ⏰ {start_time:.2f} - {start_time + patient.duration / 60:.2f}"
                return
    patient.assignment = "❌ لا يوجد وقت متاح"

# جدولة المرضى
def schedule_patients(patients, doctors, rooms):
    emergency = [p for p in patients if p.condition == 'emergency']
    normal = [p for p in patients if p.condition == 'normal']
    
    emergency.sort(key=lambda p: (0 if p.referral else 1, p.duration))
    normal_queue = deque(sorted(normal, key=lambda p: p.booking_time))
    
    for p in emergency:
        assign_patient(p, doctors, rooms)
    for p in normal_queue:
        assign_patient(p, doctors, rooms)

# واجهة Streamlit
st.title("🏥 نظام الحجز الذكي للعيادة")

st.sidebar.header("👤 إدخال بيانات المرضى")
patients_data = []

num_patients = st.sidebar.number_input("🔢 عدد المرضى", min_value=1, max_value=20, step=1)

for i in range(num_patients):
    with st.sidebar.expander(f"المريض رقم {i+1}"):
        name = st.text_input(f"👤 الاسم", key=f"name_{i}")
        booking_time = st.number_input(f"🕒 وقت الحجز (مثلاً 9.5 يعني 9:30)", key=f"time_{i}", min_value=0.0, max_value=24.0, step=0.25)
        condition = st.selectbox(f"🚨 نوع الحالة", ["normal", "emergency"], key=f"cond_{i}")
        duration = st.number_input(f"⏱️ مدة الفحص (دقائق)", key=f"dur_{i}", min_value=5, max_value=60, step=5)
        age = st.number_input(f"🎂 عمر المريض", key=f"age_{i}", min_value=0, max_value=120)
        referral = st.checkbox(f"🏥 إحالة من مستشفى؟", key=f"ref_{i}")
        if name:
            patients_data.append(Patient(name, booking_time, condition, duration, age, referral))

if st.button("📅 جدولة المرضى"):
    doctors = [Doctor("Dr. A"), Doctor("Dr. B")]
    rooms = [Room("Room 1"), Room("Room 2")]
    schedule_patients(patients_data, doctors, rooms)

    st.subheader("📋 جدول المواعيد النهائي")
    for p in patients_data:
        st.markdown(f"**{p.name}** ({'🚨 طارئة' if p.condition == 'emergency' else '🕓 عادية'}) → {p.assignment}")