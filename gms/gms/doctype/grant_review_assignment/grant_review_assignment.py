# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class GrantReviewAssignment(Document):
    # Get submitted grant Application
    def get_submitted_grant_applications(self):
        # Validations
        if not self.discipline:
            frappe.throw(_("Please select the Discipline"),
                         title=_("Discipline Required"))

        if not self.grant_call:
            frappe.throw(_("Please select the Grant Call"),
                         title=_("Grant Call Required"))

        if not self.from_date:
            frappe.throw(_("Please select the From Date Filter"),
                         title=_("From Date Required"))

        if not self.to_date:
            frappe.throw(_("Please select the To Date Filter"),
                         title=_("To Date Required"))
        # End Validations

        """ Pull submitted grant applications based on criteria selected"""
        grant_applications = get_grant_applications(self)

        if grant_applications:
            self.add_ga_in_table(grant_applications)
            frappe.msgprint(_("Grant Applications selection completed"), title=_(
                "Grant Application Selection"))
        else:
            frappe.msgprint(_("Grant Applications are not available for Grant Review Assignment"), title=_(
                "Grant Applications Missing"))

    # Add submitted grant applications in table
    def add_ga_in_table(self, grant_applications):
        """ Add grant applications in the table"""
        self.set('grant_applications', [])
        for data in grant_applications:
            self.append('grant_applications', {
                'grant_application': data.name,
                'applicant': data.applicant,
                'grant_call': data.grant_call,
                'type': data.type,
                'date': data.date
            })

    # Get discipline reviewers
    def get_current_discipline_reviewers(self):
        # Validations
        if not self.discipline:
            frappe.throw(_("Please select the Discipline"),
                         title=_("Discipline Required"))
        # End Validations

        """ Pull reviewers based on discipline selected"""
        discipline_reviewers = get_discipline_reviewers(self)

        if discipline_reviewers:
            self.add_reviewer_in_table(discipline_reviewers)
            frappe.msgprint(_("Discipline Reviewers selection completed"), title=_(
                "Reviewers Selection"))
        else:
            frappe.msgprint(_("Reviewers for the selected Discipline are not available for Grant Review Assignment"), title=_(
                "Discipline Reviewers Missing"))

    # Add discipline reviewers in table
    def add_reviewer_in_table(self, discipline_reviewers):
        """ Add reviwers in the table"""
        self.set('reviewers', [])
        for data in discipline_reviewers:
            self.append('reviewers', {
                'reviewer': data.name,
                'reviewer_name': data.member_name,
                'user': data.user
            })

        # Send Emails to Reviewers
    def send_emails_to_reviewers(self):

        # Get Grant Review Assignment Reviewers
        grant_review_assignment_reviewers = get_grant_review_assignment_reviewers(
            self)

        # Get Grant Review Assignment Applications
        grant_review_assignment_applications = get_grant_review_assignment_applications(
            self)

        for reviewer in grant_review_assignment_reviewers:
            for grant_application in grant_review_assignment_applications:
                # Get existing grant application review for reviewer
                existing_grant_application_review = get_existing_grant_application_review(
                    self, reviewer, grant_application)
                if not existing_grant_application_review:
                    # Create Grant Application Review
                    created_gar_doc = create_grant_application_review(
                        reviewer, grant_application)

    # TODO Create Grant Application Review User Permission
    # TODO Create Grant Application Review TODOs/Assignment
    # TODO Send Email for Grant Application Review

# Get grant applications


def get_grant_applications(self):
    gara_filter = ""
    if self.type:
        gara_filter += " and ga.type = %(type)s"
    if self.discipline:
        gara_filter += " and ga.discipline = %(discipline)s"
    if self.gender:
        gara_filter += " and ga.gender = %(gender)s"
    if self.programme:
        gara_filter += " and ga.programme = %(programme)s"
    if self.grant_call:
        gara_filter += " and ga.grant_call = %(grant_call)s"
    if self.from_date:
        gara_filter += " and ga.date >= %(from_date)s"
    if self.to_date:
        gara_filter += " and ga.date <= %(to_date)s"

    grant_applications = frappe.db.sql("""
		select distinct ga.name, ga.applicant, ga.grant_call, ga.type, ga.date
		from `tabGrant Application` ga
		where ga.docstatus = 1
		    and ga.company = %(company)s {0}
			and (ga.name not in (select graa.grant_application from `tabGrant Review Assignment Application` graa,
							`tabGrant Review Assignment` gra where graa.parent = gra.name and gra.docstatus != 2))
			
		order by ga.name
		""".format(gara_filter), {
        "type": self.type,
        "discipline": self.discipline,
        "gender": self.gender,
        "programme": self.programme,
        "grant_call": self.grant_call,
        "from_date": self.from_date,
        "to_date": self.to_date,
        "company": self.company

    }, as_dict=1)
    return grant_applications

