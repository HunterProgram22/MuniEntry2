from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


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
                'name': 'Criminal/Traffic',
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
