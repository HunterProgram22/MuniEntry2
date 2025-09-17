import aspose.words as aw
from pathlib import Path
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime
import os
import tempfile


class FineOnlyDocumentGenerator:
    """Generate Fine Only Plea Word documents using Aspose.Words"""

    def __init__(self):
        self.template_name = "Fine_Only_Plea_Template.docx"
        self.template_path = Path(settings.MEDIA_ROOT) / "templates" / self.template_name

    def generate_document(self, case_data):
        """Generate Fine Only Plea document from case data"""

        # Load template (we'll create a simple one for now)
        if not self.template_path.exists():
            self.create_sample_template()

        doc = aw.Document(str(self.template_path))

        # Prepare mail merge data
        field_names, field_values = self._prepare_merge_data(case_data)

        # Perform mail merge
        doc.mail_merge.execute(field_names, field_values)

        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        case_number = case_data.get('case_number', 'UNKNOWN').replace('/', '_')
        filename = f"{case_number}_Fine_Only_Plea_{timestamp}.docx"

        # Save to temporary file
        temp_dir = Path(settings.MEDIA_ROOT) / "generated"
        temp_dir.mkdir(exist_ok=True)
        output_path = temp_dir / filename

        doc.save(str(output_path))

        return output_path, filename

    def _prepare_merge_data(self, case_data):
        """Prepare data for mail merge"""

        # Basic case information
        field_names = [
            "case_number",
            "defendant_first_name",
            "defendant_last_name",
            "defendant_full_name",
            "judicial_officer",
            "plea_trial_date",
            "appearance_reason",
            "defense_counsel_name",
            "defense_counsel_type",
            "court_costs",
            "ability_to_pay",
            "total_fines",
            "total_suspended",
            "net_amount",
            "balance_due_date"
        ]

        field_values = [
            case_data.get('case_number', ''),
            case_data.get('defendant_first_name', ''),
            case_data.get('defendant_last_name', ''),
            case_data.get('defendant_full_name', ''),
            case_data.get('judicial_officer', ''),
            case_data.get('plea_trial_date', ''),
            case_data.get('appearance_reason', ''),
            case_data.get('defense_counsel_name', ''),
            case_data.get('defense_counsel_type', ''),
            case_data.get('court_costs', ''),
            case_data.get('ability_to_pay', ''),
            f"${case_data.get('total_fines', 0):.2f}",
            f"${case_data.get('total_suspended', 0):.2f}",
            f"${case_data.get('net_amount', 0):.2f}",
            case_data.get('balance_due_date', '')
        ]

        # Add charges information
        charges_list = case_data.get('charges_list', [])
        if charges_list:
            charges_text = ""
            for i, charge in enumerate(charges_list, 1):
                charges_text += f"{i}. {charge.get('offense', '')} "
                if charge.get('statute'):
                    charges_text += f"({charge.get('statute')}) "
                charges_text += f"- Plea: {charge.get('plea', '')}, "
                charges_text += f"Finding: {charge.get('finding', '')}, "
                charges_text += f"Fine: ${charge.get('fines', '0.00')}\n"

            field_names.append("charges_details")
            field_values.append(charges_text.strip())

        # Add conditions
        conditions = case_data.get('conditions', {})
        conditions_text = ""
        if conditions.get('license_suspension'):
            conditions_text += "License Suspension; "
        if conditions.get('community_service'):
            conditions_text += "Community Service; "
        if conditions.get('other_conditions'):
            conditions_text += "Other Conditions; "

        field_names.append("additional_conditions")
        field_values.append(conditions_text.rstrip('; '))

        return field_names, field_values

    def create_sample_template(self):
        """Create a sample template for testing"""

        # Ensure template directory exists
        template_dir = Path(settings.MEDIA_ROOT) / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)

        # Create a simple document
        doc = aw.Document()
        builder = aw.DocumentBuilder(doc)

        # Document header
        builder.font.bold = True
        builder.font.size = 16
        builder.paragraph_format.alignment = aw.ParagraphAlignment.CENTER
        builder.writeln("JUDGMENT ENTRY")
        builder.writeln("FINE ONLY PLEA")
        builder.writeln("")

        # Case information
        builder.font.bold = False
        builder.font.size = 12
        builder.paragraph_format.alignment = aw.ParagraphAlignment.LEFT

        # Insert merge fields using the correct syntax
        builder.write("Case Number: ")
        builder.insert_field("MERGEFIELD case_number", "")
        builder.writeln("")

        builder.write("State of Ohio v. ")
        builder.insert_field("MERGEFIELD defendant_full_name", "")
        builder.writeln("")
        builder.writeln("")

        builder.write("Date: ")
        builder.insert_field("MERGEFIELD plea_trial_date", "")
        builder.writeln("")

        builder.write("Judicial Officer: ")
        builder.insert_field("MERGEFIELD judicial_officer", "")
        builder.writeln("")
        builder.writeln("")

        builder.write("The defendant appeared for ")
        builder.insert_field("MERGEFIELD appearance_reason", "")
        builder.writeln(".")
        builder.writeln("")

        builder.write("Defense Counsel: ")
        builder.insert_field("MERGEFIELD defense_counsel_name", "")
        builder.write(" (")
        builder.insert_field("MERGEFIELD defense_counsel_type", "")
        builder.writeln(")")
        builder.writeln("")

        builder.writeln("CHARGES:")
        builder.insert_field("MERGEFIELD charges_details", "")
        builder.writeln("")
        builder.writeln("")

        builder.writeln("FINANCIAL OBLIGATIONS:")
        builder.write("Total Fines: ")
        builder.insert_field("MERGEFIELD total_fines", "")
        builder.writeln("")

        builder.write("Total Suspended: ")
        builder.insert_field("MERGEFIELD total_suspended", "")
        builder.writeln("")

        builder.write("Net Amount Due: ")
        builder.insert_field("MERGEFIELD net_amount", "")
        builder.writeln("")

        builder.write("Court Costs: ")
        builder.insert_field("MERGEFIELD court_costs", "")
        builder.writeln("")

        builder.write("Payment Terms: ")
        builder.insert_field("MERGEFIELD ability_to_pay", "")
        builder.writeln("")
        builder.writeln("")

        builder.writeln("ADDITIONAL CONDITIONS:")
        builder.insert_field("MERGEFIELD additional_conditions", "")
        builder.writeln("")
        builder.writeln("")
        builder.writeln("")

        builder.writeln("_________________________")
        builder.insert_field("MERGEFIELD judicial_officer", "")

        # Save template
        doc.save(str(self.template_path))