# Get reviewers by discipline


def get_discipline_reviewers(self):
    gara_filter = ""
    if self.discipline:
        gara_filter += " and membership.discipline = %(discipline)s"

    discipline_reviewers = frappe.db.sql("""
		select distinct member.name, member.member_name, member.user
		from `tabMember` member, `tabMembership` membership
		where member.name = membership.member
			and membership.membership_status in ("New", "Current")
			and membership.company = %(company)s {0}
			and (member.name not in (select grar.reviewer from `tabGrant Review Assignment Reviewer` grar,
							`tabGrant Review Assignment` gra where grar.parent = gra.name and gra.docstatus != 2))
			
		order by member.name
		""".format(gara_filter), {
        "discipline": self.discipline,
        "company": self.company

    }, as_dict=1)
    return discipline_reviewers

# Get Grant Review Assignment Reviewers


def get_grant_review_assignment_reviewers(self):
    g_filter = ""
    if self.name:
        g_filter += " and gra.name = %(name)s"

    grant_review_assignment_reviewers = frappe.db.sql("""
		select distinct grar.reviewer, grar.reviewer_name, grar.user, grar.mobile_no, gra.name as grant_review_assignment, gra.company
		from `tabGrant Review Assignment` gra, `tabGrant Review Assignment Reviewer` grar
		where gra.name = grar.parent
		    and gra.docstatus = 1
		    and gra.company = %(company)s {0}
		order by grar.reviewer
        """.format(g_filter), {
        "name": self.name,
        "company": self.company

    }, as_dict=1)
    return grant_review_assignment_reviewers

# Get Grant Review Assignment Applications


def get_grant_review_assignment_applications(self):
    g_filter = ""
    if self.name:
        g_filter += " and gra.name = %(name)s"

    grant_review_assignment_applications = frappe.db.sql("""
		select distinct graa.grant_application, graa.applicant, graa.grant_call
		from `tabGrant Review Assignment` gra, `tabGrant Review Assignment Application` graa
		where gra.name = graa.parent
		    and gra.docstatus = 1
		    and gra.company = %(company)s {0}
		order by graa.grant_application
        """.format(g_filter), {
        "name": self.name,
        "company": self.company

    }, as_dict=1)
    return grant_review_assignment_applications

# Get existing grant application review for reviewer


def get_existing_grant_application_review(self, reviewer, grant_application):
    gar_filter = ""
    if reviewer:
        gar_filter += " and gar.reviewer = %(reviewer)s"
    if grant_application:
        gar_filter += " and gar.grant_application = %(grant_application)s"

        existing_grant_application_review = frappe.db.sql("""
		select distinct gar.name, gar.reviewer, gar.grant_application
		from `tabGrant Application Review` gar
		where gra.docstatus != 2
			and gra.company = %(company)s {0}
		order by gar.name
		""".format(gar_filter), {
            "reviewer": reviewer,
            "grant_application": grant_application,
            "company": self.company
        }, as_dict=1)

        return existing_grant_application_review

# Get Grant Review Assignment Application Parameters and Responses


def get_grant_application_parameters(grant_application):

    grant_application_parameters = frappe.db.sql("""
		select distinct gap.parameter, gap.response, gap.response_description
		from `tabGrant Application Parameter` gap
		where gap.parent = %(grant_application)s
		order by gar.name
		""", {"grant_application": grant_application}, as_dict=1)

    return grant_application_parameters

# Create Grant Application Review


def create_grant_application_review(reviewer, grant_application):
    try:
        gar_doc = frappe.get_doc({
            "reviewer": reviewer.reviewer,
            "reviewer_name": reviewer.reviewer_name,
            "user": reviewer.user,
            "mobile_no": reviewer.mobile_no,
            "grant_call": grant_application.grant_call,
            "grant_review_assignment": reviewer.grant_review_assignment,
            "grant_application": grant_application.grant_application,
            "applicant": grant_application.applicant,
            "company": reviewer.company
        })
        grant_application_parameters = get_grant_application_parameters(
            grant_application)
        add_items(gar_doc, grant_application_parameters)
        gar_doc.flags.ignore_permissions = True
        gar_doc.run_method("set_missing_values")
        gar_doc.save()
        frappe.msgprint(
            _("Grant Application Review {0} Created").format(gar_doc.name))
        return gar_doc.name
    except Exception:
        return None


def add_items(gar_doc, grant_application_parameters):
    for data in grant_application_parameters:
        create_gar_sheet(gar_doc, data)

# Create Grant Application Review Sheet


def create_gar_sheet(gar_doc, data):
    gar_doc.append('review_sheet', {
        "parameter": data.parameter,
        "response": data.response,
        "response_description": data.response_description
    })

# TODO Create Grant Application Review User Permission

# TODO Create Grant Application Review TODOs/Assignment

# TODO Send Email for Grant Application Review
