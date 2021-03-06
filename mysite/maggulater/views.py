import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse , HttpResponseRedirect
import json
# import simplejson
from django.core.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from models import *
from django.core.urlresolvers import reverse
from django.core import serializers
from django.http import JsonResponse
from django.contrib.auth import authenticate
from datetime import date
import calendar
from .email import sendEmail
# from jsonify.decorators import ajax_request
# try:
# from django.utils import simplejson
# except:
#     import simplejson as json

ADMIN = 0
STUDENT = 1
FACULTY = 2

# Create your views here.

def home(request):
	print "Here in home "
	# request.session['id'] = 19
	if 'id' in request.session.keys():
		print "user_id" , request.session['id']
		user = MyUser.objects.get(user_id = request.session['id'])
		if user.type_flag == ADMIN:
			print "ADMIN"
			adm = authenticate(username=user.name,password = user.password)
			return redirect('/admin/')
			# response = {'status': 1, 'message': "Confirmed!!", 'url':'/admin/'}
			# return HttpResponse(json.dumps(response), content_type='application/json')

		if user.type_flag == STUDENT:
			print "STUDENT"
			return render(request, "gentelella/studenthome.html")
		if user.type_flag == FACULTY:
			print "FACULTY"
			return render(request, "gentelella/facultyhome.html")
	else :
		return redirect('/login/')
	# return render(request, "gentelella/studenthome.html")

# def adminhome(request):
# 	response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
# 	return HttpResponse(json.dumps(response), content_type='application/json')

def userdetails(request):
	user = MyUser.objects.get(user_id = request.session['id'])
	return JsonResponse(user.serialize(),safe = False)

def coursehome(request, course_id):
	request.session['course_id'] = course_id
	print "course_id = " + request.session['course_id']
	return render(request, "gentelella/courseHome.html")


def lecturehome(request, lecture_id):
	request.session['lecture_id'] = lecture_id
	return render(request, "gentelella/lecture.html")

def lecturecontent(request):
	lec = Lecture.objects.get(Lecture_Id = request.session['lecture_id'])
	test = Test.objects.get(Lecture_Id = request.session['lecture_id'])
	resp = [lec.serialize(), test.serialize()]
	return JsonResponse(resp, safe = False)

def submitperformance(request):
	json_data = request.body
	performance = Performance_Sheet(Student_Id = request.session['id'], Test_Id = json_data['test_id'], Marks_Obtained = json_data['marks_ob'], Marks_Total = json_data['marks_tot'])
	performance.save()
	response = {'status' : 'ok'}
	return HttpResponse(json.dumps(response), content_type='application/json')



def generalmail(request):
	return render(request, "gentelella/generalmail.html")

@ensure_csrf_cookie
def login(request):
	print "Here in Login!!!"
	if request.method == 'POST':
		print "yaha aaya !! "
		json_data = request.body
		# print request.body
		if not json_data:
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		json_data = json.loads(json_data)
		print json_data
		email_ = json_data['email']
		pwd = json_data['password']
		# print email_, pwd

		try:
			user = MyUser.objects.get(email = email_)
		except Exception, e:
			user = None

		print "IN LOGIN"
		# print user and user.check_password(pwd)
		# print make_password(pwd)
		if user and user.check_password(pwd):
			request.session['id'] = user.user_id
			# print request.session
			print "In profile redirect"
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/home/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			print "IN login wala !! "
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
			return HttpResponse(json.dumps(response), content_type='application/json')

	if request.method == 'GET':
		print "get h"
		return render(request,'maggulater/login.html')


def faculty(request):
	if 'id' in request.session.keys():
		print "faculty_id" , request.session['id']
	if request.method == 'GET':
		return render(request, 'gentelella/facultyhome.html')

def mailsend(request):
	print "reached API"
	print request.body

	if request.method == 'POST':
		json_data = request.body
		print json_data
		json_data = json.loads(json_data)
		recipients = [json_data['recipient']]
		subject = json_data['subject']
		body = json_data['body']
		user = MyUser.objects.get(user_id = request.session['id'])
		sender = user.email
		sendEmail(sender, recipients, subject, body)
		response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
		return HttpResponse(json.dumps(response), content_type='application/json')

	if request.method == 'GET':
		return render(request, 'maggulater/signup.html')


