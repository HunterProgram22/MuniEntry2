from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Charge:
    """Individual charge information"""
    offense: str = ""
    statute: str = ""
    degree: str = ""
    plea: str = ""
    finding: str = ""
    fines: str = "0.00"
    fines_suspended: str = "0.00"
    dismissed: bool = False
    allied_offense: bool = False


@dataclass
class FineOnlyConditions:
    """Additional conditions for Fine Only entries"""
    license_suspension: bool = False
    license_type: str = ""
    community_service: bool = False
    hours_of_service: str = ""
    other_conditions: bool = False
    terms: str = ""


@dataclass
class FRAInfo:
    """Financial Responsibility Act information"""
    distracted_driving: bool = False
    fra_in_file: str = "N/A"
    fra_in_court: str = "N/A"


@dataclass
class FineOnlyEntryCaseInformation:
    """Complete case information for Fine Only Plea entries"""
    # Basic case info
    case_number: str = ""
    defendant_first_name: str = ""
    defendant_last_name: str = ""
    plea_trial_date: str = ""
    appearance_reason: str = "arraignment"
    judicial_officer: str = ""

    # Defense counsel
    defense_counsel_name: str = ""
    defense_counsel_type: str = "Public Defender"
    defense_counsel_waived: bool = False

    # Charges
    charges_list: List[Charge] = field(default_factory=list)

    # Financial information
    court_costs: str = "Yes"
    ability_to_pay: str = "forthwith"
    balance_due_date: str = ""
    pay_today: str = "0.00"
    monthly_pay: str = "0.00"
    credit_for_jail: bool = False
    jail_time_credit: str = "0"

    # Additional conditions
    conditions: FineOnlyConditions = field(default_factory=FineOnlyConditions)

    # FRA information
    fra_info: FRAInfo = field(default_factory=FRAInfo)

    def get_total_fines(self) -> float:
        """Calculate total fines across all charges"""
        total = 0.0
        for charge in self.charges_list:
            try:
                total += float(charge.fines or 0)
            except (ValueError, TypeError):
                pass
        return total

    def get_total_suspended(self) -> float:
        """Calculate total suspended fines"""
        total = 0.0
        for charge in self.charges_list:
            try:
                total += float(charge.fines_suspended or 0)
            except (ValueError, TypeError):
                pass
        return total

    def add_charge(self, charge: Charge):
        """Add a new charge to the case"""
        self.charges_list.append(charge)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            'case_number': self.case_number,
            'defendant_first_name': self.defendant_first_name,
            'defendant_last_name': self.defendant_last_name,
            'defendant_full_name': f"{self.defendant_first_name} {self.defendant_last_name}",
            'plea_trial_date': self.plea_trial_date,
            'appearance_reason': self.appearance_reason,
            'judicial_officer': self.judicial_officer,
            'defense_counsel_name': self.defense_counsel_name,
            'defense_counsel_type': self.defense_counsel_type,
            'defense_counsel_waived': self.defense_counsel_waived,
            'charges_list': self.charges_list,
            'court_costs': self.court_costs,
            'ability_to_pay': self.ability_to_pay,
            'balance_due_date': self.balance_due_date,
            'pay_today': self.pay_today,
            'monthly_pay': self.monthly_pay,
            'credit_for_jail': self.credit_for_jail,
            'jail_time_credit': self.jail_time_credit,
            'total_fines': self.get_total_fines(),
            'total_suspended': self.get_total_suspended(),
            'net_fines': self.get_total_fines() - self.get_total_suspended(),
            'conditions': self.conditions,
            'fra_info': self.fra_info,
        }
