import cv2
import dlib
import numpy as np
from datetime import datetime
from django.contrib.auth.models import User
from .models import Attendance, AttentionScore

face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(r"adhdApp/shape_predictor_68_face_landmarks.dat")


def compute_attention(landmarks):
    nose_position = landmarks[30]
    chin_position = landmarks[8]
    attention_score = 1 if abs(nose_position[0] - chin_position[0]) < 10 else 0
    return attention_score

def identify_student(frame):
    # You can use the authenticated user's information here.
    return "Student_ID"  # Replace with actual logic to identify user.

# def start_attention_monitoring(request):
#     user = request.user  # Get the logged-in user
#     attendance_records = {}

#     video_stream = cv2.VideoCapture(0)

#     while True:
#         ret, frame = video_stream.read()
#         grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         detected_faces = face_detector(grayscale_frame)

#         for face in detected_faces:
#             facial_landmarks = landmark_predictor(grayscale_frame, face)
#             landmark_positions = [(point.x, point.y) for point in facial_landmarks.parts()]

#             student_id = identify_student(frame)
#             if student_id not in attendance_records:
#                 attendance_records[student_id] = {
#                     "Attendance": "Present",
#                     "Attention_Scores": []
#                 }

#             attention_score = compute_attention(landmark_positions)
#             attendance_records[student_id]["Attention_Scores"].append(attention_score)

#             cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
#             cv2.putText(frame, f"{student_id}: Attention Score: {attention_score}",
#                         (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

#         cv2.imshow('Video', frame)

#         # Exit loop when 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     video_stream.release()
#     cv2.destroyAllWindows()

#     # Storing attention scores in the database
#     for student_id in attendance_records:
#         scores = attendance_records[student_id]["Attention_Scores"]
#         average_score = sum(scores) / len(scores) if scores else 0
#         attendance_records[student_id]["Final_Attention_Score"] = average_score

#         # Save data in the database (Attendance and AttentionScore)
#         user = User.objects.get(username=student_id)  # Replace with actual user identification
#         for score in scores:
#             attention_score = AttentionScore.objects.create(user=user, score=score)
#             attention_score.save()

#         # You can also store an average attention score in the Attendance model
#         attendance = Attendance.objects.create(user=user, att_score=average_score)
#         attendance.save()

#     print("Attendance and attention scores stored in the database.")