def signUp(request):
	if request.method == 'POST':
		json_data = request.body
		json_data = json.loads(json_data)
		name = json_data['name']
		email = json_data['email']
		link_to_dp = "link"
		type_flag = json_data['flag']
		dob = json_data['dob']
		password = json_data['password']
		user = MyUser(name = name, email = email, link_to_dp = link_to_dp , type_flag = type_flag , dob = dob)
		hashed_pass = user.make_password(password)
		print hashed_pass
		print type_flag
		user.set_password(hashed_pass)
		user.save()
		user = MyUser.objects.get(email = email)
		# duser = User.objects.create_user(name,email,password)
		if type_flag == FACULTY:
			newfac = Faculty(Faculty_Id = user)
			newfac.save()
		elif type_flag == ADMIN:
			newadm = Admin(Admin_Id = user)
			newadm.save()
		elif type_flag == STUDENT:
			print "student"
			print user.user_id
			newst = Student(Student_Id = user)
			newst.save()
		print "Created Users succesfully"
		response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
		return HttpResponse(json.dumps(response), content_type='application/json')

	if request.method == 'GET':
		return render(request, 'maggulater/signup.html')


def profile(request):
	return render(request , 'gentelella/profile.html')


def studenthome(request):
	print "student_id" , request.session['id']
	return render(request , 'gentelella/studenthome.html')


def adminhome(request):
	print "admin_id" , request.session['id']
	return render(request , 'maggulater/admin.html')

def index2(request):
	# print "admin_id" , request.session['id']
	return render(request , 'gentelella/index2.html')

def parentPortal(request):
	if request.method == 'POST' :
		json_data = request.body
		if not json_data :
			print ("Error !! No credentials Given !! ")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/parentPortal/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		json_data = json.loads(json_data)
		email = json_data['email']
		name = json_data['name']
		user = MyUser.objects.get(email = email)
		if user is None or user.name != name :
			print("Sorry Wrong Credentials !! ")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/parentPortal/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			# Performance = Performance_Sheet.objects.get(Student_Id = user)
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/studentallperformance/'}
			request.session['id'] = user.user_id
			request.session['parentPortal'] = 1
			print request.session

			return HttpResponse(json.dumps(response), content_type = 'application/json')
	if request.method == 'GET' :
		return render(request, 'maggulater/Parent_Portal.html')

def forgotPassword(request):
	if request.method == 'POST' :
		json_data = request.body
		if not json_data :
			print ("Error !! No credentials Given !! ")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/forgotPassword/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		json_data = json.loads(json_data)
		_email = json_data['email']
		name = json_data['name']
		user = MyUser.objects.get(email = _email)
		if user is None or user.name != name :
			print("Sorry Wrong Credentials !! ")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/forgotPassword/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			newpassword = json_data['password']
			hashed_pass = user.make_password(newpassword)
			user.set_password(hashed_pass)
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/login/'}
			print response
			# return HttpResponseRedirect(("/login/"))
			return HttpResponse(json.dumps(response), content_type ='application/json')
	if request.method == 'GET' :
		return render(request, 'maggulater/forgotPassword.html')


def logout(request):
	try:
		del request.session['id']
	except KeyError:
		pass
	print request.session
	return render(request,'maggulater/login.html')


