import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.cases.models import FineOnlyEntryCaseInformation, Charge, FineOnlyConditions, FRAInfo


def select_user(request):
    """User selection page - replaces your radio button user selection"""
    users = [
        {'name': 'Judge Fowler', 'role': 'Judge'},
        {'name': 'Judge Rohrer', 'role': 'Judge'},
        {'name': 'Magistrate Bunner', 'role': 'Magistrate'},
        {'name': 'Magistrate Pelanda', 'role': 'Magistrate'},
        {'name': 'Magistrate Kudela', 'role': 'Magistrate'},
        # Add other court staff as needed
    ]

    if request.method == 'POST':
        selected_user = request.POST.get('selected_user')
        request.session['selected_user'] = selected_user
        return redirect('dashboard')

    return render(request, 'core/select_user.html', {'users': users})


def dashboard(request):
    """Main dashboard - replaces your main window"""
    # Check if user is selected
    if not request.session.get('selected_user'):
        return redirect('select_user')

    context = {
        'selected_user': request.session.get('selected_user'),
        'entry_categories': [
            {
                'name': 'Criminal-Traffic',
                'color': 'success',
                'entries': [
                    'Fine Only Plea',
                    'Jail and/or Community Control',
                    'Not Guilty Plea / Bond',
                    'Plea Only - Future Sentencing',
                    'Sentencing Only - Already Plead',
                    'Diversion',
                    'LEAP Admission Plea',
                    'Bond Modification / Revocation',
                    'Failed to Appear / Issue Warrant',
                ]
            },
            {
                'name': 'Scheduling',
                'color': 'primary',
                'entries': [
                    'General Notice of Hearing',
                    'Final/Jury Notice of Hearing',
                    'Trial To Court Notice of Hearing',
                ]
            },
            {
                'name': 'Administrative',
                'color': 'info',
                'entries': [
                    'Grant Limited Driving Privileges',
                    'Deny Driving Privileges',
                    'Fiscal Journal Entries',
                    'Juror Payment Entry',
                    'Time to Pay Order',
                ]
            },
            {
                'name': 'Civil',
                'color': 'warning',
                'entries': ['Freeform Entry']
            },
            {
                'name': 'Probation',
                'color': 'secondary',
                'entries': [
                    'Terms of Community Control',
                    'Notice of Community Control Violation',
                ]
            }
        ]
    }

    return render(request, 'core/dashboard.html', context)


def create_entry(request, category, entry_type):
    """Handle entry creation forms"""
    # Check if user is selected
    if not request.session.get('selected_user'):
        return redirect('select_user')

    context = {
        'selected_user': request.session.get('selected_user'),
        'category': category,
        'entry_type': entry_type,
    }

    if entry_type == 'Fine Only Plea' and category == 'Criminal-Traffic':  # Updated condition
        return handle_fine_only_plea(request, context)
    else:
        # Placeholder for other entry types
        context['message'] = f'{entry_type} entry form not yet implemented'
        return render(request, 'core/entry_placeholder.html', context)


