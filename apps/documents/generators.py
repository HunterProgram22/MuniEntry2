from docxtpl import DocxTemplate
from pathlib import Path
from django.conf import settings
from datetime import datetime
import os


class FineOnlyDocumentGenerator:
    """Generate Fine Only Plea Word documents using python-docx-template"""

    def __init__(self):
        self.template_name = "Fine_Only_Plea_Final_Judgment_Template.docx"
        self.template_path = Path(settings.MEDIA_ROOT) / "templates" / self.template_name

    def generate_document(self, case_data):
        """Generate Fine Only Plea document from case data"""

        # Check if template exists
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        # Load template
        doc = DocxTemplate(str(self.template_path))

        # Transform case data to match template variables
        template_data = self._prepare_template_data(case_data)

        # Render template with data
        doc.render(template_data)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_number = case_data.get('case_number', 'UNKNOWN').replace('/', '_')
        filename = f"{case_number}_Fine_Only_Plea_{timestamp}.docx"

        # Save to generated folder
        temp_dir = Path(settings.MEDIA_ROOT) / "generated"
        temp_dir.mkdir(exist_ok=True)
        output_path = temp_dir / filename

        doc.save(str(output_path))

        return output_path, filename

    def _prepare_template_data(self, case_data):
        """Transform Django form data to match Jinja2 template variables"""

        # Create defendant object structure that template expects
        defendant = {
            'first_name': case_data.get('defendant_first_name', ''),
            'last_name': case_data.get('defendant_last_name', ''),
        }

        # Create judicial officer object (simplified for now)
        judicial_officer = {
            'first_name': case_data.get('judicial_officer', '').split(' ')[-1] if case_data.get(
                'judicial_officer') else '',
            'last_name': '',
            'officer_type': 'Judge' if 'Judge' in case_data.get('judicial_officer',
                                                                '') else 'Magistrate'
        }

        # Transform charges list to match template structure
        charges_list = []
        for charge_dict in case_data.get('charges_list', []):
            charges_list.append({
                'offense': charge_dict.get('offense', ''),
                'statute': charge_dict.get('statute', ''),
                'degree': charge_dict.get('degree', ''),
                'plea': charge_dict.get('plea', ''),
                'finding': charge_dict.get('finding', ''),
                'fines_amount': charge_dict.get('fines', '0.00'),
                'fines_suspended': charge_dict.get('fines_suspended', '0.00'),
            })

        # Create court costs structure
        court_costs = {
            'ordered': case_data.get('court_costs', 'Yes'),
            'ability_to_pay_time': case_data.get('ability_to_pay', 'forthwith'),
            'monthly_pay_amount': case_data.get('monthly_pay', '0.00'),
            'pay_today_amount': case_data.get('pay_today', '0.00'),
            'balance_due_date': case_data.get('balance_due_date', ''),
        }

        # Extract conditions
        conditions = case_data.get('conditions', {})
        license_suspension = {
            'ordered': conditions.get('license_suspension', False),
            'license_type': 'operator\'s',  # default value
            'suspended_date': case_data.get('plea_trial_date', ''),
            'suspension_term': '6 months',  # default value
        }

        community_service = {
            'ordered': conditions.get('community_service', False),
            'hours_of_service': '40',  # default value
            'days_to_complete_service': '180',  # default value
            'due_date_for_service': '',  # will need to calculate
        }

        other_conditions = {
            'ordered': conditions.get('other_conditions', False),
            'terms': conditions.get('terms', ''),
        }

        # Extract FRA info
        fra_info = case_data.get('fra_info', {})

        # Build the complete template data structure
        template_data = {
            'case_number': case_data.get('case_number', ''),
            'defendant': defendant,
            'judicial_officer': judicial_officer,
            'appearance_reason': case_data.get('appearance_reason', 'arraignment'),
            'plea_trial_date': case_data.get('plea_trial_date', ''),
            'defense_counsel_waived': case_data.get('defense_counsel_waived', False),
            'defense_counsel': case_data.get('defense_counsel_name', ''),
            'defense_counsel_type': case_data.get('defense_counsel_type', ''),

            # Charges
            'charges_list': charges_list,
            'amended_charges_list': [],  # empty for now
            'amend_offense_details': None,  # not implemented yet

            # Court costs and fines
            'court_costs': court_costs,
            'fines_and_costs_jail_credit': case_data.get('credit_for_jail', False),
            'fine_jail_days': case_data.get('jail_time_credit', '0'),

            # Conditions
            'license_suspension': license_suspension,
            'community_service': community_service,
            'other_conditions': other_conditions,

            # FRA information
            'fra_in_file': fra_info.get('fra_in_file') == 'Yes' if fra_info.get(
                'fra_in_file') != 'N/A' else None,
            'fra_in_court': fra_info.get('fra_in_court') == 'Yes' if fra_info.get(
                'fra_in_court') != 'N/A' else None,
            'distracted_driving': fra_info.get('distracted_driving', False),

            # Additional fields that might be in template
            'victim_statements': False,  # default value
        }

        return template_data
