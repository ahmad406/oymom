# Copyright (c) 2023, Oymom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Farmerregistration(Document):
	def on_submit(self):
		self.create_farmer()

	def create_farmer(self):
		farmer=frappe.new_doc("Patient")
		farmer.first_name=self.farmer_name
		farmer.last_name=self.fathers_name
		farmer.sex="Male"
		farmer.dob=self.date_of_birth
		farmer.mobile=self.mobile
		farmer.email=self.email
		farmer.invite_user=1
		farmer.save()
		self.db_set("farmer_id",farmer.name)

	def on_cancel(self):
		farmer=frappe.get_doc("Patient",self.farmer_id)
		user=frappe.get_doc("User",farmer.user_id)
		user.delete()
		farmer.delete()
		
