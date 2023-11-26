import frappe
from frappe.core.doctype.user.user import *
from frappe import _, msgprint, throw

from datetime import date,datetime,timedelta
from frappe.utils.password import check_password, get_password_reset_limit
import os
from frappe.utils import cint, date_diff, datetime, get_datetime, today,getdate,add_days
from frappe.rate_limiter import rate_limit	
from frappe.auth import LoginManager
from frappe.exceptions import ValidationError	
import json


import os
from mimetypes import guess_type
from typing import TYPE_CHECKING


import frappe.sessions
import frappe.utils
from frappe import _, is_whitelisted
from frappe.utils import cint
from frappe.utils.image import optimize_image

if TYPE_CHECKING:
	from frappe.core.doctype.file.file import File
	from frappe.core.doctype.user.user import User

ALLOWED_MIMETYPES = (
	"application/pdf"
)


@frappe.whitelist(allow_guest=True)
def farmer_register():
	keys_to_check = [
    "farmer_name",
    "father_name",
    "mobile",
    "email",
    "panchayat",
    "block",
    "state",
    "are_you_a_dairy_farmer",
    "breed_of_cattle",
    "categary_of_breed",
    "vaccination",
    "daily_milk_production",
    "current_dairy_location",
    "how_many_cattle"
]
	missing_keys = [key for key in keys_to_check if frappe.form_dict.get(key) is None]

	if missing_keys:
		feilds=f"Feild {', '.join(missing_keys)} are mandatory."
		return  {
				"status": "fail",
				"message": feilds,
				}
	try:
		farmer_register=frappe.new_doc("Farmer registration")
		farmer_register.farmer_name=frappe.form_dict.get("farmer_name")
		farmer_register.fathers_name=frappe.form_dict.get("father_name")
		farmer_register.mobile=frappe.form_dict.get("mobile")
		farmer_register.email=frappe.form_dict.get("email")
		farmer_register.panchayat=frappe.form_dict.get("panchayat")
		farmer_register.block=frappe.form_dict.get("block")
		farmer_register.state=frappe.form_dict.get("state")
		farmer_register.are_you_a_dairy_farmer=frappe.form_dict.get("are_you_a_dairy_farmer")
		farmer_register.breed_of_cattle=frappe.form_dict.get("breed_of_cattle")
		farmer_register.categary_of_breed=frappe.form_dict.get("categary_of_breed")
		farmer_register.vaccination=frappe.form_dict.get("vaccination")
		farmer_register.daily_milk_production=frappe.form_dict.get("daily_milk_production")
		farmer_register.current_dairy_location=frappe.form_dict.get("current_dairy_location")
		farmer_register.how_many_cattle=frappe.form_dict.get("how_many_cattle")
		farmer_register.save(ignore_permissions = True)
		return  {
				"status": "success",
				"message": "Farmer register successfully",
				}
	except Exception as e:
		response = {
			"status": "failed",
			"message": str(e),
			"data": None
		}
		frappe.log_error(f"Error Creating Farmer: {str(e)}")

		return response
	


@frappe.whitelist(allow_guest=True)
def doctor_register():
	keys_to_check = ["doctor_name","father_name", "mobile", "email", "date_of_birth","address","course","any_experiance","prefferd_job_location","job_type"]
	missing_keys = [key for key in keys_to_check if frappe.form_dict.get(key) is None]

	if missing_keys:
		feilds=f"Feild {', '.join(missing_keys)} are mandatory."
		return  {
				"status": "fail",
				"message": feilds,
				}
	try:
		file_d=custom_upload_file_c()
		if not file_d.file_url:
			return  {
					"status": "fail",
					"message": "Registration of Certificate are mandatory",
					}
		try:
			doctor_register=frappe.new_doc("Doctor Registration")
			doctor_register.doctor_name=frappe.form_dict.get("doctor_name")
			doctor_register.father_name=frappe.form_dict.get("father_name")
			doctor_register.mobile=frappe.form_dict.get("mobile")
			doctor_register.email=frappe.form_dict.get("email")
			doctor_register.date_of_birth=frappe.form_dict.get("date_of_birth")
			doctor_register.address=frappe.form_dict.get("address")
			doctor_register.course=frappe.form_dict.get("course")
			doctor_register.any_experiance=frappe.form_dict.get("any_experiance")
			doctor_register.prefferd_job_location=frappe.form_dict.get("prefferd_job_location")
			doctor_register.job_type=frappe.form_dict.get("job_type")
			doctor_register.registration_of_certificate=file_d.file_url
			doctor_register.save(ignore_permissions = True)

			return  {
				"status": "success",
				"message": "Doctor Registration successfully",
				}

		except Exception as e:
			response = {
				"status": "failed",
				"message": str(e),
				"data": None
			}
			frappe.log_error(f"Error Creating Doctor: {str(e)}")
			return response

	except Exception as e:
		frappe.db.rollback()
		response = {
			"status": "failed",
				"message": str(e),
				"data": None
			}
		return response
	



