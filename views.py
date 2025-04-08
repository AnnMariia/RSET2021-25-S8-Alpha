from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.utils import timezone
import pytz
# import cv2
import nltk
nltk.download('maxent_ne_chunker')
nltk.download('words')
import dlib
from django.http import HttpRequest, JsonResponse, HttpResponse
from adhdApp.app.mcq_generation import MCQGenerator
from django.db.models import Max
from .models import *
from .monitor import *
import json
from gtts import gTTS
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import random
import json

# from PhythonAvatarGenerator import AvatarMaker as avatar_maker, AvatarInfo
# import PhythonAvatarGenerator as avatar_gen
# import cairosvg


# class QuestionGenerator:
#     def __init__(self, model_name='t5-base'):
#         self.model = T5ForConditionalGeneration.from_pretrained(model_name)
#         self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        
#     def generate_question(self, subject, difficulty='medium'):
#         """
#         Generate a question based on subject and difficulty
#         """
#         # Prompt templates for different subjects
#         prompts = {
#             'maths': [
#                 f"Generate a {difficulty} difficulty math problem about number system",
#                 f"Create a {difficulty} addition problem",
#                 f"Generate a {difficulty} multiplication question"
#             ],
#             'english': [
#                 f"Create a {difficulty} English grammar question",
#                 f"Generate a {difficulty} vocabulary question",
#                 f"Create a {difficulty} word usage problem"
#             ],
#             'cognitive': [
#                 f"Generate a {difficulty} logical reasoning question",
#                 f"Create a {difficulty} pattern recognition problem",
#                 f"Generate a {difficulty} spatial reasoning challenge"
#             ]
#         }
        
#         # Randomly select a prompt
#         prompt = random.choice(prompts.get(subject, prompts['maths']))
        
#         # Prepare input
#         input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        
#         # Generate question
#         output = self.model.generate(
#             input_ids, 
#             max_length=128, 
#             num_return_sequences=1, 
#             temperature=0.7
#         )
        
#         # Decode the generated question
#         question_text = self.tokenizer.decode(output[0], skip_special_tokens=True)
        
#         # Generate multiple choice options
#         options = self._generate_options(question_text)
        
#         return {
#             'question': question_text,
#             'options': options,
#             'subject': subject
#         }
    
#     def _generate_options(self, question):
#         """
#         Generate multiple choice options
#         """
#         # This is a simplified method. In a real scenario, 
#         # you'd use more sophisticated option generation
#         correct_option = question.split()[0]  # Simple placeholder
#         options = [
#             {'text': correct_option, 'isCorrect': True},
#             {'text': 'Option A', 'isCorrect': False},
#             {'text': 'Option B', 'isCorrect': False}
#         ]
#         random.shuffle(options)
#         return options

# # Example usage
# generator = QuestionGenerator()

# def generate_quiz_questions(num_questions=10):
#     subjects = ['maths', 'english']
#     questions = []
    
#     for _ in range(num_questions):
#         subject = random.choice(subjects)
#         question = generator.generate_question(subject)
#         questions.append(question)
    
#     return questions



@never_cache
def login_page(request):
    return render(request,'login.html')

@never_cache
def register_page(request):
    return render(request,'signup.html')

@never_cache
def index(request):
    return render(request,'index.html')

@never_cache
def home_page(request):
    if 'mail' in request.session:
        story_obj=Story.objects.all()
        context={
            'stories':story_obj
        }
        return render(request,'home.html',context)
    else:
        return render(request,'index.html')