def searchcourse(request):
	if request.method == 'POST':
		json_data = request.body
		json_data = json.loads(json_data)
		if not json_data:
			print("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/searchcourse/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		cid = json_data['course_id']

		course = Course.objects.get(course_id = cid)

		if course:
			request.session['course_id'] = cid
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/coursehome/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/searchcourse/'}
			return HttpResponse(json.dumps(response), content_type='application/json')

	if request.method == 'GET':
		return render(request , 'maggulater/student_home.html')

# API for enrolling a student in a course
def enroll(request):
	user = MyUser.objects.get(user_id = request.session['id'])
	student = Student.objects.get(Student_Id = user)
	print "Course_id = " + request.session['course_id']
	course = Course.objects.get(course_id = request.session['course_id'])
	newenroll = Enrolls(student_id = student, course_id = course)
	newenroll.save()
	response = {'status': 1, 'message': "Confirmed!!", 'url':'/coursehome/'}
	return HttpResponse(json.dumps(response), content_type='application/json')


# API to add a new notice
def addnotice(request):
	if request.method == 'POST':
		json_data = request.body
		json_data = json.loads(json_data)
		if not json_data:
			print("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/addnotice/'}
			return HttpResponse(json.dumps(response), content_type='application/json')

		cid = json_data['c_id']
		msg = json_data['message']

		newnotice = Notice(timestamp = now(), message = msg, c_id = cid)
		newnotice.save()
		response = {'status': 1, 'message': "Confirmed!!", 'url':'/coursehome/'}
		return HttpResponse(json.dumps(response), content_type='application/json')

	if request.method == "GET":
		return render(request, 'maggulater/addNotice.html')

# API to add a new course
def addcourse(request):
	if request.method == 'POST':
		json_data = request.body
		json_data = json.loads(json_data)
		if not json_data:
			print("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/searchcourse/'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		cid = json_data['c_id']
		cname = json_data['course_name']
		pre = json_data['prereq']
		fac_id = request.session['id']
		course = Course.objects.get(course_id = cid)

		if course:
			perror("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'/addcourse/'}
			return HttpResponse(json.dumps(response), content_type='application/json')

		newcourse = Course(course_id = cid,course_name = cname,prereq = pre,faculty = fac_id)
		newcourse.save()
		response = {'status': 1, 'message': "Confirmed!!", 'url':'/home/'}
		return HttpResponse(json.dumps(response), content_type='application/json')


	if request.method == 'GET':
		return render(request , 'maggulater/addCourse.html')


# API to approve a course
def approve(request):
	if request.method == 'POST':
		json_data = request.body
		json_data = json.loads(json_data)
		if not json_data:
			print("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'approve'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		cid = json_data['c_id']

		course = Course.objects.get(course_id = cid)

		if course:
			course.approve()
			response = {'status': 1, 'message': "Confirmed!!", 'url':'coursehome'}
			return HttpResponse(json.dumps(response), content_type='application/json')
		else:
			perror("error")
			response = {'status': 1, 'message': "Confirmed!!", 'url':'error'}
			return HttpResponse(json.dumps(response), content_type='application/json')


# API to get details of current course
def coursedetails(request):
	# print "Course id in detail api call = " + request.session['course_id']
	course = Course.objects.get(course_id = request.session['course_id'])
	# print course.serialize()
	js = course.serialize()
	try:
		prereq = Course.objects.get(course_id = course.prereq)
	except Exception, e:
		prereq = None

	if(prereq):
		js['prereq_name'] = prereq.course_name
	else:
		js['prereq_name'] = 'No Prerequisite'

	return JsonResponse(js, safe = False)


# API to get list of all courses
def allcourses(request):
	j = Course.objects.all()
	json = []
	for i in j:
		json.append(i.serialize())
	# print json
	return HttpResponse(json)

def getStudentLectures(request):
	j = Lecture.objects.all()
	# print request.session['id']
	u = MyUser.objects.all()
	# print u
	for user in u:
		if user.user_id == request.session['id']:
			break
	e = Enrolls.objects.all()
	# print e
	cids = []
	crs = []
	# print user
	for enr in e:
		if enr.student_id.Student_Id.user_id == user.user_id:
			cids.append(enr.course_id.course_id)
			crs.append(enr.course_id)

	kl = []
	for kx in j:
		# print kx
		if kx.Course_Id.course_id in cids:
			kl.append(kx)


	a = [k.serialize() for k in kl]
	# print a
	return HttpResponse(a)
	# print a

def getStudentNotices(request):
	j = Notice.objects.all()
	# print "papapa"
	# print j
	# print request.session['id']
	u = MyUser.objects.all()
	# print u
	for user in u:
		if user.user_id == request.session['id']:
			break
	e = Enrolls.objects.all()
	# print e
	cids = []
	crs = []
	# print user
	for enr in e:
		if enr.student_id.Student_Id.user_id == user.user_id:
			cids.append(enr.course_id.course_id)
			crs.append(enr.course_id)

	kl = []
	for kx in j:
		# print kx
		if kx.c_id.course_id in cids:
			kl.append(kx)


	a = [k.serialize() for k in kl]
	# print a
	return HttpResponse(a)


def getFacultyLectures(request):
	j = Lecture.objects.all()
	# print request.session['id']
	u = MyUser.objects.all()
	# print u
	for user in u:
		if user.user_id == request.session['id']:
			break
	c = Course.objects.all()
	# print e
	cids = []
	crs = []
	for cou in c:
		print cou.faculty.Faculty_Id.user_id
		if cou.faculty.Faculty_Id.user_id == user.user_id:
			cids.append(cou.course_id)
			crs.append(cou)

	kl = []
	for kx in j:
		# print kx
		if kx.Course_Id.course_id in cids:
			kl.append(kx)


	a = [k.serialize() for k in kl]
	# print a
	return HttpResponse(a)
	# print a

def getFacultyNotices(request):
	print "kbdkasbdfkb"
	j = Notice.objects.all()
	# print request.session['id']
	u = MyUser.objects.all()
	print u
	for user in u:
		if user.user_id == request.session['id']:
			break
	c = Course.objects.all()
	# print e
	cids = []
	crs = []
	print user
	for cou in c:
		print cou.faculty.Faculty_Id.user_id
		if cou.faculty.Faculty_Id.user_id == user.user_id:
			cids.append(cou.course_id)
			crs.append(cou)

	kl = []
	for kx in j:
		print kx
		if kx.c_id.course_id in cids:
			kl.append(kx)


	a = [k.serialize() for k in kl]
	print "bfdasvhsvhdf"
	print a
	return HttpResponse(a)


# API to get list of all courses of a faculty
def allfacultycourses(request):
	j = Course.objects.all()
	d = [i.serialize() for i in j if i.faculty_id == request.session['id']]
	return HttpResponse(d)

# API to get list of all courses of a faculty
def allstudentcourses(request):
	enrolled_courses = []
	print request.session['id']
	for c in Enrolls.objects.all():
		print c.student_id.Student_Id.user_id
		if c.student_id.Student_Id.user_id == request.session['id']:
			p = c.course_id.course_id
			enrolled_courses.append(p)
	print enrolled_courses
	d = [i.serialize() for i in Course.objects.all() if i.course_id in enrolled_courses]
	print d
	return HttpResponse(d)

# API to get all notices
def allnotices(request):
	for i in Notice.objects.all():
		print i.serialize()
	return JsonResponse([i.serialize() for i in Notice.objects.all()])


# API to get all notices of a course
def allcoursenotices(request):
	return jsonify(json_data = [i.serialize for i in Notice.objects.get(c_id = request.session['course_id']).all()])


# # API to get all notices of a student
# def allstudentnotices(request):
# 	enrolled_courses = []
# 	for c in Enrolls.objects.get(student_id = request.session['id']).all(request):
# 		p = c.course_id
# 		enrolled_courses.append(p)
#
# 	d = jsonify(json_data = [i.serialize for i in Notice.objects.all() if i.c_id in enrolled_courses])
# 	return d

# API to get all lectures for all courses
def alllectures(request):
	for i in Notice.objects.all():
		print i.serialize
	return jsonify(json_data = [i.serialize for i in Lecture.objects.all()])


# API to get all lectures of a course
def allcourselectures(request):
	return jsonify(json_data = [i.serialize for i in Lecture.objects.get(c_id = request.session['course_id']).all()])

# # API to get calendar
# def allstudentlectures(request):
# 	enrolled_courses = []
# 	for c in Enrolls.objects.get(student_id = request.session['id']).all(request):
# 		p = c.course_id
# 		enrolled_courses.append(p)
#
# 	d = jsonify(json_data = [i.serialize for i in Lecture.objects.all() if i.c_id in enrolled_courses])
# 	return d

# API for listing
def studentlistcourses(request):
	return render(request, 'gentelella/studentallcourses.html')

def facultylistcourses(request):
	return render(request, 'gentelella/facultyallcourses.html')

# API for listing
def listfacultycourses(request):
	return render(request, 'maggulater/faculty_course_list.html')

# API for listing
def liststudentcourses(request):
	return render(request, 'maggulater/student_course_list.html')


def faccalender(request):
	return render(request, 'gentelella/faccalender.html')

def studcalender(request):
	return render(request, 'gentelella/studcalender.html')

# API for adding a lecture
def addLecture(request):
	if request.method == 'POST' :
		json_data = request.body
		print json_data
		json_data = json.loads(json_data)
		# course_id = request.session['course_id']

		course_id = request.session['course_id']
		print json_data
		notes = json_data['Notes']
		Date_Time = json_data['Date_Time']
		print Date_Time
		date = datetime.strptime(Date_Time, '%Y-%m-%d').date()
		Topic = json_data['Topic']
		Link = json_data['Link']
		print "Here!!"
		course = Course.objects.get(course_id = course_id)
		NewLec = Lecture(Course_Id = course,Topic =  Topic)
		print "here"
		NewLec.setDate(date)
		NewLec.setNotes(notes)
		NewLec.setLink(Link)
		NewLec.save()
		Lecture_Id= NewLec.Lecture_Id
		Questions = json_data['Questions']
		Answers = json_data['Answers']
		NewTest = Test(Lecture_Id = NewLec)
		NewTest.setQuestions(Questions)
		NewTest.setAnswers(Answers)
		NewTest.save()
		response = {'status': 1, 'message': "Confirmed!!", 'url':'/coursehome/' + course_id}
		return HttpResponse(json.dumps(response), content_type='application/json')
	if request.method == 'GET' :
		return render(request, 'maggulater/addLecture.html')

def studentallperformance(request):
	return render(request, 'gentelella/studentallperformance.html')

def studentAllTestPerformance(request):
	sid = request.session['id']
	# try :
	# 	a = request.session['parentPortal']
	# 	del request.session['id']
	# except Exception, e:
	# 	pass
	print "ayayayaya"
	user = MyUser.objects.get(user_id = sid)
	print user
	student = Student.objects.get(Student_Id = user)
	print student
	PerformanceSheets = Performance_Sheet.objects.all()
	print PerformanceSheets[0].serialize()
	p = []
	for pr in PerformanceSheets:
		if pr.Student_Id.Student_Id.user_id == sid:
			p.append(pr)
	# print PerformanceSheets[0].Student_Id.Student_Id.name
	# print PerformanceSheets[0].serialize()
	print "yahan1"
	print p
	print "yaha2"
	perf = [q.serialize() for q in p]
	print perf
	return HttpResponse(perf)

def studentCoursePerformance(request):
	sid = request.session['id']
	user = MyUser.objects.get(user_id = sid)
	student = Student.objects.get(Student_Id = user)
	PerformanceSheets = Performance_Sheet.objects.get(Student_Id = student)
	course_id = request.session['course_id']
	perf = []
	for p in PerformanceSheets :
		test = Test.objects.get(Test_Id = p.Test_Id)
		lec = Lecture.objects.get(Lecture_Id = test.Lecture_Id)
		if lec.Course_Id == course_id :
			perf.append(p)
	a = [p.serialize() for p in perf]
	return HttpResponse(a)



def mailall(request):
	return render(request,'maggulater/email.html')
def CourseStudentsPerformance(request):
	fac_id = request.session['id']
	user = MyUser.objects.get(user_id = sid)
	student = Student.objects.get(Student_Id = user)