def handle_fine_only_plea(request, context):
    """Handle Fine Only Plea entry form with complex charge grid"""

    if request.method == 'POST':
        # Create case information object
        case_info = FineOnlyEntryCaseInformation()

        # Basic information
        case_info.case_number = request.POST.get('case_number', '')
        case_info.defendant_first_name = request.POST.get('defendant_first_name', '')
        case_info.defendant_last_name = request.POST.get('defendant_last_name', '')
        case_info.plea_trial_date = request.POST.get('plea_trial_date', '')
        case_info.appearance_reason = request.POST.get('appearance_reason', 'arraignment')
        case_info.judicial_officer = context['selected_user']

        # Defense counsel
        case_info.defense_counsel_name = request.POST.get('defense_counsel_name', '')
        case_info.defense_counsel_type = request.POST.get('defense_counsel_type', 'Public Defender')
        case_info.defense_counsel_waived = bool(request.POST.get('defense_counsel_waived'))

        # Financial information
        case_info.court_costs = request.POST.get('court_costs', 'Yes')
        case_info.ability_to_pay = request.POST.get('ability_to_pay', 'forthwith')
        case_info.balance_due_date = request.POST.get('balance_due_date', '')
        case_info.pay_today = request.POST.get('pay_today', '0.00')
        case_info.monthly_pay = request.POST.get('monthly_pay', '0.00')
        case_info.credit_for_jail = bool(request.POST.get('credit_for_jail'))
        case_info.jail_time_credit = request.POST.get('jail_time_credit', '0')

        # Process charges from the charge grid
        charge_count = int(request.POST.get('charge_count', '1'))
        for i in range(charge_count):
            charge = Charge(
                offense=request.POST.get(f'offense_{i}', ''),
                statute=request.POST.get(f'statute_{i}', ''),
                degree=request.POST.get(f'degree_{i}', ''),
                plea=request.POST.get(f'plea_{i}', ''),
                finding=request.POST.get(f'finding_{i}', ''),
                fines=request.POST.get(f'fines_{i}', '0.00'),
                fines_suspended=request.POST.get(f'fines_suspended_{i}', '0.00'),
                dismissed=bool(request.POST.get(f'dismissed_{i}')),
                allied_offense=bool(request.POST.get(f'allied_{i}'))
            )
            case_info.add_charge(charge)

        # Additional conditions
        case_info.conditions.license_suspension = bool(request.POST.get('license_suspension'))
        case_info.conditions.community_service = bool(request.POST.get('community_service'))
        case_info.conditions.other_conditions = bool(request.POST.get('other_conditions'))

        # FRA information
        case_info.fra_info.distracted_driving = bool(request.POST.get('distracted_driving'))
        case_info.fra_info.fra_in_file = request.POST.get('fra_in_file', 'N/A')
        case_info.fra_info.fra_in_court = request.POST.get('fra_in_court', 'N/A')

        # Store in session for document generation
        request.session['fine_only_case_data'] = case_info.to_dict()

        context[
            'success_message'] = f"Fine Only Plea entry created for case {case_info.case_number}"
        context['case_data'] = case_info.to_dict()

        return render(request, 'entries/fine_only_success.html', context)

    # GET request - show the form
    # Initialize with one empty charge
    initial_charges = [Charge()]
    context['initial_charges'] = initial_charges

    return render(request, 'entries/fine_only_form_complex.html', context)


@csrf_exempt
def add_charge_ajax(request):
    """AJAX endpoint to add new charge row"""
    if request.method == 'POST':
        charge_index = int(request.POST.get('charge_index', 0))
        # Return HTML for new charge row
        return JsonResponse({
            'html': f'''
                <tr id="charge-row-{charge_index}">
                    <td><input type="text" name="offense_{charge_index}" class="form-control form-control-sm" placeholder="Enter offense"></td>
                    <td><input type="text" name="statute_{charge_index}" class="form-control form-control-sm" placeholder="e.g., 4511.19"></td>
                    <td>
                        <select name="degree_{charge_index}" class="form-select form-select-sm">
                            <option value="">Select degree</option>
                            <option value="M1">M1</option>
                            <option value="M2">M2</option>
                            <option value="M3">M3</option>
                            <option value="M4">M4</option>
                            <option value="MM">MM</option>
                        </select>
                    </td>
                    <td><input type="checkbox" name="dismissed_{charge_index}" class="form-check-input"></td>
                    <td><input type="checkbox" name="allied_{charge_index}" class="form-check-input"></td>
                    <td>
                        <select name="plea_{charge_index}" class="form-select form-select-sm">
                            <option value="">Select plea</option>
                            <option value="Guilty">Guilty</option>
                            <option value="No Contest">No Contest</option>
                            <option value="Not Guilty">Not Guilty</option>
                        </select>
                    </td>
                    <td>
                        <select name="finding_{charge_index}" class="form-select form-select-sm">
                            <option value="">Select finding</option>
                            <option value="Guilty">Guilty</option>
                            <option value="Not Guilty">Not Guilty</option>
                        </select>
                    </td>
                    <td><input type="number" step="0.01" name="fines_{charge_index}" class="form-control form-control-sm fine-input" placeholder="0.00"></td>
                    <td><input type="number" step="0.01" name="fines_suspended_{charge_index}" class="form-control form-control-sm suspended-input" placeholder="0.00"></td>
                    <td><button type="button" class="btn btn-sm btn-danger" onclick="removeCharge({charge_index})">Remove</button></td>
                </tr>
            ''',
            'charge_index': charge_index
        })
    return JsonResponse({'error': 'Invalid request'})
