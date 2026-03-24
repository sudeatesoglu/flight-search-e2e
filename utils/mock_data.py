from dataclasses import dataclass

@dataclass
class MockPassenger:
    """Data class to hold mock passenger information for testing purposes."""
    email: str = "sude.test@gmail.com"
    phone: str = "5551234567"
    fname: str = "Sude"
    lname: str = "Atesoglu"
    id_number: str = "58880076462"
    b_day: str = "02"
    b_month: str = "02"
    b_year: str = "2000"
    gender: str = "Female"
    
@dataclass
class MockCreditCard:
    """Data class to hold mock credit card information for testing purposes."""
    cc_no: str = "4242424242424242"
    cc_month_idx: str = "0"
    cc_year_idx: str = "1"
    cc_cvv: str = "123"