@never_cache
@csrf_exempt
def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Users.objects.filter(email=email).first()
        if user and user.password==password:
            # Set session for the user
            request.session['mail'] = user.email  
            print("sucess-->")  

        if user is not None:
            # start_attention_monitoring(request) 
            return JsonResponse({'status': 'success', 'message': 'Login successful!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid credentials!'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method!'})

@never_cache
@csrf_exempt
def register(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            password = request.POST.get('password')
            profile_image = request.POST.get('profile_image')  # Get the selected image

            # Save user to the database
            user = Users(email=email, contact=contact, password=password, profile_image=profile_image)
            user.save()

            # Return success response
            return JsonResponse({'message': 'User registered successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)


@never_cache
def logout(request):
    if 'mail'in request.session:
        # attention_scores = request.session.get('attention_scores', {})

        # for student_id, data in attention_scores.items():
        #     scores = data["Attention_Scores"]
        #     average_score = sum(scores) / len(scores) if scores else 0

        #     # Save the attention scores to the database
        #     user = User.objects.get(username=student_id)
        #     for score in scores:
        #         AttentionScore.objects.create(user=user, score=score)
            
        #     Attendance.objects.create(user=user, attention_score=average_score)

       
        # del request.session['attention_scores']


        del request.session['mail']
        return render(request,'index.html')
    
@never_cache
def story_page(request):
    return render(request,'story.html')


@never_cache
def profile(request):
    if 'mail' in request.session:
        email = request.session['mail']
        user = Users.objects.get(email=email)
        
        
        if request.method == 'POST':
            user.email = request.POST.get('email')
            user.contact = request.POST.get('contact')
            
            
            if request.FILES.get('profile_image'):
                user.profile_image = request.FILES.get('profile_image')
            else:
                # If the user selected an image from the options
                selected_image = request.POST.get('profile_image')
                if selected_image:
                    user.profile_image = f'users/{selected_image}' 
            
            user.save()
            request.session['mail']=user.email
            return render(request,'profile.html')  
        
        return render(request, 'profile.html', {'user': user})





def get_story(request):
    story_id = request.GET.get('story_id')
    story = Story.objects.get(story_id=story_id)
    response_data = {
        'title': story.title,
        'text': story.text
    }
    return JsonResponse(response_data)



def format_timedelta(td):
    total_seconds = int(td.total_seconds())  # Get total seconds from timedelta
    minutes, seconds = divmod(total_seconds, 60)  # Convert seconds into minutes and seconds
    hours, minutes = divmod(minutes, 60)  # Convert minutes into hours and remaining minutes

    return f"{hours:02}:{minutes:02}:{seconds:02}" 



@never_cache
def dashboard_page(request):
    if 'mail' in request.session:
        mail = request.session['mail']
        usr_obj = Users.objects.get(email=mail)
        today = timezone.now().date()

        # Fetch all PageVisit records for the user on today's date
        get_time_objs = PageVisit.objects.filter(user=usr_obj, visit_date=today)
        
        today_total_time = timedelta(0)  # Initialize total time as timedelta object
        total_visits = get_time_objs.count()  # Get the number of visits for today

        for visit in get_time_objs:
            today_total_time += visit.total_time_spent  # Sum up all total_time_spent values

        # Calculate the average time spent in minutes
        if total_visits > 0:
            avg_time_in_seconds = today_total_time.total_seconds() / total_visits
            avg_time_in_minutes = round(avg_time_in_seconds / 60)  # Convert seconds to minutes and round
        else:
            avg_time_in_minutes = 0  # No visits, set average time to 0

        avg_time_in_minutes = f"{avg_time_in_minutes:02d}"  # Ensure two-digit format

        # Format the total time as a string (for display)
        total_time_str = format_timedelta(today_total_time)

        # Fetch the latest Mathematics and English scores
        latest_math_score = Score.objects.filter(username=mail, subject="english").order_by('-test_date').first()
        latest_english_score = Score.objects.filter(username=mail, subject="maths").order_by('-test_date').first()

        # Extract scores or set to "N/A" if not available
        math_score = latest_math_score.score if latest_math_score else "N/A"
        english_score = latest_english_score.score if latest_english_score else "N/A"

        context = {
            'total_time': total_time_str,  
            'avg_time': avg_time_in_minutes,  
            'math_score': math_score,
            'english_score': english_score,
        }

        return render(request, 'dashboard.html', context)
    

    


@never_cache
def learn_page(request):
    if 'mail' in request.session:
        mail = request.session['mail']
        usr_obj = Users.objects.get(email=mail)
        print(usr_obj)
        today = timezone.now().date()
        print(type(today))
    
    visit, created = PageVisit.objects.get_or_create(user=usr_obj, visit_date=today)
    if created:
        india_timezone = pytz.timezone('Asia/Kolkata')
        visit.start_time = timezone.now().astimezone(india_timezone)
        visit.save()

    if request.GET.get('action') == 'exit':
        india_timezone = pytz.timezone('Asia/Kolkata')
        visit.end_time = timezone.now().astimezone(india_timezone)
        time_spent = visit.end_time - visit.start_time
        visit.total_time_spent += time_spent
        visit.save()

    return render(request,'learn.html')


@never_cache
def exercise_page(request):
  
    return render(request, 'ex.html')

@never_cache
def avatar_page(request):
    return render(request,'avatar.html')

@never_cache
@csrf_exempt
def upload_story(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        text = request.POST.get('text')
        image = request.FILES.get('image')

        # Save the story to the database
        story = Story.objects.create(
            title=title,
            description=description,
            text=text,
            image=image
        )

        # Return the new story data
        return JsonResponse({
            "story": {
                "success":'done',
            }
        })
    return JsonResponse({"error": "Invalid request method."}, status=400)

@never_cache
@csrf_exempt
def generate_audio(request):
    if request.method == 'POST':
        print('in')
        content = request.POST.get('text')
        print('content->', content)
        
        if not content:
            return JsonResponse({'error': 'No text provided'}, status=400)

        tts = gTTS(text=content, lang='en', slow=False)
        audio_path = 'adhdApp/static/audio/story.mp3'  # File save path
        tts.save(audio_path)
        print('saved audio')

        # Correct URL for frontend
        audio_url = '/static/audio/story.mp3'  
        
        return JsonResponse({'message': 'success', 'audio_url': audio_url})
        


@never_cache
def math_page(request):
    if 'mail' in request.session:
        return render(request,'math.html')
    

@never_cache
def english_page(request):
    if 'mail' in request.session:
        return render(request,'english.html')
    

@never_cache
def cognitive_page(request):
    if 'mail' in request.session:
        return render(request,'cognitive.html')
    

@never_cache
def mathtest_page(request):
    if 'mail' in request.session:
        return render(request,'mathtest.html')
    

@never_cache
def englishtest_page(request):
    if 'mail' in request.session:
        return render(request,'englishtest.html')
    

@never_cache
def cognitivetest_page(request):
    if 'mail' in request.session:
        return render(request,'cognitivetest.html')
    
   



##################################################################

from django.shortcuts import render
from django.http import JsonResponse
import random


def qg(request):
    mcqs = []  
    latest_quiz_number = 1  

    if request.method == "POST":
        paragraphs = request.POST.get("englishContext", "")
        num_questions = int(request.POST.get("numQuestions", 1))

        print(paragraphs)
        print(num_questions)

      
        last_mcq = MCQ.objects.order_by("-quiz_number").first() 
        if last_mcq:
            latest_quiz_number = last_mcq.quiz_number + 1  

      
        mcq_generator = MCQGenerator()

        # Generate MCQs
        mcqs = mcq_generator.generate_mcq_questions(paragraphs, num_questions)[:num_questions]

        # Save MCQs with the new quiz number
        for q in mcqs:
            MCQ.objects.create(
                subject="English",
                question=q.questionText,
                correct_answer=q.answerText,
                distractors=q.distractors,
                quiz_number=latest_quiz_number  
            )


    latest_mcqs = MCQ.objects.filter(quiz_number=latest_quiz_number)

    return render(request, "ex.html", {"mcqs": latest_mcqs})


import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MathQuestion
import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MathQuestion


@csrf_exempt
def generate_mcq(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            hero_name = data["hero_name"]
            wizard_name = data["wizard_name"]
            adventure_theme = data["adventure_theme"]

            # Fetch latest quiz number and increment it
            latest_quiz = MathQuestion.objects.order_by("-quiz_number").first()
            quiz_number = latest_quiz.quiz_number + 1 if latest_quiz else 1

            # Generate a short story based on input
            story = f"""
            🌟 In the land of {adventure_theme}, the brave hero {hero_name} embarked on a daring quest. 
            Guided by the wise wizard {wizard_name}, they ventured into the enchanted lands, where 
            ancient scrolls of mathematical wisdom awaited. But before {hero_name} could claim the treasure, 
            they had to face a series of mystical challenges...
            """

            mcqs = []

            # Mix 1: Addition-Based Questions (🔥 The Forest of Addition)
            print("\n🔥 The journey begins in the **Forest of Addition**.")
            def mix1():
                for _ in range(3):
                    a = random.randint(1, 20)
                    b = random.randint(1, 20)
                    correct_answer = a + b
                    options = [correct_answer, correct_answer + 2, correct_answer - 2, correct_answer + 5]
                    random.shuffle(options)

                    question_text = f"{hero_name}, what is {a} + {b}?"

                    mcq = MathQuestion.objects.create(
                        hero_name=hero_name,
                        wizard_name=wizard_name,
                        adventure_theme=adventure_theme,
                        story=story,
                        quiz_number=quiz_number,
                        question=question_text,
                        option_a=options[0],
                        option_b=options[1],
                        option_c=options[2],
                        option_d=options[3],
                        correct_answer=str(correct_answer)
                    )
                    mcqs.append(mcq)

            # Mix 2: Subtraction-Based Questions (🌲 The Valley of Subtraction)
            print("\n🌲 The next trial awaits in the **Valley of Subtraction**.")
            def mix2():
                for _ in range(3):
                    a = random.randint(10, 30)
                    b = random.randint(1, 10)
                    correct_answer = a - b
                    options = [correct_answer, correct_answer + 3, correct_answer - 1, correct_answer + 4]
                    random.shuffle(options)

                    question_text = f"{hero_name}, what is {a} - {b}?"

                    mcq = MathQuestion.objects.create(
                        hero_name=hero_name,
                        wizard_name=wizard_name,
                        adventure_theme=adventure_theme,
                        story=story,
                        quiz_number=quiz_number,
                        question=question_text,
                        option_a=options[0],
                        option_b=options[1],
                        option_c=options[2],
                        option_d=options[3],
                        correct_answer=str(correct_answer)
                    )
                    mcqs.append(mcq)

            # Mix 3: Multiplication-Based Questions (🗻 The Mountain of Multiplication)
            print("\n🗻 Scaling the great **Mountain of Multiplication**.")
            def mix3():
                for _ in range(3):
                    a = random.randint(1, 10)
                    b = random.randint(1, 10)
                    correct_answer = a * b
                    options = [correct_answer, correct_answer + 2, correct_answer - 2, correct_answer + 4]
                    random.shuffle(options)

                    question_text = f"{hero_name}, what is {a} × {b}?"

                    mcq = MathQuestion.objects.create(
                        hero_name=hero_name,
                        wizard_name=wizard_name,
                        adventure_theme=adventure_theme,
                        story=story,
                        quiz_number=quiz_number,
                        question=question_text,
                        option_a=options[0],
                        option_b=options[1],
                        option_c=options[2],
                        option_d=options[3],
                        correct_answer=str(correct_answer)
                    )
                    mcqs.append(mcq)

            # Mix 4: Division-Based Questions (💦 The River of Division)
            print("\n💦 The final challenge awaits in the **River of Division**.")
            def mix4():
                for _ in range(3):
                    b = random.randint(1, 5)
                    correct_answer = random.randint(2, 10)
                    a = correct_answer * b
                    options = [correct_answer, correct_answer + 1, correct_answer - 1, correct_answer + 3]
                    random.shuffle(options)

                    question_text = f"{hero_name}, what is {a} ÷ {b}?"

                    mcq = MathQuestion.objects.create(
                        hero_name=hero_name,
                        wizard_name=wizard_name,
                        adventure_theme=adventure_theme,
                        story=story,
                        quiz_number=quiz_number,
                        question=question_text,
                        option_a=options[0],
                        option_b=options[1],
                        option_c=options[2],
                        option_d=options[3],
                        correct_answer=str(correct_answer)
                    )
                    mcqs.append(mcq)

            # Generate all question sets
            mix1()
            mix2()
            mix3()
            mix4()

            # Prepare response data
            response_data = {
            "message": "MCQs generated successfully!",
            "quiz_number": quiz_number,
            "story": story,
            "stages": [
                {"title": "🔥 The journey begins in the **Forest of Addition**."},
                {"title": "🌲 The next trial awaits in the **Valley of Subtraction**."},
                {"title": "🗻 Scaling the great **Mountain of Multiplication**."},
                {"title": "💦 The final challenge awaits in the **River of Division**."}
            ],
            "questions": [
                {
                    "question": q.question,
                    "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                    "correct_answer": q.correct_answer  
                }
                for q in mcqs
            ]
        }



            return JsonResponse(response_data, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def get_latest_quiz(request):
    subject = request.GET.get("subject")

    if subject == "maths":
        latest_quiz_number = MathQuestion.objects.aggregate(Max("quiz_number"))["quiz_number__max"]
        if latest_quiz_number is None:
            return JsonResponse({"error": "No quiz found"}, status=404)

        latest_questions = MathQuestion.objects.filter(quiz_number=latest_quiz_number).order_by("id")

        quiz_data = {
            "stages": [
                {"title": "🔥 The journey begins in the <strong>Forest of Addition</strong>."},
                {"title": "🌲 The next trial awaits in the <strong>Valley of Subtraction</strong>."},
                {"title": "🗻 Scaling the great <strong>Mountain of Multiplication</strong>."},
                {"title": "💦 The final challenge awaits in the <strong>River of Division</strong>."}
            ],
            "questions": [
                {
                    "question": q.question,
                    "options": [q.option_a, q.option_b, q.option_c, q.option_d],
                    "correct_answer": q.correct_answer,
                }
                for q in latest_questions
            ]
        }

    elif subject == "english":
        latest_quiz_number = MCQ.objects.aggregate(Max("quiz_number"))["quiz_number__max"]
        if latest_quiz_number is None:
            return JsonResponse({"error": "No quiz found"}, status=404)

        latest_questions = MCQ.objects.filter(quiz_number=latest_quiz_number).order_by("id")

        quiz_data = {
            "questions": [
                {
                    "question": q.question,
                    "options": [q.correct_answer] + q.distractors,
                    "correct_answer": q.correct_answer,
                }
                for q in latest_questions
            ]
        }

    else:
        return JsonResponse({"error": "Invalid subject"}, status=400)

    return JsonResponse(quiz_data)



@csrf_exempt
def submit_english_quiz(request):
    if request.method == "POST":
      
            # Extract form data instead of JSON
            answers = {key: value for key, value in request.POST.items()}
            print(answers)
            username = request.session.get("mail", "Anonymous")

            if not answers:
                return JsonResponse({"error": "No answers provided"}, status=400)

            # Get latest quiz
            latest_quiz_number = MCQ.objects.latest('quiz_number').quiz_number
            questions = MCQ.objects.filter(quiz_number=latest_quiz_number)

            # Calculate score
            score = sum(1 for question in questions if answers.get(f"q{question.id}", "").strip().lower() == question.correct_answer.strip().lower())
            print(score)

            # Save score
            Score.objects.create(username=username, subject="English", score=score)

            return JsonResponse({"message": f"English Quiz Submitted! Your score: {score}"})


    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
def submit_maths_quiz(request):
    if request.method == "POST":
        print("🔍 Raw request body:", request.body)
        data = json.loads(request.body.decode('utf-8') or "{}")
        username = data.get("username", "Anonymous")
        answers = data.get("answers", {})

        # Fetch the latest Maths quiz (latest quiz_number)
        latest_quiz_number = MathQuestion.objects.latest('quiz_number').quiz_number
        questions = MathQuestion.objects.filter(quiz_number=latest_quiz_number)

        score = 0
        for question in questions:
            user_answer = answers.get(str(question.id), "").strip().lower()
            correct_answer = question.correct_answer.strip().lower()

            if user_answer == correct_answer:
                score += 1  # Increase score for each correct answer

        # Save the score in the database
        Score.objects.create(username=username, subject="Maths", score=score)

        return JsonResponse({"message": f"Maths Quiz Submitted! Your score: {score}"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)




import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Score, MCQ, MathQuestion
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Score, MCQ, MathQuestion, Users  # Import Users model
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Score, MCQ, MathQuestion, Users  # Import Users model
@csrf_exempt
def submit_quiz(request):
    if request.method == "POST":
        print("Raw POST Data:", request.POST)  # Debugging output

        answers_json = request.POST.get("answers", "{}")
        print("Received Answers JSON:", answers_json)  # Debugging output

        try:
            data = json.loads(answers_json)  # Deserialize JSON
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid answers format"}, status=400)

        print("Parsed Answers Dictionary:", data)  # Debugging output

        subject = request.POST.get("subject")
        print("Subject:", subject)  # Debugging output

        email = request.session.get("mail")
        print("User Email:", email)  # Debugging output

        if not email:
            return JsonResponse({"error": "User not logged in"}, status=403)

        user = Users.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        score = 0  # Initialize score

        # Fetch latest quiz number dynamically
        if subject == "english":
            latest_quiz_number = MCQ.objects.latest("quiz_number").quiz_number
            questions = MCQ.objects.filter(quiz_number=latest_quiz_number)
            correct_answers = {f"q{index}": q.correct_answer for index, q in enumerate(questions)}

        elif subject == "maths":
            latest_quiz_number = MathQuestion.objects.latest("quiz_number").quiz_number
            questions = MathQuestion.objects.filter(quiz_number=latest_quiz_number)
            correct_answers = {f"q{index}": q.correct_answer for index, q in enumerate(questions)}
        else:
            return JsonResponse({"error": "Invalid subject"}, status=400)

        # Check answers
        for q_id, selected_ans in data.items():
            if correct_answers.get(q_id) == selected_ans:
                score += 1  # Increment score for correct answers

        # Save score in database
        Score.objects.create(username=email, subject=subject, score=score)

        return JsonResponse({"message": "Quiz submitted successfully!", "score": score})

    return JsonResponse({"error": "Invalid request"}, status=400)



def get_user_scores(request):
    email = request.session.get('email') 
    print("-->>",email) 
    scores = Score.objects.filter(username=email)  

    score_data = []
    for score in scores:
        score_data.append({
            "subject": score.subject,
            "score": score.score,
            "test_date": score.test_date.strftime("%Y-%m-%d"),
        })
    print("-->",score_data)
    return JsonResponse({"scores": score_data})