@frappe.whitelist(allow_guest=True)
def custom_upload_file(files=None,file_url=None,filename=None):
	user = "Guest"
	ignore_permissions = True
	is_private = 0
	doctype = "Doctor Registration"
	docname = "as@gm.com"
	fieldname = "registration_of_certificate"
	file_url = frappe.form_dict.file_url
	folder = "Home"
	filename = frappe.form_dict.file_name
	optimize = None
	content = None

	if frappe.form_dict.get("library_file_name", False):
		doc = frappe.get_value(
			"File",
			frappe.form_dict.library_file_name,
			["is_private", "file_url", "file_name"],
			as_dict=True,
		)
		is_private = doc.is_private
		file_url = doc.file_url
		filename = doc.file_name

	

	if "file" in files:
		file = files["file"]
		content = file.stream.read()
		filename = file.filename

		content_type = guess_type(filename)[0]
		if optimize and content_type and content_type.startswith("image/"):
			args = {"content": content, "content_type": content_type}
			if frappe.form_dict.max_width:
				args["max_width"] = int(frappe.form_dict.max_width)
			if frappe.form_dict.max_height:
				args["max_height"] = int(frappe.form_dict.max_height)
			content = optimize_image(**args)

	frappe.local.uploaded_file = content
	frappe.local.uploaded_filename = filename

	if content is not None and (
		frappe.session.user == "Guest" or (user and not user.has_desk_access())
	):
		filetype = guess_type(filename)[0]
		if filetype not in ALLOWED_MIMETYPES:
			frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

	
	return frappe.get_doc(
		{
			"doctype": "File",
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": fieldname,
			"folder": folder,
			"file_name": filename,
			"file_url": file_url,
			"is_private": cint(is_private),
			"content": content,
		}
	).save(ignore_permissions=ignore_permissions)


@frappe.whitelist(allow_guest=True)
def custom_upload_file_c():
		user = None
		files = frappe.request.files
		frappe.log_error("fl in files: " + str(files))
		frappe.log_error("to in files: " + str(type(files)))
		is_private = frappe.form_dict.is_private
		doctype = frappe.form_dict.doctype
		docname = frappe.form_dict.docname
		fieldname = frappe.form_dict.fieldname
		file_url = frappe.form_dict.file_url
		folder = frappe.form_dict.folder or "Home"
		method = frappe.form_dict.method
		filename = frappe.form_dict.file_name
		optimize = frappe.form_dict.optimize
		content = None

		if frappe.form_dict.get("library_file_name", False):
			doc = frappe.get_value(
				"File",
				frappe.form_dict.library_file_name,
				["is_private", "file_url", "file_name"],
				as_dict=True,
			)
			is_private = doc.is_private
			file_url = doc.file_url
			filename = doc.file_name



		if "file" in files:
			file = files["file"]
			content = file.stream.read()
			filename = file.filename

			content_type = guess_type(filename)[0]
			if optimize and content_type and content_type.startswith("image/"):
				args = {"content": content, "content_type": content_type}
				if frappe.form_dict.max_width:
					args["max_width"] = int(frappe.form_dict.max_width)
				if frappe.form_dict.max_height:
					args["max_height"] = int(frappe.form_dict.max_height)
				content = optimize_image(**args)

		frappe.local.uploaded_file = content
		frappe.local.uploaded_filename = filename

		if content is not None and (
			frappe.session.user == "Guest" or (user and not user.has_desk_access())
		):
			filetype = guess_type(filename)[0]
			if filetype not in ALLOWED_MIMETYPES:
				frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

		if method:
			method = frappe.get_attr(method)
			is_whitelisted(method)
			return method()
		else:
			frappe.log_error("file_url: " + str(file_url))
			return frappe.get_doc(
				{
					"doctype": "File",
					"attached_to_doctype": doctype,
					"attached_to_name": docname,
					"attached_to_field": fieldname,
					"folder": folder,
					"file_name": filename,
					"file_url": file_url,
					"is_private": cint(is_private),
					"content": content,
				}
			).save(ignore_permissions=True)
